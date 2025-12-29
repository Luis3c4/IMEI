"""
Servicio para generación de PDFs de facturas estilo Apple Store
"""
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
from io import BytesIO

from weasyprint import HTML, CSS
from jinja2 import Environment, FileSystemLoader, select_autoescape


class InvoicePDFService:
    """Servicio para generar facturas PDF estilo Apple Store"""
    
    def __init__(self): 
        # Configurar Jinja2 para templates
        template_dir = Path(__file__).parent.parent / "templates" / "invoices"
        self.env = Environment(
            loader=FileSystemLoader(str(template_dir)),
            autoescape=select_autoescape(['html', 'xml'])
        )    
    def generar_factura_estatica(self) -> bytes:
        """
        Genera PDF con datos estáticos para pruebas
        
        Returns:
            bytes: PDF generado en bytes
        """
        # Cargar template HTML
        template = self.env.get_template("apple_invoice.html")
        
        # Renderizar HTML (sin datos dinámicos por ahora)
        html_content = template.render()
        
        # Directorio base para recursos (imágenes, etc.)
        template_dir = Path(__file__).parent.parent / "templates" / "invoices"
        
        # Generar PDF
        pdf_bytes = self._html_to_pdf(html_content, base_url=str(template_dir))
        
        return pdf_bytes
    
    def generar_factura_dinamica(
        self,
        order_date: str,
        location: Dict[str, str],
        order_number: str,
        customer: Dict[str, Any],
        products: List[Dict[str, Any]],
        payment: Dict[str, Any],
        invoice_info: Dict[str, Any]
    ) -> bytes:
        """
        Genera PDF con datos dinámicos desde el frontend
        
        Args:
            order_date: Fecha de la orden
            location: Información de la tienda
            order_number: Número de orden
            customer: Información del cliente
            products: Lista de productos ordenados
            payment: Información de pago
            invoice_info: Información adicional de la factura
            
        Returns:
            bytes: PDF generado en bytes
        """
        # Calcular totales
        subtotal = sum(float(p.get('extended_price', 0)) for p in products)
        sales_tax = float(payment.get('sales_tax', 0))
        total = subtotal + sales_tax
        amount_due = float(payment.get('amount_due', 0))
        
        # Cargar template dinámico
        template = self.env.get_template("apple_invoice_dynamic.html")
        
        # Preparar contexto
        contexto = {
            "order_date": order_date,
            "location": location,
            "order_number": order_number,
            "customer": customer,
            "products": products,
            "subtotal": subtotal,
            "sales_tax": sales_tax,
            "total": total,
            "amount_due": amount_due,
            "payment": payment,
            "invoice_info": invoice_info
        }
        
        # Renderizar HTML
        html_content = template.render(**contexto)
        
        # Directorio base para recursos (imágenes, etc.)
        template_dir = Path(__file__).parent.parent / "templates" / "invoices"
        
        # Generar PDF
        pdf_bytes = self._html_to_pdf(html_content, base_url=str(template_dir))
        
        return pdf_bytes
    
    def _html_to_pdf(self, html_content: str, base_url: Optional[str] = None) -> bytes:
        """
        Convierte HTML a PDF usando WeasyPrint
        
        Args:
            html_content: String con HTML a convertir
            base_url: URL base para resolver rutas relativas de recursos (imágenes, CSS, etc.)
            
        Returns:
            bytes: PDF generado
        """
        # Crear objeto HTML de WeasyPrint
        html = HTML(string=html_content, base_url=base_url)
        
        # Generar PDF en memoria
        pdf_buffer = BytesIO()
        html.write_pdf(pdf_buffer)
        
        # Obtener bytes del PDF
        pdf_bytes = pdf_buffer.getvalue()
        pdf_buffer.close()
        
        return pdf_bytes