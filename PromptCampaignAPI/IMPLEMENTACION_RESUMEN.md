# 🎯 Resumen de Implementación: Integración con n8n para Feedback de IA

## ✅ Cambios Realizados

### 1. **Modelos Actualizados**

- ✓ `models/campaign.py` - Agregada relación `feedbacks`
- ✓ `models/metric.py` - Agregada relación `feedbacks`
- ✓ `models/feedback.py` - Ya existía con relaciones correctas

### 2. **Nuevos Schemas Creados**

- ✓ `schemas/n8n_schema.py` - Schemas para integración con n8n:
  - `MetricDataForAI` - Datos enviados a n8n con métricas calculadas
  - `SendMetricsToN8nRequest` - Request para enviar métricas
  - `ReceiveFeedbackFromN8n` - Feedback recibido de n8n
  - `SendMetricsResponse` - Respuesta del envío

### 3. **Endpoints Implementados** (`routes/feedbacks.py`)

- ✓ `POST /feedbacks/send-to-n8n` - Envía métricas a n8n para análisis
- ✓ `POST /feedbacks/receive-from-n8n` - Recibe feedback de n8n y lo guarda
- ✓ `GET /feedbacks/campaign/{campaign_id}` - Obtiene todos los feedbacks de una campaña
- ✓ `GET /feedbacks/{feedback_id}` - Obtiene un feedback específico
- ✓ `DELETE /feedbacks/{feedback_id}` - Elimina un feedback

### 4. **Documentación Creada**

- ✓ `FEEDBACK_N8N_README.md` - Documentación completa de uso
- ✓ `n8n_workflow_example.json` - Workflow de ejemplo para n8n
- ✓ `test_n8n_integration.py` - Script de pruebas
- ✓ `requirements.txt` - Dependencias necesarias

### 5. **Dependencias Agregadas**

- ✓ `httpx` - Cliente HTTP asíncrono para comunicación con n8n

---

## 🔄 Flujo de Trabajo

```
┌─────────────┐     ┌──────────┐     ┌──────────┐     ┌─────────────┐
│  Tu API     │────▶│   n8n    │────▶│  AI LLM  │────▶│  Tu API     │
│  FastAPI    │     │ Webhook  │     │ (OpenAI) │     │  (Guarda)   │
└─────────────┘     └──────────┘     └──────────┘     └─────────────┘
      │                                                        │
      │                                                        ▼
      └────────────────────────────────────────────▶  ┌─────────────┐
                    Consulta feedbacks                │  Base de    │
                                                      │  Datos      │
                                                      └─────────────┘
```

---

## 📊 Métricas Calculadas Automáticamente

El endpoint calcula automáticamente estas métricas adicionales:

| Métrica             | Fórmula                         | Descripción                                                       |
| ------------------- | ------------------------------- | ----------------------------------------------------------------- |
| **CTR**             | `(clicks / impresiones) * 100`  | Click Through Rate - Porcentaje de impresiones que generan clicks |
| **Conversion Rate** | `(conversiones / clicks) * 100` | Tasa de conversión - Porcentaje de clicks que se convierten       |
| **CPC**             | `gasto_total / clicks`          | Costo por Click                                                   |
| **CPA**             | `gasto_total / conversiones`    | Costo por Adquisición/Conversión                                  |

---

## 🚀 Cómo Usar

### Paso 1: Instalar Dependencias

```bash
cd PromptCampaignAPI
pip install -r requirements.txt
```

### Paso 2: Configurar n8n

1. Importa el workflow de ejemplo: `n8n_workflow_example.json`
2. Configura tus credenciales de OpenAI en n8n
3. Activa el workflow
4. Copia la URL del webhook

### Paso 3: Enviar Métricas para Análisis

```python
# Ejemplo usando httpx
import httpx

async def analizar_campaña(campaign_id: int):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/feedbacks/send-to-n8n",
            json={
                "campaign_id": campaign_id,
                "n8n_webhook_url": "https://tu-n8n.com/webhook/analizar-metricas"
            }
        )
        return response.json()
```

### Paso 4: Ver los Feedbacks Generados

```bash
# Vía API
GET http://localhost:8000/feedbacks/campaign/1
```

---

## 🧪 Testing

### Opción 1: Con Simulación (sin n8n)

```bash
python test_n8n_integration.py
```

Esto simulará la respuesta de n8n y guardará un feedback de ejemplo.

### Opción 2: Con n8n Real

1. Edita `test_n8n_integration.py`
2. Actualiza `N8N_WEBHOOK_URL` con tu URL real
3. Descomenta la sección de test real
4. Ejecuta: `python test_n8n_integration.py`

---

## 📝 Ejemplo de Uso Completo

```python
import httpx
import asyncio

async def ejemplo_completo():
    async with httpx.AsyncClient() as client:
        # 1. Enviar métricas a n8n
        print("Enviando métricas a n8n...")
        response = await client.post(
            "http://localhost:8000/feedbacks/send-to-n8n",
            json={
                "campaign_id": 1,
                "n8n_webhook_url": "https://n8n.example.com/webhook/analizar"
            }
        )
        print(f"✓ {response.json()['message']}")

        # 2. Esperar a que n8n procese (ajusta el tiempo según necesites)
        await asyncio.sleep(5)

        # 3. Obtener el feedback generado
        print("\nObteniendo feedbacks...")
        response = await client.get(
            "http://localhost:8000/feedbacks/campaign/1"
        )
        feedbacks = response.json()

        # 4. Mostrar el último feedback
        if feedbacks:
            ultimo = feedbacks[0]
            print(f"\n📝 Último Feedback (ID: {ultimo['id']}):")
            print(ultimo['texto_feedback'])

# Ejecutar
asyncio.run(ejemplo_completo())
```

---

## 🔐 Consideraciones de Seguridad

1. **Autenticación en n8n**: Configura autenticación básica o API key en tu webhook
2. **Validación de origen**: Verifica que las peticiones vengan de tu instancia de n8n
3. **Rate Limiting**: Implementa límites para prevenir abuso
4. **HTTPS**: Siempre usa HTTPS en producción

---

## 🛠️ Estructura de Archivos Nuevos/Modificados

```
PromptCampaignAPI/
├── models/
│   ├── campaign.py          ✏️ MODIFICADO
│   └── metric.py            ✏️ MODIFICADO
├── schemas/
│   └── n8n_schema.py        ✨ NUEVO
├── routes/
│   └── feedbacks.py         ✏️ REESCRITO COMPLETO
├── main.py                  ✏️ MODIFICADO (import Feedback)
├── requirements.txt         ✨ NUEVO
├── FEEDBACK_N8N_README.md   ✨ NUEVO
├── n8n_workflow_example.json ✨ NUEVO
└── test_n8n_integration.py  ✨ NUEVO
```

---

## 📚 Recursos Adicionales

- [Documentación completa](./FEEDBACK_N8N_README.md)
- [Workflow de n8n](./n8n_workflow_example.json)
- [Script de testing](./test_n8n_integration.py)
- [Documentación FastAPI](https://fastapi.tiangolo.com/)
- [Documentación n8n](https://docs.n8n.io/)

---

## ❓ Preguntas Frecuentes

### ¿Puedo usar otra IA además de OpenAI?

Sí, en el workflow de n8n puedes cambiar el nodo de OpenAI por Claude, Gemini, o cualquier otro modelo.

### ¿Qué pasa si n8n está caído?

El endpoint responderá con un error 503. Puedes implementar un sistema de cola para reintentos.

### ¿Puedo personalizar el análisis de la IA?

Sí, modifica el prompt en el workflow de n8n según tus necesidades.

### ¿Necesito n8n cloud o puedo usar self-hosted?

Funciona con ambos. Solo necesitas que la API pueda acceder al webhook de n8n.

---

## 🎉 ¡Listo para Usar!

Tu API ahora está completamente integrada con n8n para generar feedback automático de campañas usando IA.

**Próximos pasos sugeridos:**

1. Ejecutar el script de testing
2. Configurar tu workflow en n8n
3. Hacer una prueba end-to-end
4. Integrar en tu frontend

---

**¿Necesitas ayuda?** Consulta la documentación completa en `FEEDBACK_N8N_README.md`
