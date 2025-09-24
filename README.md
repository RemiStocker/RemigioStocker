# Boleta de Honorarios - Módulo Odoo (Integración con SimpleAPI)

Este módulo permite la **emisión, descarga y anulación** de Boletas de Honorarios electrónicas a través de [SimpleAPI](https://servicios.simpleapi.cl/api), directamente desde **Odoo**.

---

## 🚀 Funcionalidades principales

1. **Emisión de Boletas de Honorarios**

   * Generación de boletas con datos del emisor y receptor.
   * Validaciones de RUT, valores y correos electrónicos.
   * Llamadas directas a la API de SimpleAPI.

2. **Descarga de PDFs**

   * Obtención del PDF oficial desde el SII a través de SimpleAPI.
   * Almacenamiento en el campo binario `pdf_file`.
   * Visualización en Odoo mediante un **iframe preview**. //No habilitado

3. **Anulación de boletas**

   * **Legacy**: Anulación vía endpoint clásico (`/bhe/anular`).
   * **Nuevo**: Anulación con motivo vía endpoint REST (`/bhe/anular/<folio>/<motivo>`).

4. **Automatizaciones**

   * Cron configurado para descargar PDFs pendientes cada 15 minutos. //No habilitado

5. **Configuración flexible**

   * Parámetros de conexión a SimpleAPI administrables desde `Ajustes > Configuración`:

     * API Key
     * Base URL
     * Timeout

---

## 📂 Estructura del módulo

```
src/user/simple_api_custom/
├── controllers/
│   ├── __init__.py
│   └── main.py              # Endpoints HTTP/JSON
├── data/
│   └── ir_cron_data.xml     # Cron de descargas
├── models/
│   ├── __init__.py
│   ├── boleta_honorarios.py # Modelo principal con lógica de negocio
│   ├── boleta_honorarios_pdf.py # Extensión para descarga de PDFs
│   └── res_config_settings.py   # Configuración en ajustes
├── security/
│   └── ir.model.access.csv  # Reglas de acceso
├── static/
│   ├── description/icon.png
│   └── src/js/preview_iframe.js # Lógica JS para previsualizar PDFs
├── views/
│   ├── assets.xml
│   └── boleta_honorarios_views.xml
```

---

## 🔑 Endpoints HTTP expuestos

### 1. Webhook de recepción (ejemplo de integración externa)

```
POST /boleta_honorarios/webhook
```

* Tipo: JSON
* Autenticación: `none`
* Uso: Placeholder para integrar callbacks externos.

### 2. Descarga de PDF

```
GET /boleta_honorarios/download/<boleta_id>
```

* Tipo: HTTP
* Autenticación: `user`
* Retorna: Archivo PDF adjunto.

### 3. Anulación vía API (Path Params)

```
POST /boleta_honorarios/anular/<boleta_id>/<motivo>
```

* Tipo: JSON
* Autenticación: `user`
* Parámetros:

  * `boleta_id`: ID interno de Odoo
  * `motivo`: Código (1: no pago, 2: no prestación, 3: error digitación)

---

## ⚙️ Modelos principales

### `boleta.honorarios`

Campos destacados:

* `numero_boleta`: Folio asignado por SII
* `rut_usuario`, `password_sii`: Credenciales emisor
* `partner_id`, `receptor_rut`, `receptor_nombre`: Datos receptor
* `descripcion_servicio`, `valor_bruto`: Detalles de la prestación
* `pdf_file`, `pdf_filename`: Archivo PDF descargado
* `state`: Flujo de estado (`draft → processing → emitted → downloaded → cancelled/error`)

### Métodos clave

* `action_emitir_boleta()`: Emisión vía API.
* `action_get_sii_pdf()`: Descarga PDF oficial.
* `action_anular_boleta()` y `action_anular_boleta_path()`: Anulación de boletas.
* `cron_download_pending_pdfs()`: Placeholder para ejecución periódica.

---

## 🖥️ Vista en Odoo

* **Formulario de Boleta de Honorarios** incluye botones:

  * Emitir Boleta
  * Descargar PDF desde SII
  * Anular (legacy)
  * Anular por folio (nuevo método)

* **Statusbar de estados**: draft → processing → emitted → downloaded → cancelled/error

* **Iframe Preview**: muestra el PDF descargado dentro del formulario.

---

## 🔒 Seguridad

* Acceso otorgado a usuarios de grupo `base.group_user`.
* Permisos: Lectura, creación, escritura y borrado.

---

## 🛠️ Configuración

1. Ir a **Ajustes > Configuración**.
2. Completar los campos:

   * API Key (`boleta_honorarios.simpleapi_api_key`)
   * Base URL (`boleta_honorarios.simpleapi_base_url`)
   * Timeout (`boleta_honorarios.simpleapi_timeout`)

---

## 📌 Notas técnicas

* El RUT es validado con algoritmo de módulo 11. //Desde SimpleAPI
* Logs enmascaran API Keys para seguridad (`_mask_key`).
* Envío automático de correo al receptor si está configurado.

---

## 🧩 Requisitos

* Odoo 18
* Dependencia de librerías Python:

  * `requests`
  * `base64`
  * `logging`
  * `json`