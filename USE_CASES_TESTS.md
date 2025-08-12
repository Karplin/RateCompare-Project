# Casos de Uso - Documentación de Pruebas

## Descripción General

Este documento describe todos los casos de uso cubiertos por las pruebas unitarias.

## 1. Pruebas del Servicio de Intercambio (`tests/unit/test_exchange_service.py`)

### **Caso de Uso 1: Selección de Mejor Tasa**

- **Método**: `test_service_selects_best_rate`
- **Propósito**: Verificar que el servicio selecciona automáticamente el proveedor que ofrece el monto convertido más
  alto
- **Escenario**:
    - API1 retorna: 85.0 EUR por 100 USD
    - API2 retorna: 87.5 EUR por 100 USD (mejor)
    - API3 retorna: 86.0 EUR por 100 USD
- **Resultado Esperado**:
    - El servicio selecciona API2 como la mejor oferta
    - Retorna statusCode 200
    - bestOffer.provider = "API2"
    - bestOffer.convertedAmount = 87.5
    - successfulProviders = 3, failedProviders = 0

### **Caso de Uso 2: Resiliencia ante Fallas Parciales**

- **Método**: `test_service_resilience_with_failures`
- **Propósito**: Demostrar que el sistema continúa funcionando cuando algunos proveedores fallan
- **Escenario**:
    - API1 funciona: 85.0 EUR
    - API2 falla: Exception "API unavailable"
    - API3 funciona: 86.0 EUR (mejor de los disponibles)
- **Resultado Esperado**:
    - El servicio selecciona API3 como mejor oferta disponible
    - successfulProviders = 2, failedProviders = 1
    - Sistema continúa operando normalmente

### **Caso de Uso 3: Falla Completa del Sistema**

- **Método**: `test_service_all_providers_fail`
- **Propósito**: Verificar el comportamiento cuando todos los proveedores fallan
- **Escenario**: Los 3 proveedores (API1, API2, API3) lanzan excepciones
- **Resultado Esperado**:
    - Se lanza ValueError con mensaje "All providers failed"
    - Sistema maneja la falla total

### **Caso de Uso 4: Manejo de Divisas No Soportadas**

- **Método**: `test_service_with_unsupported_currencies`
- **Propósito**: Verificar comportamiento con pares de divisas no disponibles
- **Escenario**: Solicitar conversión AED → QAR (no soportada por ningún proveedor)
- **Resultado Esperado**: ValueError con mensaje "All providers failed"

## 2. Pruebas de Modelos de Datos (`tests/unit/test_models.py`)

### **Caso de Uso 5: Creación Válida de Solicitud**

- **Método**: `test_valid_request_creation`
- **Propósito**: Verificar que las solicitudes válidas se crean correctamente
- **Escenario**: Crear ExchangeRequest con USD → EUR, monto 100.00
- **Resultado Esperado**:
    - Objeto creado exitosamente
    - Campos asignados correctamente
    - Validación aprobada

### **Caso de Uso 6: Validación de Divisas Inválidas**

- **Método**: `test_invalid_currency_validation`
- **Propósito**: Asegurar que divisas inválidas son rechazadas
- **Escenario**: Usar "INVALID" como divisa de origen
- **Resultado Esperado**: ValidationError es lanzado

### **Caso de Uso 7: Validación de Divisas Iguales**

- **Método**: `test_same_currency_validation`
- **Propósito**: Prevenir conversiones de la misma divisa
- **Escenario**: Solicitar conversión USD → USD
- **Resultado Esperado**: ValidationError es lanzado

### **Caso de Uso 8: Validación de Montos Negativos**

- **Método**: `test_negative_amount_validation`
- **Propósito**: Rechazar montos negativos o cero
- **Escenario**: Usar monto -100.00
- **Resultado Esperado**: ValidationError es lanzado

## 3. Pruebas de Proveedores (`tests/unit/test_providers.py`)

### **Caso de Uso 9: Funcionamiento API1 (Formato JSON)**

- **Método**: `test_api1_direct_provider_success`
- **Propósito**: Verificar que API1 retorna respuestas en formato correcto
- **Escenario**: Solicitud USD → EUR con 100.00
- **Resultado Esperado**:
    - Respuesta de tipo API1Response
    - Campo 'rate' presente y positivo
    - Tipo de dato Decimal

### **Caso de Uso 10: Funcionamiento API2 (Formato XML)**

- **Método**: `test_api2_direct_provider_success`
- **Propósito**: Verificar que API2 retorna respuestas en formato XML correcto
- **Escenario**: Solicitud USD → EUR con 100.00
- **Resultado Esperado**:
    - Respuesta de tipo API2Response
    - Campo 'Result' presente y positivo
    - Tipo de dato Decimal

### **Caso de Uso 11: Funcionamiento API3 (Formato JSON Anidado)**

- **Método**: `test_api3_direct_provider_success`
- **Propósito**: Verificar que API3 retorna respuestas en formato JSON anidado
- **Escenario**: Solicitud USD → EUR con 100.00, con reintentos para estabilidad
- **Resultado Esperado**:
    - Respuesta de tipo API3Response
    - statusCode = 200
    - data.total presente y positivo
    - Éxito en al menos 1 de 10 intentos

### **Caso de Uso 12: Manejo de Divisas No Soportadas por Proveedores**

- **Método**: `test_providers_handle_unsupported_currencies`
- **Propósito**: Verificar que cada proveedor maneja apropiadamente pares no soportados
- **Escenario**: Solicitar AED → QAR en los 3 proveedores
- **Resultado Esperado**: Cada proveedor lanza ValueError

### **Caso de Uso 13: Precisión de Formatos de Respuesta**

- **Método**: `test_response_format_accuracy`
- **Propósito**: Asegurar que las respuestas cumplen exactamente con las especificaciones
- **Escenario**: Verificar estructura exacta de respuestas API1 y API2
- **Resultado Esperado**:
    - API1: tiene 'rate', no tiene 'converted_amount'
    - API2: tiene 'Result', no tiene 'rate'

## Fixtures de Pruebas

### **Datos de Prueba Estándar**

- **sample_request**: USD → EUR, 100.00 (caso típico)
- **unsupported_request**: AED → QAR, 100.00 (caso no soportado)
- **api1_sample_request**: Formato específico API1
- **api2_sample_request**: Formato específico API2
- **api3_sample_request**: Formato específico API3

## Cobertura de Requisitos

### **Aspectos de Calidad Cubiertos:**

- **Robustez**: Manejo de fallas y excepciones
- **Precisión**: Validación exacta de formatos
- **Confiabilidad**: Múltiples escenarios y reintentos
- **Usabilidad**: Validación de entrada para prevenir errores

## Estadísticas de Pruebas

- **Total de casos de uso**: 13
- **Pruebas síncronas**: 4 (modelos y validaciones)
- **Pruebas asíncronas**: 9 (servicios y proveedores)
- **Casos de éxito**: 8
- **Casos de falla controlada**: 5
- **Cobertura de formatos**: 100% (JSON, XML, JSON anidado)

#
