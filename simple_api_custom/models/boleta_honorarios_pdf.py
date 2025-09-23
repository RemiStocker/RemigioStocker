# Asegúrate de que estas líneas estén al principio de tu archivo .py
import base64
import requests
import logging
import json # <-- AÑADE ESTA LÍNEA SI NO ESTÁ
from odoo import models, api, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

class BoletaHonorariosPdf(models.Model):
    _inherit = 'boleta.honorarios'

    # Reemplaza la función completa con esta versión
    def action_get_sii_pdf(self):
        self.ensure_one()

        if self.state not in ('emitted', 'downloaded'):
            raise UserError(_("Solo se puede descargar el PDF de boletas ya emitidas."))
        if not self.numero_boleta:
            raise UserError(_("Esta boleta no tiene un número de folio para consultar."))
        if not self.fecha_emision:
            raise UserError(_("La boleta debe tener una fecha de emisión."))

        _logger.info(f"Iniciando descarga de PDF para boleta folio {self.numero_boleta}")

        config = self.get_simpleapi_config()
        folio = self.numero_boleta
        anio = self.fecha_emision.year
        
        url = f"{config['base_url']}/bhe/pdf/emitidas/{folio}/{anio}"
        
        # --- AJUSTE FINAL ---
        headers = {
            'Authorization': config['api_key'],
            'Accept': 'application/pdf',
            'Content-Type': 'application/json', # Usamos el Content-Type estándar para JSON
        }
        
        payload = {
            "RutUsuario": self.rut_usuario.replace('.', '').replace('-', ''),
            "PasswordSII": self.password_sii,
        }
        # --------------------

        try:
            _logger.info(f"Llamando a endpoint (usando POST): {url}")
            # Usamos POST que es el método estándar para enviar un Body JSON.
            response = requests.post(url, json=payload, headers=headers, timeout=config['timeout'])
            response.raise_for_status()

            if response.content:
                pdf_en_base64 = base64.b64encode(response.content)
                self.write({
                    'pdf_file': pdf_en_base64,
                    'pdf_filename': f"BHE_{folio}.pdf",
                    'state': 'downloaded',
                })
                self.message_post(body="El PDF de la boleta se ha descargado exitosamente desde el SII.")
            else:
                self.message_post(body="La API no devolvió contenido para el PDF, pero la conexión fue exitosa.")

        except requests.exceptions.HTTPError as e:
            error_body = e.response.text
            _logger.error(f"Error HTTP al descargar PDF: {error_body}")
            raise UserError(_(f"La API devolvió un error al intentar descargar el PDF: {error_body}"))
        except Exception as e:
            _logger.error(f"Error inesperado al descargar PDF: {e}")
            raise UserError(_(f"Ocurrió un error inesperado: {e}"))