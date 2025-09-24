import base64
import requests
import logging
import json
from odoo import models, api, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

# --- Definición de la Clase ---
# Creamos una nueva clase que "extiende" la funcionalidad del modelo de boletas.
class BoletaHonorariosPdf(models.Model):
    _inherit = 'boleta.honorarios'

    # --- Definición del Método Principal ---
    def action_get_sii_pdf(self):
        self.ensure_one()
        
        # --- Validaciones Previas
        if self.state not in ('emitted', 'downloaded'):
            raise UserError(_("Solo se puede descargar el PDF de boletas ya emitidas."))
        if not self.numero_boleta:
            raise UserError(_("Esta boleta no tiene un número de folio para consultar."))
        if not self.fecha_emision:
            raise UserError(_("La boleta debe tener una fecha de emisión."))

        _logger.info(f"Iniciando descarga de PDF para boleta folio {self.numero_boleta}")

        # --- Preparación de la Llamada a la API ---

        # Reutilizamos una función del modelo original para obtener la configuración (API Key, URL base)
        config = self.get_simpleapi_config()
        folio = self.numero_boleta
        anio = self.fecha_emision.year
        
        # Construimos la URL completa del endpoint, insertando el folio y el año.
        url = f"{config['base_url']}/bhe/pdf/emitidas/{folio}/{anio}"

        # Preparamos las cabeceras/headers de la petición HTTP.
        headers = {
            'Authorization': config['api_key'],
            'Accept': 'application/pdf', # Le decimos al servidor que esperamos recibir un PDF.
        }
        
        # Preparamos el "cuerpo" (payload) de la petición con las credenciales del SII.
        payload = {
            "RutUsuario": self.rut_usuario.replace('.', '').replace('-', ''),
            "PasswordSII": self.password_sii,
        }

        # --- Ejecución y Manejo de la Respuesta ---
        try:
            _logger.info(f"Llamando a GET endpoint: {url}")
            response = requests.get(url, json=payload, headers=headers, timeout=config['timeout'])
            response.raise_for_status()

            if response.content:
                pdf_en_base64 = base64.b64encode(response.content)
                self.write({
                    'pdf_file': pdf_en_base64,
                    'pdf_filename': f"BHE_{folio}.pdf",
                    'state': 'downloaded',
                })
                self.message_post(body="El PDF de la boleta se ha descargado exitosamente desde el SII.")
                
                return {
                    'type': 'ir.actions.act_url',
                    'url': f'/boleta_honorarios/download/{self.id}',
                    'target': 'self',
                }

            else:
                self.message_post(body="La API no devolvió contenido para el PDF, pero la conexión fue exitosa.")

        # --- Manejo de Errores Específicos ---
        except requests.exceptions.HTTPError as e:
            error_body = e.response.text
            _logger.error(f"Error HTTP al descargar PDF: {error_body}")
            raise UserError(_(f"La API devolvió un error al intentar descargar el PDF: {error_body}"))
        except Exception as e:
            _logger.error(f"Error inesperado al descargar PDF: {e}")
            raise UserError(_(f"Ocurrió un error inesperado: {e}"))
        
        return True