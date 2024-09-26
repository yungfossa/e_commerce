from datetime import UTC, datetime

from flask import Blueprint, current_app, request
from flask_jwt_extended import get_jwt_identity
from marshmallow import ValidationError
from models import Cart, Listing, Order, OrderEntry, OrderStatus

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import joinedload
from core import db
from core.blueprints.errors.handlers import handle_exception

from core.utils import (
    bad_request,
    required_user_type,
    send_order_cancellation_email,
    send_order_confirmation_email,
    success_response,
)
from core.validators.customer.customer_orders import (
    OrderCreationSchema,
    OrderSummaryFilterSchema,
)

customer_orders_bp = Blueprint("customer_orders", __name__)

config_name = current_app.config["NAME"]

validate_order_creation = OrderCreationSchema()
validate_order_summary_filters = OrderSummaryFilterSchema()


@customer_orders_bp.route("/orders", methods=["POST"])
@required_user_type(["customer"])
def create_orders():
    customer_id = get_jwt_identity()

    try:
        # Validate input data
        validated_data = validate_order_creation.load(data=request.get_json())

        cart = Cart.query.filter_by(customer_id=customer_id).first()

        # Check if cart exists and is not empty
        if not cart or not cart.cart_entries:
            return bad_request(message="I cannot create an order: the cart is empty")

        # Calculate total order price
        total_order_price = sum(
            entry.price * entry.quantity for entry in cart.cart_entries
        )

        # Create new order
        new_order = Order.create(
            customer_id=customer_id,
            price=total_order_price,
            order_status=OrderStatus.PENDING,
            purchased_at=datetime.now(UTC),
            address_street=validated_data["address_street"],
            address_city=validated_data["address_city"],
            address_state=validated_data["address_state"],
            address_country=validated_data["address_country"],
            address_postal_code=validated_data["address_postal_code"],
        )

        # Process each cart entry
        for cart_entry in cart.cart_entries:
            listing = cart_entry.listing

            # Create order entry
            OrderEntry.create(
                order_id=new_order.id,
                listing_id=cart_entry.listing_id,
                quantity=cart_entry.amount,
                price=listing.price,
            )

            # Update listing quantity and purchase count
            listing.update(
                quantity=listing.quantity - cart_entry.amount,
                purchase_count=listing.purchase_count + cart_entry.amount,
            )

        # Clear the cart
        for entry in cart.cart_entries:
            entry.delete()

        if config_name != "development":
            send_order_confirmation_email(customer_id, new_order.id)

        return success_response(
            message="Order created successfully", data={"order_id": new_order.id}
        )

    except ValidationError as ve:
        return bad_request(message=f"Validation error: {ve.messages}")
    except Exception as e:
        db.session.rollback()
        return bad_request(message=f"Error creating order: {str(e)}")


@customer_orders_bp.route("/orders/<order_ulid>", methods=["GET"])
@required_user_type(["customer"])
def get_order_details(order_ulid):
    customer_id = get_jwt_identity()

    try:
        order = Order.query.filter_by(id=order_ulid, customer_id=customer_id).first()

        if not order:
            return bad_request(message="Order not found")

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
                    "quantity": entry.listing.quantity,
                    "price": float(entry.listing.price),
                }
                for entry in order.entries
            ],
        }
        return success_response(
            message="Order details retrieved successfully", data=order_data
        )
    except SQLAlchemyError as e:
        db.session.rollback()
        return handle_exception(
            message="A database error occurred while fetching the order details. Please try again later.",
            error=str(e),
        )
    except Exception as e:
        return bad_request(message=f"Error retrieving order details: {str(e)}")


@customer_orders_bp.route("/orders/summary", methods=["GET"])
@required_user_type(["customer"])
def get_orders_summary():
    customer_id = get_jwt_identity()

    try:
        # Validate and load filter parameters from request
        filters = validate_order_summary_filters.load(request.args)
    except ValidationError as err:
        return bad_request(message="Invalid filter parameters", errors=err.messages)

    try:
        # Construct query with eager loading of related models
        query = Order.query.filter_by(customer_id=customer_id).options(
            joinedload(Order.order_entries)
            .joinedload(OrderEntry.listing)
            .joinedload(Listing.product)
        )

        # Apply status filter if provided
        if filters.get("status"):
            query = query.filter(
                Order.order_status == OrderStatus[filters["status"].upper()]
            )

        # Apply sorting based on filter parameters
        order_column = getattr(Order, filters["order_by"])
        if filters["order_direction"] == "desc":
            query = query.order_by(order_column.desc())
        else:
            query = query.order_by(order_column.asc())

        # Apply pagination
        total_items = query.count()
        orders = query.offset(filters["offset"]).limit(filters["limit"]).all()

        # Construct response data
        orders_data = [
            {
                "id": order.id,
                "status": order.order_status.value,
                "total_amount": float(order.price),
                "created_at": order.purchased_at.isoformat(),
                "entries": [
                    {
                        "product_name": entry.listing.product.name,
                        "quantity": entry.listing.quantity,
                        "price": float(entry.listing.price),
                    }
                    for entry in order.entries
                ],
            }
            for order in orders
        ]

        # Return successful response with orders data and pagination info
        return success_response(
            message="Orders history retrieved successfully",
            data={
                "orders": orders_data,
                "pagination": {
                    "offset": filters["offset"],
                    "limit": filters["limit"],
                    "total_items": total_items,
                },
            },
        )
    except SQLAlchemyError as e:
        db.session.rollback()
        return handle_exception(
            message="A database error occurred while fetching the order details. Please try again later.",
            error=str(e),
        )
    except Exception as e:
        return bad_request(message=f"Error retrieving orders history: {str(e)}")


@customer_orders_bp.route("/orders/<order_id>/", methods=["DELETE"])
@required_user_type(["customer"])
def delete_order(order_ulid):
    customer_id = get_jwt_identity()

    try:
        order = Order.query.filter_by(id=order_ulid, customer_id=customer_id).first()

        if not order:
            return bad_request(message="Order not found")

        if order.order_status != OrderStatus.PENDING:
            return bad_request(message="Only pending orders can be cancelled")

        # Update order status to cancelled
        order.update(order_status=OrderStatus.CANCELLED)

        # Revert listing quantities and purchase counts
        for entry in order.order_entries:
            listing = entry.listing
            listing.update(
                quantity=listing.quantity + entry.quantity,
                purchase_count=listing.purchase_count - entry.quantity,
            )

        if config_name != "development":
            send_order_cancellation_email(customer_id, order.id)

        return success_response(
            message="Order cancelled successfully", data={"order_id": order.id}
        )
    except SQLAlchemyError as e:
        db.session.rollback()
        return handle_exception(
            message="A database error occurred while cancelling the order. Please try again later.",
            error=str(e),
        )
    except Exception as e:
        db.session.rollback()
        return bad_request(message=f"Error cancelling order: {str(e)}")
