from flask import Blueprint, current_app, request
from flask_jwt_extended import get_jwt_identity
from marshmallow import ValidationError
from sqlalchemy.exc import SQLAlchemyError

from core import db
from core.blueprints.errors.handlers import bad_request, handle_exception, not_found
from core.blueprints.utils import (
    required_user_type,
    send_order_cancellation_email,
    success_response,
)
from core.models import Customer, Listing, Order, OrderEntry, OrderStatus, Product
from core.validators.seller.seller_orders import (
    OrderFilterSchema,
    UpdateOrderStatusSchema,
)

seller_orders_bp = Blueprint("seller_orders", __name__)

validate_order_filters = OrderFilterSchema()
validate_update_status = UpdateOrderStatusSchema()


@seller_orders_bp.route("/seller/orders", methods=["GET"])
@required_user_type(["seller"])
def get_orders():
    """
    Retrieve orders for the authenticated seller with optional filtering and pagination.

    Returns:
        JSON response containing the filtered and paginated orders.
    """
    seller_id = get_jwt_identity()

    try:
        filters = validate_order_filters.load(request.get_json())
    except ValidationError as err:
        return bad_request(error=err.messages)

    try:
        query = (
            db.session.query(Order, OrderEntry, Listing)
            .join(OrderEntry, Order.id == OrderEntry.order_id)
            .join(Listing, OrderEntry.listing_id == Listing.id)
            .filter(Listing.seller_id == seller_id)
        )

        if filters.get("status"):
            try:
                status_lower = filters["status"].lower()
                status_enum = OrderStatus(status_lower)
                query = query.filter(Order.order_status == status_enum)
            except ValueError:
                return bad_request(error=f"Invalid status value: {filters['status']}")

        total_items = query.count()

        order_column = getattr(Order, filters["order_by"])
        if filters["order_direction"] == "desc":
            order_column = order_column.desc()
        else:
            order_column = order_column.asc()

        orders = (
            query.order_by(order_column)
            .offset(filters["offset"])
            .limit(filters["limit"])
            .all()
        )

        order_data = [
            {
                "order_id": order.id,
                "status": order.order_status.value,
                "purchased_at": order.purchased_at.isoformat(),
                "total_amount": float(order.price),
                "product_name": entry.listing.product.name,
                "quantity": entry.quantity,
                "price_per_unit": float(entry.listing.price),
            }
            for order, entry, listing in orders
        ]

        return success_response(
            data={
                "orders": order_data,
                "pagination": {
                    "offset": filters["offset"],
                    "limit": filters["limit"],
                    "total_items": total_items,
                },
            },
            status_code=200,
        )

    except SQLAlchemyError as sql_err:
        db.session.rollback()
        return handle_exception(error=str(sql_err))
    except Exception as e:
        return handle_exception(error=str(e))


@seller_orders_bp.route("/seller/orders/<string:order_ulid>", methods=["GET"])
@required_user_type(["seller"])
def get_order(order_ulid):
    """
    Retrieve details of a specific order for the authenticated seller.

    Args:
        order_ulid (str): The unique identifier of the order.

    Returns:
        JSON response containing the details of the specified order.
    """
    seller_id = get_jwt_identity()

    try:
        order_details = (
            db.session.query(Order, OrderEntry, Listing, Product, Customer)
            .join(OrderEntry, Order.id == OrderEntry.order_id)
            .join(Listing, OrderEntry.listing_id == Listing.id)
            .join(Product, Listing.product_id == Product.id)
            .join(Customer, Order.customer_id == Customer.id)
            .filter(Order.id == order_ulid, Listing.seller_id == seller_id)
            .first()
        )

        if not order_details:
            return not_found(error="Order not found or does not belong to this seller")

        order, order_entry, listing, product, customer = order_details

        order_data = {
            "order_id": order.id,
            "status": order.order_status.value,
            "purchased_at": order.purchased_at.isoformat(),
            "total_amount": float(order.price),
            "customer_info": {
                "name": f"{customer.name} {customer.surname}",
                "email": customer.email,
            },
            "shipping_address": {
                "street": order.address_street,
                "city": order.address_city,
                "state": order.address_state,
                "country": order.address_country,
                "postal_code": order.address_postal_code,
            },
            "product_details": {
                "product_id": product.id,
                "product_name": product.name,
                "quantity": order_entry.quantity,
                "price_per_unit": float(listing.price),
                "total_price": float(listing.price * order_entry.quantity),
            },
        }

        return success_response(data=order_data, status_code=200)

    except SQLAlchemyError as sql_err:
        db.session.rollback()
        return handle_exception(error=str(sql_err))
    except Exception as e:
        return handle_exception(error=str(e))


@seller_orders_bp.route("/seller/orders/<string:order_ulid>", methods=["POST"])
@required_user_type(["seller"])
def update_order_status(order_ulid):
    """
    Update the status of a specific order for the authenticated seller.

    Args:
        order_ulid (str): The unique identifier of the order.

    Returns:
        JSON response indicating the success of the status update.
    """
    seller_id = get_jwt_identity()
    config_name = current_app.config["NAME"]

    try:
        validated_data = validate_update_status.load(request.get_json())
    except ValidationError as err:
        return bad_request(error=err.messages)

    try:
        new_status_str = validated_data.get("status").lower()
        try:
            new_status = OrderStatus(new_status_str)
        except ValueError:
            return bad_request(error=f"Invalid status value: {new_status_str}")

        order = (
            db.session.query(Order)
            .join(OrderEntry, Order.id == OrderEntry.order_id)
            .join(Listing, OrderEntry.listing_id == Listing.id)
            .filter(Order.id == order_ulid, Listing.seller_id == seller_id)
            .first()
        )

        if not order:
            return not_found(error="Order not found or does not belong to this seller")

        if order.order_status == OrderStatus.CANCELLED:
            return bad_request(error="Cannot update status of a cancelled order")

        if new_status == OrderStatus.CANCELLED:
            if order.order_status != OrderStatus.PENDING:
                return bad_request(error="Only pending orders can be cancelled")

            # Restore inventory for cancelled orders
            for entry in order.order_entries:
                listing = entry.listing
                listing.quantity += entry.quantity
                listing.purchase_count -= entry.quantity

            if config_name != "development":
                send_order_cancellation_email(order.customer_id, order.id)
        else:
            valid_transitions = {
                OrderStatus.PENDING: [OrderStatus.SHIPPED],
                OrderStatus.SHIPPED: [OrderStatus.DELIVERED],
                OrderStatus.DELIVERED: [],  # Final state, no further transitions
            }

            if new_status not in valid_transitions[order.order_status]:
                return bad_request(
                    error=f"Invalid status transition from {order.order_status.value} to {new_status.value}"
                )

        order.order_status = new_status
        db.session.commit()

        return success_response(
            data={"order_id": order.id, "new_status": new_status.value},
            message="Order status updated successfully",
            status_code=200,
        )

    except SQLAlchemyError as sql_err:
        db.session.rollback()
        return handle_exception(error=str(sql_err))
    except Exception as e:
        db.session.rollback()
        return handle_exception(error=str(e))


# This module defines the routes for handling seller order operations.

# Key features:
# - Retrieve orders for a seller with filtering and pagination
# - Get details of a specific order
# - Update the status of an order

# Security considerations:
# - All routes are protected by the @required_user_type decorator, ensuring only sellers can access them
# - The seller ID is obtained from the JWT token, preventing unauthorized access to other sellers' orders

# Note: This module uses SQLAlchemy for database operations and Marshmallow for request validation.

# Error handling:
# - ValidationErrors are caught and returned as bad requests
# - SQLAlchemyErrors trigger a database rollback and are handled as exceptions
# - General exceptions are also caught and handled appropriately

# Future improvements could include:
# - Implementing more advanced filtering options for orders
# - Adding support for bulk order status updates
# - Implementing a notification system for status changes (e.g., email notifications to customers)
