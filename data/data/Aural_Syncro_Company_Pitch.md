# Aural-Syncro — Company & Products Pitch
**Versión:** 1.18.2 · Abril 2026  
**Empresa:** Aural-Syncro · San Juan, Argentina  
**Dominio:** aural-syncro.com.ar  
**Registro legal:** DNDA EX-2026-21285835-APN-DNDA#MJ

---

## ¿Quiénes somos? / Who We Are

Aural-Syncro es una empresa de investigación y desarrollo de inteligencia artificial aplicada, fundada en 2024 en San Juan, Argentina. Nuestra filosofía es procesar los datos donde se generan — en el borde de la red — eliminando la dependencia de servidores en la nube para lograr respuestas en tiempo real con evidencia forense inmutable.

Trabajamos en tres frentes simultáneos: seguridad perimetral con SSPA, diagnóstico predictivo de enfermedades crónicas con Endo-Edge LAB+, y productividad de desarrollo de software con nuestro Asistente Multimodal Agéntico. Los tres productos comparten el mismo núcleo tecnológico: inteligencia artificial de alto rendimiento ejecutándose completamente on-premise.

---

*Aural-Syncro is an applied artificial intelligence R&D company, founded in 2024 in San Juan, Argentina. Our philosophy is to process data where it is generated — at the network edge — eliminating cloud dependency to achieve real-time responses with immutable forensic evidence.*

*We work on three simultaneous fronts: perimeter security with SSPA, predictive diagnosis of chronic diseases with Endo-Edge LAB+, and software development productivity with our Agentic Multimodal Assistant. All three products share the same technological core: high-performance AI running entirely on-premise.*

---

## Producto 1 — SSPA (Security System Perception & Automation)

### ¿Qué es SSPA?

SSPA es una plataforma de vigilancia proactiva de grado industrial y militar. A diferencia de los sistemas de seguridad tradicionales que dependen de la observación humana constante, SSPA utiliza **True Edge AI** para transformar cámaras y micrófonos comunes en agentes inteligentes autónomos capaces de detectar, analizar y responder a amenazas en tiempo real — sin intervención humana permanente y sin depender de la nube.

El sistema está certificado bajo el estándar DDA (Deployment, Development & Architecture) y registrado bajo DNDA Argentina.

---

*SSPA is an industrial and military-grade proactive surveillance platform. Unlike traditional security systems that rely on constant human observation, SSPA uses True Edge AI to transform standard cameras and microphones into autonomous intelligent agents capable of detecting, analyzing, and responding to threats in real time — without permanent human intervention and without cloud dependency.*

---

### Capacidades principales / Core Capabilities

**Detección visual (Vision Engine)**
- Identifica personas, vehículos, objetos sospechosos en flujos de video RTSP en tiempo real
- Motor YOLOv10 acelerado por TensorRT en hardware NVIDIA — latencia de inferencia < 25ms por frame
- Soporta hasta 50 cámaras simultáneas según el hardware del nodo

**Detección acústica (Audio Engine)**
- Clasifica eventos sonoros críticos: disparos, explosiones, rotura de vidrio, sirenas, gritos, alarmas
- Motor PANNs CNN14 con análisis continuo del entorno — 527 clases de audio detectables
- Análisis paralelo e independiente del motor visual

**Fusión sensorial**
- Cuando el motor visual y el auditivo detectan simultáneamente un evento correlacionado (ej. sujeto + disparo), el sistema escala automáticamente a nivel CRÍTICO y activa el protocolo de respuesta inmediata

**Control IoT en tiempo real**
- Activa actuadores Tasmota conectados: sirenas, luces estroboscópicas, portones, cerraduras electromagnéticas
- Ciclo detección → respuesta IoT: < 200ms

**Evidencia forense inmutable**
- Almacenamiento de imágenes e incidentes con política WORM (Write Once Read Many)
- Cada evidencia lleva firma SHA-256 y acta de custodia forense compatible con los arts. 236 y 236 bis del CPPN
- Acceso auditado mediante URLs pre-firmadas con tiempo de expiración

**Notificaciones tácticas**
- Alertas en tiempo real por Telegram con imagen del incidente, nivel de confianza, cámara origen y opciones de acción remota
- Tiempo de alerta desde detección: < 2 segundos

**Panel de operaciones SOC**
- Dashboard web en tiempo real para gestionar nodos, incidentes, suscripciones y usuarios
- Acceso con autenticación de dos factores (TOTP) + cookie de sesión auditada
- Audit log completo de accesos y acciones

---

### Arquitectura y diferencial tecnológico / Architecture & Technical Differentiator

SSPA opera en tres capas distribuidas:

1. **Nodo Edge (hardware físico en el sitio protegido):** Vision Engine + Audio Engine + Event Router + IoT Gateway corren directamente en hardware NVIDIA Jetson Orin. Sin nube. Sin latencia de red externa.

2. **Transporte seguro:** Los nodos se conectan al SOC mediante VPN WireGuard (cifrado ChaCha20-Poly1305 / Curve25519) con failover automático en < 30 segundos ante pérdida de conectividad.

3. **SOC (servidor central):** Panel de gestión, base de datos de incidentes, facturación, almacenamiento forense y observabilidad operacional.

**Diferencial clave:** Todo el procesamiento de IA ocurre en el nodo físico, en el lugar donde están las cámaras. El SOC solo recibe los resultados. Esto garantiza respuestas sub-50ms incluso con conectividad intermitente.

---

*SSPA operates on three distributed layers: Edge Node (physical hardware on-site running AI inference), Secure Transport (WireGuard VPN with automatic failover), and SOC (management, billing, forensic storage, and observability). The key differentiator: all AI processing happens on the physical node where the cameras are — the SOC only receives results, guaranteeing sub-50ms responses even with intermittent connectivity.*

---

### Planes comerciales / Commercial Plans

| Plan | USD/mes | Cámaras | Micrófonos | Hardware recomendado |
|---|---|---|---|---|
| Starter | $149 | hasta 8 | hasta 4 | Jetson Orin NX 8GB |
| Standard | $299 | hasta 16 | hasta 8 | Jetson Orin NX 16GB |
| Professional | $499 | hasta 32 | hasta 16 | Jetson AGX Orin 32GB |
| Enterprise | $899 | hasta 50 | hasta 20 | Jetson AGX Orin 64GB |

Gateways de pago disponibles: **MercadoPago** (ARS, Checkout Pro) y **Stripe** (USD, Sessions).  
Arquitectura multi-tenant: cada cliente tiene sus datos y facturación completamente aislados.

---

### Sectores objetivo / Target Sectors

- **Gobierno y Defensa:** Fronteras, instalaciones estratégicas, fuerzas de seguridad
- **Infraestructura crítica:** Centrales energéticas, plantas nucleares, centros de datos, subestaciones eléctricas
- **Aeropuertos:** Control perimetral de pistas y terminales
- **Industria:** Plantas de manufactura, complejos logísticos
- **Sector privado:** Barrios cerrados, complejos corporativos, universidades, hospitales

---

### SLAs validados en producción / Production-validated SLAs

| Componente | SLA garantizado |
|---|---|
| Inferencia visual (por frame) | < 25ms |
| Routing de eventos (p95) | < 50ms |
| Notificación Telegram desde detección | < 2s |
| Dashboard WebSocket | < 100ms |
| Recuperación WireGuard ante caída | < 30s |
| Comando IoT → actuación física | < 200ms |

---

## Producto 2 — Endo-Edge LAB+

### ¿Qué es Endo-Edge LAB+?

Endo-Edge LAB+ es una plataforma de diagnóstico predictivo temprano de enfermedades crónicas. Integra datos continuos de dispositivos wearable (ECG, glucómetro continuo CGM, respuesta galvánica de la piel GSR) con el historial longitudinal de laboratorio clínico del paciente en un marcador unificado de tendencia de riesgo denominado **RTM (Risk Trend Marker)**.

El RTM permite anticipar el desarrollo de patologías crónicas —Diabetes Tipo 2, Hipotiroidismo, Síndrome Metabólico— con una ventana de **2 a 5 años de anticipación** respecto al diagnóstico convencional.

**Características técnicas:**
- Arquitectura 100% on-premise bajo estándar **HAPI FHIR R4** (interoperabilidad clínica internacional)
- Hardware de inferencia en el borde: **MAX78000** (procesamiento ultra-bajo consumo)
- Modelos LSTM para análisis de series temporales fisiológicas
- Diseñado bajo norma **ISO 14155:2020** (ensayos clínicos de dispositivos médicos)
- Co-investigadora médica: Dra. Alejandra Cicchitti
- Estado actual: **Investigación activa — Fase 1B** · Protocolo EE-2026-002

---

*Endo-Edge LAB+ is an early predictive diagnosis platform for chronic diseases. It integrates continuous wearable data (ECG, CGM, GSR) with longitudinal clinical lab history into a unified Risk Trend Marker (RTM), enabling anticipation of chronic conditions — T2 Diabetes, Hypothyroidism, Metabolic Syndrome — 2 to 5 years ahead of conventional diagnosis. Fully on-premise, HAPI FHIR R4 compliant, ISO 14155:2020 designed.*

---

## Producto 3 — Asistente Multimodal Agéntico para Desarrollo de Software

### ¿Qué es el Asistente Multimodal?

El Asistente Multimodal Agéntico es un sistema de inteligencia artificial on-premise diseñado para potenciar la productividad de equipos de desarrollo de software. Funciona con tres agentes especializados que colaboran entre sí:

- **Agente Arquitecto:** Diseña soluciones, toma decisiones técnicas de alto nivel y define la estructura del sistema
- **Agente Developer:** Genera, refactoriza y depura código en múltiples lenguajes
- **Agente QA & Sandbox:** Valida el código generado, ejecuta pruebas y detecta regresiones en un entorno aislado

**Características clave:**
- **100% on-premise:** el código y los datos del proyecto nunca salen de la infraestructura del cliente
- **Tiers de inteligencia dinámica:** el sistema selecciona automáticamente el modelo óptimo (Ligero / Balanceado / Potente) según la complejidad de la tarea, usando Ollama
- **PromptRegistry:** trazabilidad completa de cada generación de código — qué prompt generó qué resultado, cuándo y por qué
- Estado actual: **Release Candidate v3.0**

---

*The Agentic Multimodal Assistant is an on-premise AI system designed to boost software development team productivity. Three specialized agents collaborate: Architect (high-level design decisions), Developer (code generation and refactoring), and QA & Sandbox (validation and testing). Fully on-premise — client code never leaves their infrastructure.*

---

## Preguntas frecuentes / FAQ

**¿SSPA requiere conexión a internet permanente?**  
No. Todo el procesamiento de IA ocurre en el nodo edge físico. La conectividad a internet solo es necesaria para sincronización con el SOC y notificaciones Telegram. Ante pérdida de conectividad, el nodo continúa detectando y almacenando evidencia localmente.

*No. All AI processing happens on the physical edge node. Internet connectivity is only needed for SOC synchronization and Telegram notifications. In case of connectivity loss, the node continues detecting and storing evidence locally.*

---

**¿Qué pasa si el nodo pierde conexión con el SOC?**  
El servicio WireGuard Watchdog detecta la pérdida en menos de 30 segundos y realiza failover automático a un gateway redundante. Si no hay gateway disponible, el nodo opera en modo autónomo local.

*The WireGuard Watchdog service detects the loss in under 30 seconds and automatically fails over to a redundant gateway. If no gateway is available, the node operates in local autonomous mode.*

---

**¿Cómo se protege la evidencia contra manipulación?**  
Cada evidencia forense se almacena con política WORM (inmutable desde el momento del almacenamiento) y firma SHA-256. El sistema genera automáticamente un acta de custodia forense compatible con el Código Procesal Penal de la Nación Argentina (arts. 236 y 236 bis).

*Each forensic evidence file is stored with WORM policy (immutable from the moment of storage) and SHA-256 signature. The system automatically generates a forensic chain-of-custody certificate compliant with Argentine national procedural law.*

---

**¿Cómo contacto al equipo de Aural-Syncro?**  
Por email: **juanpablo.chancay@aural-syncro.com.ar**  
Sitio web: **aural-syncro.com.ar**  
Ubicación: San Juan, Argentina

*By email: juanpablo.chancay@aural-syncro.com.ar · Website: aural-syncro.com.ar · Location: San Juan, Argentina*

---

*Aural-Syncro — San Juan, Argentina — aural-syncro.com.ar*  
*DNDA EX-2026-21285835-APN-DNDA#MJ | © 2026 Juan Pablo Chancay*
