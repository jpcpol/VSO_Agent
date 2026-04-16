# SSPA Aural-Syncro — Manual de Operaciones SOC (Centro de Operaciones de Seguridad)

Este documento detalla el proceso de despliegue, gestión y mantenimiento del Stack Central del SOC bajo el dominio `aural-syncro.com.ar`.

## 1. Arquitectura del Stack SOC
El SOC es un ecosistema de microservicios orquestados mediante **Docker Compose** y blindados con **Docker Secrets**.

### Componentes Críticos
- **Base de Datos**: PostgreSQL 15 + TimescaleDB (Métricas e Incidentes).
- **Mensajería**: Mosquitto MQTT (Bus de eventos tiempo real).
- **Caché/Estado**: Redis (Máquina de estados y Pub/Sub).
- **Core API**: Management Platform (FastAPI) + CRM API (Billing/Tenants).
- **Seguridad**: WireGuard (VPN) + WireGuard HA (Backhaul Nodos).
- **Observabilidad**: Zabbix 7.0 + Prometheus + Grafana.

---

## 2. Despliegue Inicial (Zero-Touch)

Para levantar el SOC por primera vez, utilice la herramienta de orquestación `construct.py`.

### Requisitos Previos
- Docker y Docker Compose instalados.
- Dominio `aural-syncro.com.ar` configurado en Cloudflare/DNS.
- Módulo `wireguard` cargado en el kernel del host.

### Pasos de Instalación
1. Navegue al directorio del orquestador:
   ```bash
   cd construct
   ```
2. Inicie el asistente de configuración:
   ```bash
   python construct.py
   ```
3. **Wizard de Configuración**:
   - Ingrese el dominio: `aural-syncro.com.ar`.
   - Configure las contraseñas maestras (PostgreSQL, Redis, MQTT).
   - Ingrese las llaves de **MercadoPago** y **Stripe**.
   - El script generará automáticamente el directorio `./infraestructura_soc/secrets/` y los archivos `.env`.

4. Levantar el stack:
   En el menú de `construct.py`, seleccione la opción **"Levantar Stack Completo"**.

---

## 3. Gestión de Secretos (Militar-Grade)
El sistema utiliza **Docker Secrets** para proteger credenciales.
- **Ubicación**: `infraestructura_soc/secrets/*.txt`.
- **Rotación**: Para rotar una clave, actualice el archivo `.txt` y reinicie el servicio correspondiente:
  ```bash
  python construct.py restart management_backend
  ```

---

## 4. Monitoreo y Alertas
### Zabbix 7.0
- **Acceso**: `https://zabbix.aural-syncro.com.ar`
- **Plantilla**: Utilice `zabbix_template_sspa.yaml` para importar los triggers de HA y Vision Engine.
- **Alertas Críticas**:
  - `sspa.wg.tunnel_up`: Alerta si un nodo pierde conexión VPN.
  - `sspa.pipeline.watchdog_trigger`: Alerta si una GPU de un nodo se bloquea.

### Grafana
- **Acceso**: `https://grafana.aural-syncro.com.ar`
- **Dashboards**: "SSPA Global Health" y "Tenant Resource Consumption".

---

## 5. Operaciones de Mantenimiento
El script `construct.py` provee herramientas integradas:
- **Backups**: Opción "Gestionar Backups" para exportar volúmenes de DB y Modelos AI.
- **Logs**: Opción "Ver logs en vivo" para depuración táctica.
- **Limpieza**: Opción "Pruning de Docker" para mantenimiento de espacio en disco.

---

## 6. URLs de Producción
- **Portal Institucional**: `https://aural-syncro.com.ar`
- **Panel de Gestión**: `https://admin.aural-syncro.com.ar`
- **API Core**: `https://api.aural-syncro.com.ar`
- **MLOps Lab**: `https://lab.aural-syncro.com.ar`

---

## 7. Despliegue del Portal Institucional (Standalone)
El portal institucional corre de forma independiente para no comprometer el SOC.

### Pasos de Despliegue:
1. Navegue al directorio institucional:
   ```bash
   cd institucional
   ```
2. Inicie el stack:
   ```bash
   docker-compose up -d
   ```
3. **Gestión de Correo (Mailcow)**:
   - Siga el manual oficial de Mailcow para la configuración del dominio `aural-syncro.com.ar`.
   - El stack institucional está preparado para integrarse con los puertos SMTP/IMAP de Mailcow.

### Chatbot Botpress:
- El portal incluye un widget pre-configurado que se conecta a la nube de Botpress.
- Para personalizar las respuestas, acceda al panel de Botpress Cloud con las credenciales del proyecto.
