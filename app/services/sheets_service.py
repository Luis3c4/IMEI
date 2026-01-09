from typing import Dict, Any
import gspread
from google.oauth2.service_account import Credentials
from ..config import settings
from datetime import datetime

class SheetsService:
    """Servicio para manejar Google Sheets"""
    
    SCOPES = [
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive'
    ]
    
    def __init__(self):
        self.sheet_id = settings.GOOGLE_SHEET_ID
        self.client = self._get_client()
    
    def _get_client(self):
        """Obtiene cliente autenticado de Google Sheets"""
        import json
        import os
        
        if settings.GOOGLE_CREDENTIALS_JSON:
            # Verificar si es un path de archivo o JSON string
            if os.path.isfile(settings.GOOGLE_CREDENTIALS_JSON):
                # Es un path de archivo
                creds = Credentials.from_service_account_file(
                    settings.GOOGLE_CREDENTIALS_JSON, scopes=self.SCOPES
                )
            else:
                # Es un JSON string
                try:
                    creds_dict = json.loads(settings.GOOGLE_CREDENTIALS_JSON)
                    creds = Credentials.from_service_account_info(
                        creds_dict, scopes=self.SCOPES
                    )
                except json.JSONDecodeError:
                    raise ValueError(
                        "GOOGLE_CREDENTIALS_JSON debe ser un path válido a un archivo JSON "
                        "o un string JSON válido"
                    )
        else:
            # Usar archivo por defecto
            creds = Credentials.from_service_account_file(
                'credentials.json', scopes=self.SCOPES
            )
        return gspread.authorize(creds)
    
    def add_record(self, device_info: Dict[str, Any], metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Agrega registro al sheet"""
        try:
            sheet = self.client.open_by_key(self.sheet_id).worksheet('Historial')
            
            row = [
                datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                metadata.get('input_value', ''),
                device_info.get('Serial Number', ''),
                device_info.get('Model Description', ''),
                device_info.get('IMEI', ''),                             # IMEI
                device_info.get('IMEI2', ''),                            # IMEI2
                device_info.get('MEID', ''),                             # MEID
                device_info.get('Warranty Status', ''),                  # Warranty Status
                device_info.get('Estimated Purchase Date', ''),          # Purchase Date
                device_info.get('Purchase Country', ''),                 # Purchase Country
                device_info.get('Sim-Lock Status', ''),                  # Sim-Lock Status
                device_info.get('Locked Carrier', ''),                   # Locked Carrier
                device_info.get('iCloud Lock', ''),                      # iCloud Lock
                device_info.get('Demo Unit', ''),                        # Demo Unit
                device_info.get('Loaner Device', ''),                    # Loaner Device
                device_info.get('Refurbished Device', ''),               # Refurbished Device
                device_info.get('Replaced Device', ''),                  # Replaced Device
                device_info.get('Replacement Device', ''),
                metadata.get('service_id', ''),
                metadata.get('order_id', ''),
                metadata.get('price', ''),
                metadata.get('balance', ''),
            ]
            
            sheet.append_row(row)
            
            return {
                'success': True,
                'total_records': len(sheet.get_all_values()) - 1
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    def get_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas del sheet"""
        try:
            sheet = self.client.open_by_key(self.sheet_id).worksheet('Historial')
            records = sheet.get_all_values()
            total_consultas = len(records) - 1  # Excluir header
            
            ultima_consulta = records[-1][0] if total_consultas > 0 else None
            
            return {
                'success': True,
                'total_consultas': total_consultas,
                'ultima_consulta': ultima_consulta,
                'sheet_url': f"https://docs.google.com/spreadsheets/d/{self.sheet_id}",
                'sheet_existe': True
            }
        except gspread.SpreadsheetNotFound:
            return {
                'success': False,
                'error': 'Sheet no encontrado',
                'sheet_existe': False
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    def get_sheet_url(self) -> Dict[str, Any]:
        """Devuelve la URL del sheet"""
        try:
            # Verificar si el sheet existe
            self.client.open_by_key(self.sheet_id)
            return {
                'url': f"https://docs.google.com/spreadsheets/d/{self.sheet_id}",
                'sheet_id': self.sheet_id
            }
        except gspread.SpreadsheetNotFound:
            return {
                'error': 'Sheet no encontrado',
                'sheet_id': self.sheet_id
            }
        except Exception as e:
            return {'error': str(e)}
    def initialize_sheet(self) -> Dict[str, Any]:
        """Inicializa el sheet con headers si no existe"""
        try:
            sheet = self.client.open_by_key(self.sheet_id).worksheet('Historial')
            first_row = sheet.row_values(1)
            if not first_row:
                headers = [
                    'Fecha Consulta',
                    'Input Consultado',
                    'Serial Number',
                    'Model Description',
                    'IMEI',
                    'IMEI2',
                    'MEID',
                    'Warranty Status',
                    'Purchase Date',
                    'Purchase Country',
                    'Sim-Lock Status',
                    'Locked Carrier',
                    'iCloud Lock',
                    'Demo Unit',
                    'Loaner Device',
                    'Refurbished Device',
                    'Replaced Device',
                    'Replacement Device',
                    'Service ID',
                    'Order ID',
                    'Precio',
                    'Balance Restante'
                ]
                sheet.append_row(headers)
                # Formatear headers (bold y color)
                sheet.format('A1:U1', {
                    'textFormat': {'bold': True, 'fontSize': 11},
                    'backgroundColor': {'red': 0.2, 'green': 0.6, 'blue': 0.9},
                    'horizontalAlignment': 'CENTER'
                })
                # Ajustar ancho de columnas
                sheet.format('A1:U1', {'wrapStrategy': 'WRAP'})
            return {'success': True, 'message': 'Sheet ya inicializado'}
        except Exception as e:
            print(f"Error al inicializar sheet: {str(e)}")
            return {'success': False, 'error': str(e)}