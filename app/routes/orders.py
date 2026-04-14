"""
Orders Router — Kanban board CRUD
GET    /api/orders
POST   /api/orders
PATCH  /api/orders/{order_id}/phase
DELETE /api/orders/{order_id}
"""

import logging
from fastapi import APIRouter, HTTPException, status
from app.schemas import (
    OrderCreate,
    OrderPhaseUpdate,
    OrderProductResponse,
    OrderResponse,
)
from app.services.supabase_service import supabase_service

logger = logging.getLogger(__name__)
router = APIRouter()

_VALID_PHASES = {"pedido", "reservado", "entregado", "completado"}


def _serialize(o: dict) -> OrderResponse:
    customer = o.get("customers") or {}
    prods = o.get("order_products") or []
    return OrderResponse(
        id=o["id"],
        customer_id=o["customer_id"],
        customer_name=customer.get("name"),
        customer_dni=customer.get("dni"),
        customer_phone=customer.get("phone"),
        phase=o["phase"],
        order_date=o["order_date"],
        created_by=o.get("created_by"),
        created_at=str(o.get("created_at", "")),
        updated_at=str(o.get("updated_at", "")),
        products=[
            OrderProductResponse(
                id=p["id"],
                product_id=p["product_id"],
                variant_id=p.get("variant_id"),
                label=p["label"],
                unit_price=float(p.get("unit_price", 0)),
            )
            for p in prods
        ],
    )


@router.get("/", response_model=list[OrderResponse])
async def get_orders():
    try:
        rows = supabase_service.orders.get_all_orders()
        return [_serialize(r) for r in rows]
    except Exception as e:
        logger.error(f"Error al obtener pedidos: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order(body: OrderCreate):
    try:
        # get_or_create customer so we always have a customer_id
        customer_result = supabase_service.customers.get_or_create_customer(
            name=body.customer_name,
            dni=body.customer_dni,
            phone=body.customer_phone,
        )
        if not customer_result.get("success"):
            raise HTTPException(
                status_code=400,
                detail=customer_result.get("error", "Error al obtener/crear cliente"),
            )
        customer_id = customer_result["data"]["id"]

        order = supabase_service.orders.create_order(
            customer_id=customer_id,
            order_date=body.order_date,
            created_by=None,
            products=[p.model_dump() for p in body.products],
        )

        # Fetch complete row (includes customer + products via JOIN)
        rows = supabase_service.orders.get_all_orders()
        full = next((r for r in rows if r["id"] == order["id"]), None)
        return _serialize(full or order)
    except Exception as e:
        logger.error(f"Error al crear pedido: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/{order_id}/phase", response_model=OrderResponse)
async def update_order_phase(order_id: str, body: OrderPhaseUpdate):
    if body.phase not in _VALID_PHASES:
        raise HTTPException(
            status_code=422,
            detail=f"Fase inválida. Válidas: {sorted(_VALID_PHASES)}",
        )
    try:
        supabase_service.orders.update_order_phase(order_id, body.phase)
        rows = supabase_service.orders.get_all_orders()
        full = next((r for r in rows if r["id"] == order_id), None)
        if not full:
            raise HTTPException(status_code=404, detail="Pedido no encontrado")
        return _serialize(full)
    except HTTPException:
        raise
    except LookupError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error al actualizar fase: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_order(order_id: str):
    try:
        supabase_service.orders.delete_order(order_id)
    except Exception as e:
        logger.error(f"Error al eliminar pedido: {e}")
        raise HTTPException(status_code=500, detail=str(e))
