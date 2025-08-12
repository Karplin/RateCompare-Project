# Proyecto RateCompare - Documentación de Cumplimiento de Requisitos

## Descripción General del Proyecto
**RateCompare** es un servicio de comparación de tasas de cambio bancarias que consulta múltiples APIs de tasas de cambio de divisas y selecciona la mejor oferta para remesas.

## Verificación de Cumplimiento de Requisitos

### 1. Requisitos del Concepto Principal

#### **Comparación de Tasas de Cambio para Clientes Bancarios**
- **Implementación**: El servicio compara tasas de 3 APIs diferentes (API1, API2, API3)
- **Ubicación**: `common/services/exchange_service.py` - Lógica principal de comparación
- **Función**: Método `get_best_exchange_rate()` consulta todas las APIs y selecciona el monto de conversión más alto

#### **Entrada del Proceso: Un Conjunto de Datos**
- **Formato**: `{source_currency, target_currency, amount}`
- **Ubicación**: `common/models/request.py` - Modelo `ExchangeRequest`
- **Validación**: Validación integral para divisas y montos
- **Divisas Soportadas**: 30+ divisas principales (USD, EUR, GBP, JPY, etc.)

#### **Múltiples APIs con Diferentes Firmas**
- **API1 (JSON)**: `{from, to, value}` → `{rate}`
- **API2 (XML)**: `<XML><From/><To/><Amount/></XML>` → `<XML><Result/></XML>`
- **API3 (JSON)**: `{exchange: {sourceCurrency, targetCurrency, quantity}}` → `{statusCode, message, data: {total}}`

#### **Salida del Proceso: Mejor Monto de Conversión**
- **Implementación**: `common/services/exchange_service.py` - `get_best_exchange_rate()`
- **Selección**: Selecciona automáticamente el `convertedAmount` más alto de todas las respuestas exitosas
- **Formato de Respuesta**: Respuesta unificada con la mejor oferta y datos de comparación

### 2. Requisitos Técnicos

#### **No se Espera Interfaz de Usuario**
- **Implementación**: Arquitectura de microservicios usando FastAPI
- **Ubicación**: 
  - API Gateway: `services/api-gateway/app/main.py` y `services/api-gateway/app/api/endpoints.py`
  - Servicios individuales: `services/{api1,api2,api3,exchange-service}/app/main.py`
- **Documentación**: Documentación de API auto-generada en `/docs` y `/redoc` para cada servicio

#### **No se Requiere SQL**
- **Implementación**: Proveedores simulados en memoria con tasas de cambio de ejemplo
- **Ubicación**: `common/providers/` - Los tres proveedores de API usan datos simulados

#### **Debe Tener Pruebas Unitarias**
- **Cobertura de Pruebas**: Pruebas unitarias integrales para todos los componentes
- **Ubicación**: Directorio `tests/unit/`
- **Pruebas Principales**:
  - `test_exchange_service.py` - Lógica del servicio e integración de proveedores
  - `test_models.py` - Validación de datos y serialización
  - `test_providers.py` - Funcionalidad individual de proveedores de API
- **Ejecutor de Pruebas**: `tests/run_tests.py` para ejecución fácil

#### **Debe Funcionar con APIs No Disponibles/Inválidas**
- **Resiliencia**: `common/services/exchange_service.py` - `asyncio.gather()` con `return_exceptions=True`
- **Manejo de Errores**: Mensaje personalizado cuando las APIs fallan
- **Lógica de Respaldo**: El servicio continúa funcionando con los proveedores disponibles

#### **Buenas Prácticas Esperadas**

##### **Arquitectura Limpia**
- **Separación de Responsabilidades**:
  - `common/models/` - Estructuras de datos y validación (compartido)
  - `common/providers/` - Integraciones de APIs externas (compartido)
  - `common/services/` - Lógica de negocio (compartido)
  - `services/*/app/api/` - Interfaces HTTP específicas por servicio
  - `common/utils/` - Utilidades compartidas
  - `common/config/` - Gestión de configuración (compartido)

##### **Principios SOLID**
- **Responsabilidad Única**: Cada clase tiene un propósito claro
- **Abierto/Cerrado**: Fácil agregar nuevos proveedores sin modificar código existente
- **Sustitución de Liskov**: Todos los proveedores implementan la misma interfaz
- **Segregación de Interfaces**: Interfaces limpias y enfocadas
- **Inversión de Dependencias**: El servicio depende de abstracciones, no de concreciones

##### **Registro de Actividad (Logging)**
- **Implementación**: `common/utils/logger.py` - Sistema de registro estructurado
- **Configuración**: `common/config/settings.py` - Niveles de registro configurables
- **Cobertura**: Todas las operaciones principales registradas con niveles apropiados

##### **Manejo de Errores**
- **Validación**: Modelos Pydantic con validación integral
- **Errores HTTP**: Códigos de estado HTTP apropiados y mensajes de error
- **Degradación Elegante**: El servicio continúa funcionando con fallas parciales

### 3. Detalles de Implementación de APIs

#### **API1 (Proveedor JSON)**
- **Ubicación**: `common/providers/api1_provider.py`
- **Servicio**: `services/api1/` - Microservicio independiente en puerto 8002
- **Formato de Entrada**: `{from, to, value}`
- **Formato de Salida**: `{rate}`
- **Características**: Variaciones aleatorias de tasas, simulación asíncrona

#### **API2 (Proveedor XML)**
- **Ubicación**: `common/providers/api2_provider.py`
- **Servicio**: `services/api2/` - Microservicio independiente en puerto 8003
- **Formato de Entrada**: XML con etiquetas `<From>`, `<To>`, `<Amount>`
- **Formato de Salida**: XML con etiqueta `<Result>`
- **Características**: Manejo nativo de XML, conversión bidireccional

#### **API3 (Proveedor JSON Anidado)**
- **Ubicación**: `common/providers/api3_provider.py`
- **Servicio**: `services/api3/` - Microservicio independiente en puerto 8004
- **Formato de Entrada**: `{exchange: {sourceCurrency, targetCurrency, quantity}}`
- **Formato de Salida**: `{statusCode, message, data: {total}}`
- **Características**: Respuesta estructurada con códigos de estado

### 4. Tecnología de Contenedores

#### **Implementación Docker**
- **Arquitectura**: Microservicios con contenedores independientes
- **API Gateway**: `services/api-gateway/Dockerfile` - Servicio principal en puerto 8000
- **Exchange Service**: `services/exchange-service/Dockerfile` - Servicio de comparación en puerto 8001
- **APIs Individuales**: `services/{api1,api2,api3}/Dockerfile` - Microservicios independientes
- **Despliegue Individual**: Cada servicio tiene su propio `docker-compose.yml`

### 6. Cumplimiento de Estructura del Proyecto

#### **Desarrollo Independiente**
- **Autocontenido**: Sin dependencias externas más allá de la biblioteca estándar de Python
- **Datos Simulados**: Tasas de cambio de ejemplo para pruebas inmediatas
- **Arquitectura Clara**: Fácil de entender y modificar

## Resumen de Cumplimiento

| Requisito |  Ubicación de Implementación | Notas                           |
|-----------|------------------------------|---------------------------------|
| Comparación de Tasas de Cambio |  `common/services/exchange_service.py` | Lógica de negocio principal     |
| Soporte Múltiples APIs |  `common/providers/` + `services/{api1,api2,api3}/` | 3 microservicios independientes |
| Sin Interfaz de Usuario |  Servicio REST FastAPI | API pura de backend             |
| Sin SQL |  Proveedores simulados | Datos en memoria                |
| Pruebas Unitarias |  `tests/unit/` | Cobertura integral              |
| Resiliencia de API |  Manejo de errores + respaldos | Errores Personalizados          |
| Arquitectura Limpia | Estructura de microservicios + `common/` | Principios SOLID                |
| Registro de Actividad |  `common/utils/logger.py` | Registro estructurado           |
| Manejo de Errores |  Validación + errores HTTP | Cobertura integral              |
| Rendimiento |  Llamadas asíncronas + concurrentes | Ejecución paralela              |
| Contenedores |  Microservicios Docker + Compose | Escalabilidad independiente     |
| Documentación |  Auto-generada + README | Cobertura completa              |

#
