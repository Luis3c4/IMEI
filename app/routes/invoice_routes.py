"""
Rutas para generación de facturas PDF estilo Apple Store
"""
from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from typing import List, Optional
from io import BytesIO
import asyncio

from app.services.invoice_pdf_service import InvoicePDFService
from app.services.supabase_service import supabase_service
from app.middleware import get_current_user_id

router = APIRouter()

# Inicializar servicio
invoice_service = InvoicePDFService()


# Modelos Pydantic para validación
class LocationModel(BaseModel):
    """Modelo para información de ubicación"""
    name: str = Field(..., examples=["Apple Pioneer Place"])
    address: str = Field(..., examples=["450 SW Yamhill Street"])
    city_state_zip: str = Field(..., examples=["PORTLAND OR 97204-2007"])
    country: str = Field(default="United States")


class CustomerModel(BaseModel):
    """Modelo para información del cliente"""
    name: str = Field(..., examples=["Geraldine Eva Flores Flores"])
    dni: str = Field(..., examples=["12345678"], description="DNI del cliente (requerido - identificador único)")
    phone: Optional[str] = Field(default=None, examples=["+51 999 888 777"])


class ProductModel(BaseModel):
    """Modelo para producto en la factura"""
    product_id: int = Field(..., examples=[1], description="ID del producto (FK a products.id)")
    variant_id: Optional[int] = Field(None, examples=[5], description="ID del variant (FK a product_variants.id)")
    product_item_id: Optional[int] = Field(None, examples=[42], description="ID del product_item (FK a product_items.id)")
    name: str = Field(..., examples=["IPAD MINI 8.3 WIFI 128GB PURPLE - USA"])
    product_number: str = Field(..., examples=["MXN93LL/A"])
    item_price: float = Field(..., examples=[499.00])
    quantity_ordered: int = Field(default=1)
    quantity_fulfilled: int = Field(default=1)
    extended_price: float = Field(..., examples=[499.00])

"""Modelo para información de pago(FUTURE USE)"""
class PaymentModel(BaseModel):
    """Modelo para información de pago"""
    sales_tax: float = Field(default=0.00)
    amount_due: float = Field(default=0.00)
    card_type: str = Field(..., examples=["Visa"])
    card_last_four: str = Field(..., examples=["8722"])
    charged_amount: float = Field(..., examples=[628.00])


class InvoiceInfoModel(BaseModel):
    """Modelo para información adicional de la factura"""
    invoice_number: str = Field(..., examples=["MA85377130"])
    invoice_date: str = Field(..., examples=["September 04, 2025"])
    terms: str = Field(default="Credit Card")


class InvoiceRequest(BaseModel):
    """Modelo completo para solicitud de factura"""
    order_date: str = Field(..., examples=["September 04, 2025"])
    order_number: str = Field(..., examples=["W1351042737"])
    customer: CustomerModel
    products: List[ProductModel]
    invoice_info: InvoiceInfoModel


@router.get("/test/pdf")
def generar_factura_prueba(preview: bool = True):
    """
    Genera factura PDF estática para pruebas
    
    Returns:
        PDF file: Factura de ejemplo con datos estáticos
    """
    try:
        # Generar PDF estático
        pdf_bytes = invoice_service.generar_factura_estatica()
        
        # Preparar respuesta como stream
        pdf_stream = BytesIO(pdf_bytes)
        
        # Nombre del archivo
        filename = f"factura_apple_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        disposition = "inline" if preview else f"attachment; filename={filename}"

        return StreamingResponse(
            pdf_stream,
            media_type="application/pdf",
            headers={
                "Content-Disposition": disposition
            }
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generando factura de prueba: {str(e)}"
        )


@router.post("/generate/pdf")
async def generar_factura_dinamica(
    request: InvoiceRequest,
    user_id: str = Depends(get_current_user_id)
):
    """
    Genera factura PDF con datos dinámicos desde el frontend
    Requiere autenticación JWT de Supabase
    
    - **order_date**: Fecha de la orden
    - **order_number**: Número de orden
    - **customer**: Información del cliente
    - **products**: Lista de productos (mínimo 1)
    - **invoice_info**: Información de factura (invoice_number, invoice_date)
    
    Returns:
        PDF file: Factura personalizada descargable con customer_number generado automáticamente
    """
    try:
        # Validar que hay al menos un producto
        if not request.products:
            raise HTTPException(
                status_code=400,
                detail="Debe incluir al menos un producto"
            )
        
        # Paso 1: Obtener o crear cliente PRIMERO (usando DNI único)
        # Esto nos da el customer.id para relacionar con la factura
        customer_result = await supabase_service.customers.get_or_create_customer(
                name=request.customer.name,
                dni=request.customer.dni,
                phone=request.customer.phone
            )
        
        if not customer_result['success']:
            raise HTTPException(
                status_code=500,
                detail=f"Error al gestionar cliente: {customer_result.get('error', 'Error desconocido')}"
            )
        
        # Obtener el ID del cliente para la foreign key
        customer_data = customer_result['data']
        customer_id = customer_data['id']
        
        # Paso 2: Crear registro en la tabla invoices con la relación al customer
        # El trigger generará automáticamente el customer_number para el PDF
        invoice_result = await supabase_service.invoices.create_invoice(
                invoice_number=request.invoice_info.invoice_number,
                invoice_date=request.invoice_info.invoice_date,
                customer_id=customer_id,
                user_id=user_id,
                order_number=request.order_number
            )
        
        if not invoice_result['success']:
            raise HTTPException(
                status_code=500,
                detail=f"Error al crear factura: {invoice_result.get('error', 'Error desconocido')}"
            )
        
        # Obtener el customer_number generado automáticamente por el trigger
        invoice_data = invoice_result['data']
        generated_customer_number = invoice_data['customer_number']
        invoice_id = invoice_data['id']
        
        # Paso 2.5: Persistir productos asociados a la factura
        # Guardar snapshot de los productos en el momento de la venta
        products_list = [p.model_dump() for p in request.products]
        invoice_products_result = await supabase_service.invoices.create_invoice_products(
                invoice_id=invoice_id,
                products_list=products_list
            )
        
        if not invoice_products_result['success']:
            # Log warning pero no fallar la generación del PDF
            # Ya que la factura ya fue creada exitosamente
            print(f"⚠️ Warning: Error al guardar productos de factura {invoice_id}: {invoice_products_result.get('error')}")
        
        # Paso 2.75: Resolver serial_number de cada producto desde product_items para el PDF
        item_ids = [p.product_item_id for p in request.products if p.product_item_id is not None]
        serial_by_item_id: dict = {}
        if item_ids:
            serial_result = await supabase_service.invoices.get_product_items_by_ids(item_ids)
            if serial_result['success']:
                serial_by_item_id = serial_result['data']
        
        # Enriquecer la lista de productos con serial_number resuelto desde BD
        products_for_pdf = []
        for p_dict, p_req in zip(products_list, request.products):
            resolved_serial = serial_by_item_id.get(p_req.product_item_id) if p_req.product_item_id else None
            products_for_pdf.append({**p_dict, 'serial_number': resolved_serial or ''})
        
        # Paso 3: Preparar datos del cliente para el PDF con el customer_number de invoices
        customer_dict = {
            'name': request.customer.name,
            'customer_number': generated_customer_number,  # Usar el generado por invoice
            'dni': request.customer.dni,
            'phone': request.customer.phone
        }
        
        # Convertir invoice_info a diccionario
        invoice_info_dict = request.invoice_info.model_dump()
        
        # Generar PDF dinámico
        pdf_bytes = await asyncio.to_thread(
            invoice_service.generar_factura_dinamica,
            order_date=request.order_date,
            order_number=request.order_number,
            customer=customer_dict,
            products=products_for_pdf,
            invoice_info=invoice_info_dict,
        )
        
        # Preparar respuesta
        pdf_stream = BytesIO(pdf_bytes)
        
        # Nombre del archivo con número de orden
        filename = f"invoice_{request.order_number}_{datetime.now().strftime('%Y%m%d')}.pdf"
        
        return StreamingResponse(
            pdf_stream,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename={filename}",
                "X-Customer-Number": generated_customer_number,  # Header con el customer_number generado
                "X-Invoice-Id": str(invoice_id)  # ID de la factura creada
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generando factura: {str(e)}"
        )


@router.get("/customer/{customer_id}")
async def listar_facturas_por_cliente(
    customer_id: int,
    user_id: str = Depends(get_current_user_id)
):
    """
    Lista todas las facturas de un cliente.
    Requiere autenticación JWT de Supabase.
    """
    try:
        result = await supabase_service.invoices.get_invoices_by_customer_id(customer_id)

        # No encontradas no es un error — puede que el cliente aún no tenga facturas
        invoices = result.get('data', []) if result['success'] else []

        return {"success": True, "data": invoices}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listando facturas: {str(e)}")


@router.get("/{invoice_id}/pdf")
async def regenerar_factura_pdf(
    invoice_id: int,
    user_id: str = Depends(get_current_user_id)
):
    """
    Regenera el PDF de una factura existente desde los datos guardados en BD.
    Requiere autenticación JWT de Supabase.
    """
    try:
        result = await supabase_service.invoices.get_invoice_with_products(invoice_id)

        if not result['success']:
            raise HTTPException(
                status_code=404,
                detail=f"Factura no encontrada: {result.get('error', 'Error desconocido')}"
            )

        data = result['data']
        invoice = data['invoice']
        customer = data['customer']
        products = data['products']

        # Reconstruir customer_dict para el PDF
        customer_dict = {
            'name': customer.get('name', ''),
            'customer_number': invoice.get('customer_number', ''),
            'dni': customer.get('dni', ''),
            'phone': customer.get('phone', ''),
        }

        # Reconstruir lista de productos para el PDF
        products_for_pdf = [
            {
                'name': p.get('name', ''),
                'product_number': p.get('product_number', ''),
                'serial_number': p.get('serial_number', ''),
                'item_price': p.get('unit_price', 0),
                'extended_price': p.get('extended_price', 0),
                'quantity_ordered': 1,
                'quantity_fulfilled': 1,
            }
            for p in products
        ]

        # order_number: usar el guardado; fallback a invoice_number para facturas legacy
        order_number = invoice.get('order_number') or f"W{str(int(datetime.now().timestamp() * 1000))[-10:]}"
        invoice_date = invoice.get('invoice_date', '')

        invoice_info_dict = {
            'invoice_number': invoice.get('invoice_number', ''),
            'invoice_date': invoice_date,
            'terms': 'Credit Card',
        }

        pdf_bytes = await asyncio.to_thread(
            invoice_service.generar_factura_dinamica,
            order_date=invoice_date,
            order_number=order_number,
            customer=customer_dict,
            products=products_for_pdf,
            invoice_info=invoice_info_dict,
        )

        pdf_stream = BytesIO(pdf_bytes)
        filename = f"invoice_{order_number}.pdf"

        return StreamingResponse(
            pdf_stream,
            media_type="application/pdf",
            headers={"Content-Disposition": f"inline; filename={filename}"}
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error regenerando PDF: {str(e)}")


@router.get("/{invoice_id}/details")
async def obtener_factura_con_productos(
    invoice_id: int,
    user_id: str = Depends(get_current_user_id)
):
    """
    Obtiene los detalles completos de una factura incluyendo sus productos
    Requiere autenticación JWT de Supabase
    
    Args:
        invoice_id: ID de la factura a consultar
        
    Returns:
        JSON con información de la factura y lista de productos asociados
    """
    try:
        # Obtener factura con productos
        result = await supabase_service.invoices.get_invoice_with_products(invoice_id)
        
        if not result['success']:
            raise HTTPException(
                status_code=404,
                detail=f"Factura no encontrada: {result.get('error', 'Error desconocido')}"
            )
        
        return {
            "success": True,
            "data": result['data']
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error obteniendo detalles de factura: {str(e)}"
        )
