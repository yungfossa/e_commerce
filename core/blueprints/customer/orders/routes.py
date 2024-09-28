from datetime import UTC, datetime

from flask import Blueprint, current_app, request
from flask_jwt_extended import get_jwt_identity
from marshmallow import ValidationError
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import joinedload

from core import db
from core.blueprints.errors.handlers import bad_request, handle_exception
from core.blueprints.utils import (
    required_user_type,
    send_order_cancellation_email,
    send_order_confirmation_email,
    success_response,
)
from core.models import (
    Cart,
    CartEntry,
    CustomerAddress,
    Listing,
    Order,
    OrderEntry,
    OrderStatus,
)
from core.validators.customer.customer_orders import (
    OrderCreationSchema,
    OrderSummaryFilterSchema,
)

customer_orders_bp = Blueprint("customer_orders", __name__)

validate_order_creation = OrderCreationSchema()
validate_order_summary_filters = OrderSummaryFilterSchema()


@customer_orders_bp.route("/orders", methods=["POST"])
@required_user_type(["customer"])
def create_order():
    """
    Create a new order for the authenticated customer.

    This function processes the customer's cart, creates a new order, updates inventory,
    and sends a confirmation email (except in development environment).

    Returns:
        A JSON response with the new order ID or an error message.
    """
    config_name = current_app.config["NAME"]
    customer_id = get_jwt_identity()

    try:
        data = validate_order_creation.load(data=request.get_json())
    except ValidationError as ve:
        return bad_request(error=ve.messages)

    try:
        # Fetch the cart and its entry
        cart_with_entry = (
            db.session.query(Cart)
            .options(joinedload(Cart.cart_entry).joinedload(CartEntry.listing))
            .filter(Cart.customer_id == customer_id)
            .first()
        )

        if not cart_with_entry or not cart_with_entry.cart_entry:
            return bad_request(error="The cart is empty")

        # Calculate total order price
        total_order_price = (
            cart_with_entry.cart_entry.quantity
            * cart_with_entry.cart_entry.listing.price
        )

        # Check if there's enough quantity available
        if (
            cart_with_entry.cart_entry.quantity
            > cart_with_entry.cart_entry.listing.quantity
        ):
            return bad_request(error="Not enough quantity available for this listing")

        # Create new order
        new_order = Order.create(
            customer_id=customer_id,
            price=total_order_price,
            order_status=OrderStatus.PENDING,
            purchased_at=datetime.now(UTC),
            address_street=data.get("address_street"),
            address_city=data.get("address_city"),
            address_state=data.get("address_state"),
            address_country=data.get("address_country"),
            address_postal_code=data.get("address_postal_code"),
        )

        # Create OrderEntry for the cart entry
        _oe = OrderEntry.create(
            order_id=new_order.id,
            listing_id=cart_with_entry.cart_entry.listing_id,
            quantity=cart_with_entry.cart_entry.quantity,
        )

        # Update the listing quantity
        listing = cart_with_entry.cart_entry.listing
        listing.quantity -= cart_with_entry.cart_entry.quantity
        listing.purchase_count += cart_with_entry.cart_entry.quantity
        listing.update()

        # Delete the cart entry
        db.session.delete(cart_with_entry.cart_entry)

        # Add the current CustomerAddress in the db
        CustomerAddress.create(
            customer_id=customer_id,
            street=data.get("address_street"),
            city=data.get("address_city"),
            state=data.get("address_state"),
            country=data.get("address_country"),
            postal_code=data.get("address_postal_code"),
        )

        if config_name != "development":
            send_order_confirmation_email(customer_id, new_order.id)

        db.session.commit()
        return success_response(data={"id": new_order.id}, status_code=201)
    except SQLAlchemyError as sql_err:
        db.session.rollback()
        return handle_exception(error=str(sql_err))
    except Exception as e:
        db.session.rollback()
        return handle_exception(error=str(e))


@customer_orders_bp.route("/orders/<order_ulid>", methods=["GET"])
@required_user_type(["customer"])
def get_order_details(order_ulid):
    """
    Retrieve details of a specific order for the authenticated customer.

    Args:
        order_ulid (str): The ULID of the order to retrieve.

    Returns:
        A JSON response with the order details or an error message.
    """
    customer_id = get_jwt_identity()

    try:
        order = Order.query.filter_by(id=order_ulid, customer_id=customer_id).first()

        if not order:
            return bad_request(error="Order not found")

        order_data = {
            "id": order.id,
            "status": order.order_status.value,
            "total_amount": float(order.price),
            "created_at": order.purchased_at.isoformat(),
            "address": {
                "street": order.address_street,
                "city": order.address_city,
                "state": order.address_state,
                "country": order.address_country,
                "postal_code": order.address_postal_code,
            },
            "entries": [
                {
                    "product_name": entry.listing.product.name,
                    "image_src": entry.listing.product.image_src,
                    "quantity": entry.quantity,
                    "price": entry.listing.price,
                }
                for entry in order.order_entries
            ],
        }
        return success_response(
            data=order_data,
            status_code=200,
        )
    except SQLAlchemyError as sql_err:
        db.session.rollback()
        return handle_exception(
            error=str(sql_err),
        )
    except Exception as e:
        return handle_exception(
            error=str(e),
        )


@customer_orders_bp.route("/orders/summary", methods=["GET"])
@required_user_type(["customer"])
def get_orders_summary():
    """
    Retrieve a summary of orders for the authenticated customer.

    This function supports filtering, sorting, and pagination of orders.

    Returns:
        A JSON response with the list of orders and pagination information.
    """
    customer_id = get_jwt_identity()

    try:
        filters = validate_order_summary_filters.load(request.args)
    except ValidationError as err:
        return bad_request(error=err.messages)

    try:
        query = Order.query.filter_by(customer_id=customer_id).options(
            joinedload(Order.order_entries)
            .joinedload(OrderEntry.listing)
            .joinedload(Listing.product)
        )

        if filters.get("status"):
            query = query.filter(
                Order.order_status == OrderStatus(filters["status"].lower())
            )

        order_column = getattr(Order, filters["order_by"])
        if filters["order_direction"] == "desc":
            query = query.order_by(order_column.desc())
        else:
            query = query.order_by(order_column.asc())

        total_items = query.count()
        orders = query.offset(filters["offset"]).limit(filters["limit"]).all()

        orders_data = [
            {
                "id": order.id,
                "status": order.order_status.value,
                "total_amount": float(order.price),
                "created_at": order.purchased_at.isoformat(),
                "entries": [
                    {
                        "product_name": entry.listing.product.name,
                        "quantity": entry.quantity,
                        "price": float(entry.listing.price),
                    }
                    for entry in order.order_entries
                ],
            }
            for order in orders
        ]

        return success_response(
            data={
                "orders": orders_data,
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
        return handle_exception(
            error=str(sql_err),
        )
    except Exception as e:
        return handle_exception(
            error=str(e),
        )


@customer_orders_bp.route("/orders/<order_ulid>/", methods=["DELETE"])
@required_user_type(["customer"])
def delete_order(order_ulid):
    """
    Cancel a pending order for the authenticated customer.

    This function cancels the order, updates inventory, and sends a cancellation email
    (except in development environment).

    Args:
        order_ulid (str): The ULID of the order to cancel.

    Returns:
        A JSON response indicating success or an error message.
    """
    customer_id = get_jwt_identity()
    config_name = current_app.config["NAME"]

    try:
        order = Order.query.filter_by(id=order_ulid, customer_id=customer_id).first()

        if not order:
            return bad_request(error="Order not found")

        if order.order_status != OrderStatus.PENDING:
            return bad_request(error="Only pending orders can be cancelled")

        order.update(order_status=OrderStatus.CANCELLED)

        for entry in order.order_entries:
            listing = entry.listing
            listing.update(
                quantity=listing.quantity + entry.quantity,
                purchase_count=listing.purchase_count - entry.quantity,
            )

        if config_name != "development":
            send_order_cancellation_email(customer_id, order.id)

        return success_response(status_code=200)
    except SQLAlchemyError as sql_err:
        db.session.rollback()
        return handle_exception(
            error=str(sql_err),
        )
    except Exception as e:
        db.session.rollback()
        return handle_exception(
            error=str(e),
        )


# Future improvements could include:
# - Implementing a more robust inventory management system
# - Adding support for partial order cancellations
# - Implementing a retry mechanism for failed email notifications
