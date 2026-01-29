"""
Rutas para generación de facturas PDF estilo Apple Store
"""
from datetime import datetime
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from typing import List
from io import BytesIO

from app.services.invoice_pdf_service import InvoicePDFService

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
    customer_number: str = Field(..., examples=["900007"])


class ProductModel(BaseModel):
    """Modelo para producto en la factura"""
    name: str = Field(..., examples=["IPAD MINI 8.3 WIFI 128GB PURPLE - USA"])
    product_number: str = Field(..., examples=["MXN93LL/A"])
    serial_number: str = Field(..., examples=["L9FHJMXD66"])
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
async def generar_factura_prueba(preview: bool = True):
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
async def generar_factura_dinamica(request: InvoiceRequest):
    """
    Genera factura PDF con datos dinámicos desde el frontend
    
    - **order_date**: Fecha de la orden
    - **order_number**: Número de orden
    - **customer**: Información del cliente
    - **products**: Lista de productos (mínimo 1)
    - **invoice_info**: Información adicional
    
    Returns:
        PDF file: Factura personalizada descargable
    """
    try:
        # Validar que hay al menos un producto
        if not request.products:
            raise HTTPException(
                status_code=400,
                detail="Debe incluir al menos un producto"
            )
        
        # Convertir modelos a diccionarios
        customer_dict = request.customer.model_dump()
        products_list = [p.model_dump() for p in request.products]
        invoice_info_dict = request.invoice_info.model_dump()
        
        # Generar PDF dinámico
        pdf_bytes = invoice_service.generar_factura_dinamica(
            order_date=request.order_date,
            order_number=request.order_number,
            customer=customer_dict,
            products=products_list,
            invoice_info=invoice_info_dict
        )
        
        # Preparar respuesta
        pdf_stream = BytesIO(pdf_bytes)
        
        # Nombre del archivo con número de orden
        filename = f"invoice_{request.order_number}_{datetime.now().strftime('%Y%m%d')}.pdf"
        
        return StreamingResponse(
            pdf_stream,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generando factura: {str(e)}"
        )


@router.post("/preview")
async def preview_factura(request: InvoiceRequest):
    """
    Genera preview de la factura (mismo PDF pero con nombre diferente)
    Útil para mostrar en el navegador sin descargar
    """
    try:
        if not request.products:
            raise HTTPException(
                status_code=400,
                detail="Debe incluir al menos un producto"
            )
        
        customer_dict = request.customer.model_dump()
        products_list = [p.model_dump() for p in request.products]
        invoice_info_dict = request.invoice_info.model_dump()
        
        pdf_bytes = invoice_service.generar_factura_dinamica(
            order_date=request.order_date,
            order_number=request.order_number,
            customer=customer_dict,
            products=products_list,
            invoice_info=invoice_info_dict
        )
        
        pdf_stream = BytesIO(pdf_bytes)
        
        # Para preview, usar inline en lugar de attachment
        return StreamingResponse(
            pdf_stream,
            media_type="application/pdf",
            headers={
                "Content-Disposition": "inline"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generando preview: {str(e)}"
        )