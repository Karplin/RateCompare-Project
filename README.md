# RateCompare API - Banking Exchange Rate Comparison Service

RateCompare es una API que compara tasas de cambio de divisas de múltiples proveedores y devuelve la mejor oferta
disponible. El sistema está diseñado como microservicios usando Docker para máxima escalabilidad y flexibilidad.

## Características Principales

- **Comparación de tasas** de múltiples proveedores de APIs
- **Arquitectura de microservicios** con Docker
- **Múltiples formatos de API** (JSON, XML, Nested JSON)
- **Validación robusta** de monedas y montos
- **Logging detallado** para debugging y monitoreo
- **Health checks** automáticos
- **Documentación automática** con Swagger/OpenAPI

## Arquitectura del Sistema

### Estructura de Microservicios

```
RateCompare-Project/
├── services/                    # Microservicios independientes
│   ├── api-gateway/            # API Gateway principal
│   │   ├── app/
│   │   │   ├── api/endpoints.py    # Rutas del gateway
│   │   │   └── main.py            # Aplicación FastAPI
│   │   ├── Dockerfile             # Imagen
│   │   ├── docker-compose.yml     # Despliegue
│   │   └── requirements.txt       # Dependencias
│   ├── exchange-service/       # Servicio de comparación
│   │   ├── app/
│   │   │   ├── api/endpoints.py
│   │   │   └── main.py
│   │   ├── Dockerfile
│   │   ├── docker-compose.yml
│   │   └── requirements.txt
│   ├── api1/                  # API1 - Formato JSON
│   │   ├── app/
│   │   │   ├── api/endpoints.py
│   │   │   └── main.py
│   │   ├── Dockerfile
│   │   ├── docker-compose.yml
│   │   └── requirements.txt
│   ├── api2/                  # API2 - Formato XML
│   │   ├── app/
│   │   │   ├── api/endpoints.py
│   │   │   └── main.py
│   │   ├── Dockerfile
│   │   ├── docker-compose.yml
│   │   └── requirements.txt
│   └── api3/                  # API3 - JSON anidado
│       ├── app/
│       │   ├── api/endpoints.py
│       │   └── main.py
│       ├── Dockerfile
│       ├── docker-compose.yml
│       └── requirements.txt
├── common/                    # Código compartido entre servicios
│   ├── models/               # Modelos Pydantic (request, response)
│   ├── providers/            # Proveedores de APIs externas
│   ├── services/             # Lógica de negocio
│   ├── utils/                # Utilidades (logger, etc.)
│   └── config/               # Configuración

├── tests/                     # Pruebas unitarias
├── docker-compose.yml         # Orquestación completa
└── requirements.txt           # Dependencias base del proyecto
```

### Microservicios

- **API Gateway** (Puerto 8000): Punto de entrada principal con todos los servicios
- **Exchange Service** (Puerto 8001): Servicio especializado en comparación de tasas
- **API1** (Puerto 8002): Microservicio independiente con formato JSON
- **API2** (Puerto 8003): Microservicio independiente con formato XML
- **API3** (Puerto 8004): Microservicio independiente con formato JSON anidado

## Requisitos Previos

- Python 3.9+
- Docker y Docker Compose
- Git

## Inicio Rápido

```bash
# 1. Desplegar el API Gateway (incluye todos los servicios)
cd services/api-gateway
docker-compose up -d --build
cd ../..

# 2. Verificar que todo funciona
docker-compose ps

# 3. Probar el endpoint principal
curl -X POST "http://localhost:8000/exchange/compare" \
  -H "Content-Type: application/json" \
  -d '{"source_currency": "USD", "target_currency": "EUR", "amount": 100.00}'

# 4. Ejecutar pruebas unitarias
make test

# 5. Detener todos los servicios
cd services/api-gateway
docker-compose down
cd ../..
```

### Comandos Individuales de Prueba

```bash
# Probar endpoints individuales
curl -X POST "http://localhost:8000/exchange/rate/api1" \
  -H "Content-Type: application/json" \
  -d '{"from": "USD", "to": "EUR", "value": 100.00}'

curl -X POST "http://localhost:8000/exchange/rate/api2" \
  -H "Content-Type: application/xml" \
  -d '<XML><From>USD</From><To>EUR</To><Amount>100.00</Amount></XML>'

curl -X POST "http://localhost:8000/exchange/rate/api3" \
  -H "Content-Type: application/json" \
  -d '{"exchange": {"sourceCurrency": "USD", "targetCurrency": "EUR", "quantity": 100.00}}'

# Verificar que los servicios responden
curl http://localhost:8000/
curl http://localhost:8001/
curl http://localhost:8002/
curl http://localhost:8003/
curl http://localhost:8004/
```

## Endpoints de la API

### API Gateway (Puerto 8000) - Todos los endpoints

#### Comparar Tasas de Cambio

```http
POST /exchange/compare
Content-Type: application/json

{
    "source_currency": "USD",
    "target_currency": "EUR",
    "amount": 100.00
}
```

#### Obtener Tasa de API1 (JSON)

```http
POST /exchange/rate/api1
Content-Type: application/json

{
    "from": "USD",
    "to": "EUR",
    "value": 100.00
}
```

#### Obtener Tasa de API2 (XML)

```http
POST /exchange/rate/api2
Content-Type: application/xml

<XML>
    <From>USD</From>
    <To>EUR</To>
    <Amount>100.00</Amount>
</XML>
```

#### Obtener Tasa de API3 (Nested JSON)

```http
POST /exchange/rate/api3
Content-Type: application/json

{
    "exchange": {
        "sourceCurrency": "USD",
        "targetCurrency": "EUR",
        "quantity": 100.00
    }
}
```

### Microservicios y Puertos

| Puerto | Microservicio    | Descripción              | Acceso Individual            |
|--------|------------------|--------------------------|------------------------------|
| 8000   | API Gateway      | Punto de entrada principal | Todos los endpoints         |
| 8001   | Exchange Service | Comparación de tasas     | POST /exchange/compare      |
| 8002   | API1 Service     | Formato JSON             | POST /exchange/rate         |
| 8003   | API2 Service     | Formato XML              | POST /exchange/rate         |
| 8004   | API3 Service     | JSON anidado             | POST /exchange/rate         |

## Monedas Soportadas

El sistema soporta las siguientes monedas:
USD, EUR, GBP, JPY, CHF, CAD, AUD, NZD, SEK, NOK, DKK, PLN, CZK, HUF, RUB, CNY, HKD, SGD, KRW, INR, BRL, MXN, ZAR, TRY,
ILS, AED, SAR, QAR, KWD, BHD

## Gestión de Servicios

### Comandos de Despliegue

```bash
# Desplegar todos los servicios (a través del API Gateway)
cd services/api-gateway
docker-compose up -d --build
cd ../..

# Desplegar servicios individuales
cd services/api-gateway && docker-compose up -d --build && cd ../..
cd services/exchange-service && docker-compose up -d --build && cd ../..
cd services/api1 && docker-compose up -d --build && cd ../..
cd services/api2 && docker-compose up -d --build && cd ../..
cd services/api3 && docker-compose up -d --build && cd ../..

# Gestión de servicios
docker-compose down               # Detener todos
docker-compose ps                 # Ver estado
docker-compose logs -f            # Ver logs
docker-compose down -v --remove-orphans && docker system prune -af  # Limpiar contenedores
```

### Ver Estado de Servicios

```bash
docker-compose ps
```

### Ver Logs

```bash
# Todos los servicios
docker-compose logs -f

# Servicio específico (desde el directorio del servicio)
cd services/api-gateway && docker-compose logs -f
cd services/exchange-service && docker-compose logs -f
cd services/api1 && docker-compose logs -f
cd services/api2 && docker-compose logs -f
cd services/api3 && docker-compose logs -f
```

## Desarrollo y Pruebas

### Ejecutar Pruebas Unitarias

```bash
make test
# o
python3 tests/run_tests.py
```

### Construir Imágenes Docker

```bash
make build
```

### Limpiar Docker

```bash
make clean
```

## Configuración

### Variables de Entorno

```bash
LOG_LEVEL=INFO              # Nivel de logging
```

### Puertos por Defecto

- 8000: API Gateway
- 8001: Exchange Compare
- 8002: API1
- 8003: API2
- 8004: API3

## Seguridad
- Health checks verifican la funcionalidad
- Logs se mantienen dentro de los contenedores

## Documentación de la API

Una vez desplegado, puedes acceder a:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Estructura de Respuestas

### Respuesta de Comparación

```json
{
  "statusCode": 200,
  "message": "Exchange comparison completed successfully. Best rate from API2: 0.875",
  "data": {
    "bestOffer": {
      "sourceCurrency": "USD",
      "targetCurrency": "EUR",
      "amount": 100.00,
      "convertedAmount": 87.50,
      "rate": 0.875,
      "provider": "API2",
      "responseTimeMs": 150
    },
    "allOffers": [
      ...
    ],
    "totalProvidersQueried": 3,
    "successfulProviders": 3,
    "failedProviders": 0
  }
}
```
#
