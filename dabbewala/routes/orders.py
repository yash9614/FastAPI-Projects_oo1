from datetime import date, datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select

from database import get_session
from models import Order, OrderCreate, OrderStatus, OrderUpdate, StatusLog

router = APIRouter(prefix="/orders", tags=["orders"])

NEXT_STATUS = {
    OrderStatus.PREPARING: OrderStatus.PICKED_UP,
    OrderStatus.PICKED_UP: OrderStatus.IN_TRANSIT,
    OrderStatus.IN_TRANSIT: OrderStatus.DELIVERED,
    OrderStatus.DELIVERED: None,
}


def apply_status_change(order: Order, new_status: OrderStatus, session: Session) -> None:
    if new_status == order.status:
        return

    expected = NEXT_STATUS[order.status]
    if expected is None:
        raise HTTPException(status_code=409, detail="Order is already delivered")
    if new_status != expected:
        raise HTTPException(
            status_code=409,
            detail=(
                f"Cannot jump {order.status.value} → {new_status.value}. "
                f"Next is {expected.value}"
            ),
        )

    session.add(
        StatusLog(
            order_id=order.id,
            old_status=order.status.value,
            new_status=new_status.value,
        )
    )
    order.status = new_status


@router.post("/", response_model=Order)
def create_order(order: OrderCreate, session: Session = Depends(get_session)):
    db_order = Order(**order.model_dump())
    session.add(db_order)
    session.commit()
    session.refresh(db_order)
    return db_order


@router.get("/", response_model=list[Order])
def list_orders(
    status: OrderStatus | None = Query(default=None, description="Filter by order status"),
    created_date: date | None = Query(default=None, description="Filter by creation date (YYYY-MM-DD)"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    session: Session = Depends(get_session),
):
    query = select(Order)

    if status:
        query = query.where(Order.status == status)

    if created_date:
        start = datetime.combine(created_date, datetime.min.time())
        end = datetime.combine(created_date, datetime.max.time())
        query = query.where(Order.created_at >= start, Order.created_at <= end)

    query = query.offset(skip).limit(limit)
    return session.exec(query).all()


@router.get("/{order_id}", response_model=Order)
def get_order(order_id: int, session: Session = Depends(get_session)):
    order = session.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order


@router.get("/{order_id}/logs", response_model=list[StatusLog])
def get_order_logs(order_id: int, session: Session = Depends(get_session)):
    order = session.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    return session.exec(
        select(StatusLog).where(StatusLog.order_id == order_id)
    ).all()


@router.patch("/{order_id}", response_model=Order)
def update_order(
    order_id: int,
    payload: OrderUpdate,
    session: Session = Depends(get_session),
):
    order = session.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    data = payload.model_dump(exclude_unset=True)
    if not data:
        raise HTTPException(status_code=400, detail="No fields to update")

    new_status = data.pop("status", None)
    if "delivery_address" in data:
        order.delivery_address = data["delivery_address"]
    if new_status is not None:
        apply_status_change(order, new_status, session)

    order.updated_at = datetime.now(timezone.utc)
    session.add(order)
    session.commit()
    session.refresh(order)
    return order
