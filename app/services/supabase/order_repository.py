"""
OrderRepository - CRUD para pedidos del tablero Kanban
"""

import logging
from typing import Any, Optional, cast
from .base import BaseSupabaseRepository

logger = logging.getLogger(__name__)

_VALID_PHASES = {"pedido", "reservado", "entregado", "completado"}


class OrderRepository(BaseSupabaseRepository):
    """Repositorio de pedidos del tablero Kanban"""

    async def create_order(
        self,
        customer_id: int,
        order_date: str,
        created_by: Optional[str],
        products: list,
    ) -> dict:
        """
        Inserta un pedido y sus productos en la BD.
        Returns the created order row.
        """
        client = await self._get_client()
        assert client is not None, "Supabase client not initialized"
        order_resp = await (
            client.table("orders")
            .insert(
                {
                    "customer_id": customer_id,
                    "order_date": order_date,
                    "created_by": created_by,
                    "phase": "pedido",
                }
            )
            .execute()
        )

        if not order_resp.data:
            raise ValueError("Error al crear el pedido en Supabase")

        data = cast(list[dict[str, Any]], order_resp.data)
        order_id = data[0]["id"]

        if products:
            rows = [
                {
                    "order_id": order_id,
                    "product_id": p["product_id"],
                    "label": p["label"],
                    "unit_price": p.get("unit_price", 0),
                }
                for p in products
            ]
            await client.table("order_products").insert(rows).execute()

        return data[0]

    async def get_all_orders(self) -> list:
        """
        Devuelve todos los pedidos con datos de cliente y productos.
        """
        client = await self._get_client()
        assert client is not None, "Supabase client not initialized"
        resp = await (
            client.table("orders")
            .select("*, customers(name, dni, phone), order_products(*)")
            .order("created_at", desc=True)
            .execute()
        )
        return resp.data or []

    async def update_order_phase(self, order_id: str, phase: str) -> dict:
        client = await self._get_client()
        assert client is not None, "Supabase client not initialized"
        if phase not in _VALID_PHASES:
            raise ValueError(f"Fase inválida: {phase}. Válidas: {_VALID_PHASES}")

        resp = await (
            client.table("orders")
            .update({"phase": phase})
            .eq("id", order_id)
            .execute()
        )

        if not resp.data:
            raise LookupError(f"Pedido {order_id} no encontrado")

        return cast(list[dict[str, Any]], resp.data)[0]

    async def delete_order(self, order_id: str) -> None:
        client = await self._get_client()
        assert client is not None, "Supabase client not initialized"
        await client.table("orders").delete().eq("id", order_id).execute()
