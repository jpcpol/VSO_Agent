# SSPA Aural-Syncro — Manual de Operaciones de Nodo Edge

Este documento detalla el proceso de instalación y mantenimiento de los Nodos de Visión en campo para el ecosistema `aural-syncro.com.ar`.

## 1. Arquitectura del Nodo Edge
El nodo es una unidad autónoma de procesamiento AI que se conecta al SOC mediante un túnel seguro.

### Componentes
- **Vision Engine**: Motor C++20 (YOLOv10 + YAMNet) con aceleración TensorRT.
- **Watchdog**: Servicio Systemd que monitorea la conexión VPN y realiza Failover HA.
- **WireGuard**: Cliente VPN para comunicación con el SOC.

---

## 2. Instalación en Campo (Provisioning)

Utilice la herramienta `node_construct.py` ubicada en el directorio `vision_engine`.

### Requisitos de Hardware
- NVIDIA Jetson (Orin Nano/NX) o PC con GPU RTX (Arquitectura Ada Lovelace recomendada).
- Ubuntu 22.04 LTS con NVIDIA Container Toolkit.
- Conexión a Internet (puerto UDP 51820 de salida permitido).

### Pasos de Instalación
1. Clonar el repositorio en el nodo:
   ```bash
   git clone <URL_REPOSITORIO>
   cd vision_engine
   ```
2. Iniciar el asistente de despliegue:
   ```bash
   python node_construct.py
   ```
3. **Wizard de Configuración**:
   - **ID de Nodo**: Ej. `nodo_buenos_aires_01`.
   - **Gateways del SOC**: Ingrese la lista separada por comas (ej. `gw1.aural-syncro.com.ar:51820, gw2.aural-syncro.com.ar:51820`).
   - **URLs RTSP**: Direcciones de las cámaras IP (hasta 4).
   - **SOC API Token**: Llave JWT obtenida desde el panel administrativo.

4. **Desplegar**: Seleccione la opción **"Deploy completo"** para construir la imagen AI y levantar los servicios.

---

## 3. Gestión del Watchdog (Failover HA)
El Watchdog asegura que el nodo siempre esté conectado al SOC más cercano o disponible.

- **Instalación**: Use el menú "Watchdog (Systemd)" en `node_construct.py` para instalar el servicio.
- **Comandos Útiles**:
  ```bash
  sudo systemctl status sspa-watchdog
  sudo journalctl -u sspa-watchdog -f
  ```
- **Lógica de Failover**: Si el ping al SOC falla por más de 30s, el Watchdog rotará automáticamente al siguiente Gateway de la lista configurada.

---

## 4. Monitoreo Local y Remoto
### Zabbix Agent 2
El nodo reporta automáticamente al SOC:
- Uso de GPU/CPU y temperatura.
- Latencia del túnel VPN.
- Estado de la captura de audio (ALSA).

### Logs de Visión
Para depurar detecciones en tiempo real:
```bash
docker logs -f sspa_vision_engine
```

---

## 5. Actualización de Modelos AI
El SOC puede enviar nuevos pesos de modelos (.engine/.onnx).
1. El nodo descarga el modelo desde MinIO.
2. `node_construct.py` permite verificar la integridad mediante la opción **"Calcular SHA-256 del modelo"**.
3. Reinicie el motor: `python node_construct.py` -> Opción **"Reiniciar Vision Engine"**.

---

## 6. Resolución de Problemas Frecuentes
- **VPN Caída**: Verifique que el servicio `wg-quick@wg0` esté activo y que las llaves pública/privada coincidan con las del SOC.
- **GPU no detectada**: Ejecute `nvidia-smi` en el host. Si no responde, revise los drivers del kernel.
- **Fallo de Audio**: Asegúrese de que el usuario de Docker tenga permisos sobre `/dev/snd`.
