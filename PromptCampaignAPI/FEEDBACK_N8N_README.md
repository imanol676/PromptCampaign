# Integración con n8n para Feedback de IA

## Descripción General

Este módulo proporciona endpoints para integrar tu API de PromptCampaign con n8n, permitiendo que un agente de IA analice las métricas de tus campañas y genere feedback automatizado.

## Flujo de Trabajo

```
API FastAPI → n8n Webhook → Agente IA → n8n procesa → API FastAPI (guarda feedback)
```

## Endpoints Disponibles

### 1. Enviar Métricas a n8n

**POST** `/feedbacks/send-to-n8n`

Envía las métricas de una campaña al workflow de n8n para análisis de IA.

#### Request Body

```json
{
  "campaign_id": 1,
  "metric_id": 5, // Opcional - si no se especifica, se usa la métrica más reciente
  "n8n_webhook_url": "https://tu-instancia-n8n.com/webhook/analizar-metricas"
}
```

#### Response

```json
{
  "success": true,
  "message": "Métricas enviadas exitosamente a n8n para análisis de IA",
  "campaign_id": 1,
  "metric_id": 5,
  "n8n_response_status": 200
}
```

#### Datos Enviados a n8n

El webhook de n8n recibirá el siguiente JSON:

```json
{
  "campaign_id": 1,
  "campaign_nombre": "Campaña Navidad 2024",
  "campaign_plataforma": "Google Ads",
  "metric_id": 5,
  "impresiones": 50000,
  "clicks": 2500,
  "conversiones": 125,
  "gasto_total": 1500.5,
  "fecha_registro": "2024-12-15",
  "ctr": 5.0, // Click Through Rate (%)
  "conversion_rate": 5.0, // Tasa de conversión (%)
  "cpc": 0.6, // Costo por Click
  "cpa": 12.0 // Costo por Adquisición
}
```

---

### 2. Recibir Feedback desde n8n

**POST** `/feedbacks/receive-from-n8n`

Recibe el feedback generado por la IA y lo guarda en la base de datos.

#### Request Body

```json
{
  "campaign_id": 1,
  "metric_id": 5,
  "texto_feedback": "La campaña muestra un excelente rendimiento con un CTR de 5% y una tasa de conversión del 5%. El CPA de $12 está dentro del rango objetivo. Se recomienda: 1) Aumentar el presupuesto en un 20% para capitalizar el buen rendimiento. 2) Realizar pruebas A/B en los anuncios de mejor rendimiento. 3) Considerar expandir a audiencias similares."
}
```

#### Response

```json
{
  "id": 10,
  "campaign_id": 1,
  "metric_id": 5,
  "texto_feedback": "La campaña muestra un excelente rendimiento..."
}
```

---

### 3. Obtener Feedbacks de una Campaña

**GET** `/feedbacks/campaign/{campaign_id}`

Obtiene todos los feedbacks generados para una campaña específica.

#### Response

```json
[
  {
    "id": 10,
    "campaign_id": 1,
    "metric_id": 5,
    "texto_feedback": "Feedback para métrica 5..."
  },
  {
    "id": 9,
    "campaign_id": 1,
    "metric_id": 4,
    "texto_feedback": "Feedback para métrica 4..."
  }
]
```

---

### 4. Obtener un Feedback Específico

**GET** `/feedbacks/{feedback_id}`

Obtiene un feedback por su ID.

---

### 5. Eliminar un Feedback

**DELETE** `/feedbacks/{feedback_id}`

Elimina un feedback específico.

---

## Configuración del Workflow en n8n

### Paso 1: Crear Webhook de Entrada

1. Añade un nodo **Webhook** en n8n
2. Configura el método: `POST`
3. Copia la URL del webhook generada
4. Esta URL será la que uses en `n8n_webhook_url`

### Paso 2: Procesar los Datos

Añade nodos para procesar las métricas recibidas. Ejemplo de estructura:

```
Webhook → Set Node (preparar datos) → AI Agent (OpenAI/Claude/etc) → HTTP Request (enviar feedback a API)
```

### Paso 3: Configurar el Agente de IA

Ejemplo de prompt para el agente de IA:

```
Analiza las siguientes métricas de campaña publicitaria y proporciona:

1. Evaluación del rendimiento general
2. Análisis de CTR y tasa de conversión
3. Evaluación de costos (CPC y CPA)
4. Recomendaciones específicas de optimización
5. Alertas sobre métricas que requieran atención

Datos de la campaña:
- Nombre: {{campaign_nombre}}
- Plataforma: {{campaign_plataforma}}
- Impresiones: {{impresiones}}
- Clicks: {{clicks}}
- Conversiones: {{conversiones}}
- Gasto Total: ${{gasto_total}}
- CTR: {{ctr}}%
- Conversion Rate: {{conversion_rate}}%
- CPC: ${{cpc}}
- CPA: ${{cpa}}

Proporciona un análisis detallado y profesional.
```

### Paso 4: Enviar Feedback de Vuelta

Añade un nodo **HTTP Request** con:

- **Method**: POST
- **URL**: `https://tu-api.com/feedbacks/receive-from-n8n`
- **Body**:

```json
{
  "campaign_id": "={{$node["Webhook"].json["campaign_id"]}}",
  "metric_id": "={{$node["Webhook"].json["metric_id"]}}",
  "texto_feedback": "={{$node["AI_Agent"].json["output"]}}"
}
```

---

## Ejemplo de Uso Completo

### 1. Desde tu aplicación frontend o backend:

```python
import httpx

async def analizar_campaña_con_ia(campaign_id: int):
    """Envía una campaña para análisis de IA"""

    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/feedbacks/send-to-n8n",
            json={
                "campaign_id": campaign_id,
                "n8n_webhook_url": "https://n8n.example.com/webhook/analizar-metricas"
            }
        )
        return response.json()

# Uso
resultado = await analizar_campaña_con_ia(1)
print(resultado)
```

### 2. El workflow de n8n procesa automáticamente

### 3. Obtener el feedback generado:

```python
async def obtener_feedbacks_de_campaña(campaign_id: int):
    """Obtiene todos los feedbacks de una campaña"""

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"http://localhost:8000/feedbacks/campaign/{campaign_id}"
        )
        return response.json()

# Uso
feedbacks = await obtener_feedbacks_de_campaña(1)
for feedback in feedbacks:
    print(f"Feedback ID {feedback['id']}: {feedback['texto_feedback']}")
```

---

## Métricas Calculadas Automáticamente

La API calcula automáticamente estas métricas derivadas:

- **CTR (Click Through Rate)**: `(clicks / impresiones) * 100`
- **Conversion Rate**: `(conversiones / clicks) * 100`
- **CPC (Cost Per Click)**: `gasto_total / clicks`
- **CPA (Cost Per Acquisition)**: `gasto_total / conversiones`

Estas métricas facilitan el análisis para el agente de IA.

---

## Requisitos

Asegúrate de tener instalado:

```bash
pip install httpx
```

---

## Consideraciones de Seguridad

1. **Validación de Webhook**: Considera añadir autenticación en los webhooks de n8n
2. **Rate Limiting**: Implementa límites de tasa para prevenir abuso
3. **Validación de Datos**: Los schemas Pydantic validan automáticamente los datos
4. **HTTPS**: Usa siempre HTTPS en producción para las URLs de webhook

---

## Errores Comunes

### Error 404 - Campaña no encontrada

```json
{
  "detail": "Campaña con id 999 no encontrada"
}
```

**Solución**: Verifica que el `campaign_id` existe en la base de datos.

### Error 503 - Error al comunicarse con n8n

```json
{
  "detail": "Error al comunicarse con n8n: Connection timeout"
}
```

**Solución**:

- Verifica que la URL del webhook de n8n es correcta
- Verifica que n8n está ejecutándose y accesible
- Revisa los logs de n8n para más detalles

### División por cero en métricas

La API maneja automáticamente casos donde:

- No hay impresiones → CTR = 0
- No hay clicks → Conversion Rate = 0, CPC = 0
- No hay conversiones → CPA = 0

---

## Testing

Puedes probar los endpoints usando la documentación interactiva de FastAPI:

```
http://localhost:8000/docs
```

O con curl:

```bash
# Enviar métricas a n8n
curl -X POST "http://localhost:8000/feedbacks/send-to-n8n" \
  -H "Content-Type: application/json" \
  -d '{
    "campaign_id": 1,
    "n8n_webhook_url": "https://n8n.example.com/webhook/test"
  }'
```

---

## Soporte

Para más información sobre la integración, consulta:

- [Documentación de n8n](https://docs.n8n.io)
- [FastAPI Documentation](https://fastapi.tiangolo.com)
