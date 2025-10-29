"""
Script de ejemplo para probar la integración con n8n
Asegúrate de tener tu API corriendo y un workflow de n8n configurado
"""

import asyncio
import httpx
from datetime import date
from dotenv import load_dotenv
import os


load_dotenv()  

n8n_webhoow = os.getenv("N8N_URL")

# Configuración
API_BASE_URL = "http://localhost:8000"
N8N_WEBHOOK_URL = n8n_webhoow




async def crear_campaña_ejemplo():
    """Crea una campaña de ejemplo para testing"""
    async with httpx.AsyncClient() as client:
     
        campaign_data = {
            "nombre": "Campaña Black Friday 2024",
            "plataforma": "Google Ads",
            "fecha_inicio": "2024-11-20",
            "fecha_fin": "2024-11-30",
            "presupuesto": 5000.00,
            "user_id": 1  # Asegúrate de que este usuario existe
        }
        
        response = await client.post(
            f"{API_BASE_URL}/campaigns",
            json=campaign_data
        )
        
        if response.status_code == 201:
            print(f"✓ Campaña creada: {response.json()}")
            return response.json()["id"]
        else:
            print(f"✗ Error creando campaña: {response.text}")
            return None


async def crear_metrica_ejemplo(campaign_id: int):
    """Crea una métrica de ejemplo para testing"""
    async with httpx.AsyncClient() as client:
        metric_data = {
            "campaign_id": campaign_id,
            "impresiones": 75000,
            "clicks": 3750,
            "conversiones": 187,
            "gasto_total": 2250.75,
            "fecha_registro": str(date.today())
        }
        
        response = await client.post(
            f"{API_BASE_URL}/metrics",
            json=metric_data
        )
        
        if response.status_code == 201:
            print(f"✓ Métrica creada: {response.json()}")
            return response.json()["id"]
        else:
            print(f"✗ Error creando métrica: {response.text}")
            return None


async def enviar_metricas_a_n8n(campaign_id: int, metric_id: int = None):
    """Envía métricas a n8n para análisis de IA"""
    async with httpx.AsyncClient(timeout=60.0) as client:
        request_data = {
            "campaign_id": campaign_id,
            "n8n_webhook_url": N8N_WEBHOOK_URL
        }
        
        if metric_id:
            request_data["metric_id"] = metric_id
        
        print(f"\n📤 Enviando métricas a n8n...")
        print(f"   Campaign ID: {campaign_id}")
        print(f"   Metric ID: {metric_id or 'Más reciente'}")
        print(f"   Webhook URL: {N8N_WEBHOOK_URL}")
        
        response = await client.post(
            f"{API_BASE_URL}/feedbacks/send-to-n8n",
            json=request_data
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"\n✓ {result['message']}")
            print(f"   Status de n8n: {result['n8n_response_status']}")
            return result
        else:
            print(f"\n✗ Error: {response.status_code}")
            print(f"   {response.text}")
            return None


async def obtener_feedbacks_de_campaña(campaign_id: int):
    """Obtiene todos los feedbacks de una campaña"""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{API_BASE_URL}/feedbacks/campaign/{campaign_id}"
        )
        
        if response.status_code == 200:
            feedbacks = response.json()
            print(f"\n📋 Feedbacks encontrados: {len(feedbacks)}")
            
            for i, feedback in enumerate(feedbacks, 1):
                print(f"\n--- Feedback #{i} (ID: {feedback['id']}) ---")
                print(f"Métrica ID: {feedback['metric_id']}")
                print(f"Texto: {feedback['texto_feedback'][:200]}...")
                
            return feedbacks
        else:
            print(f"\n✗ Error obteniendo feedbacks: {response.text}")
            return []


async def simular_respuesta_n8n(campaign_id: int, metric_id: int):
    """
    Simula la respuesta de n8n enviando un feedback directamente
    Útil para testing sin necesidad de configurar n8n
    """
    async with httpx.AsyncClient() as client:
        feedback_data = {
            "campaign_id": campaign_id,
            "metric_id": metric_id,
            "texto_feedback": """
📊 ANÁLISIS DE RENDIMIENTO - Campaña Black Friday 2024

🎯 EVALUACIÓN GENERAL: EXCELENTE
La campaña muestra un rendimiento sobresaliente en todas las métricas clave.

📈 MÉTRICAS DESTACADAS:
• CTR: 5.0% - Muy superior al promedio de la industria (1.91%)
• Conversion Rate: 4.99% - Excelente tasa de conversión
• CPC: $0.60 - Costo competitivo por click
• CPA: $12.04 - Excelente retorno por conversión

💡 RECOMENDACIONES:
1. ESCALAR PRESUPUESTO: Aumentar inversión en 30% para capitalizar el excelente rendimiento
2. A/B TESTING: Crear variaciones de los anuncios top performers para optimización continua
3. AUDIENCIAS SIMILARES: Expandir a lookalike audiences basadas en convertidores
4. REMARKETING: Implementar campaña de remarketing para usuarios que hicieron click pero no convirtieron

⚠️ ALERTAS:
• Ninguna alerta crítica detectada
• Monitorear de cerca el CPA si se escala el presupuesto

🎖️ CONCLUSIÓN:
Esta campaña es un caso de éxito. Se recomienda escalar con precaución y mantener monitoreo constante.
            """
        }
        
        print(f"\n🤖 Simulando respuesta de IA de n8n...")
        
        response = await client.post(
            f"{API_BASE_URL}/feedbacks/receive-from-n8n",
            json=feedback_data
        )
        
        if response.status_code == 201:
            result = response.json()
            print(f"✓ Feedback guardado exitosamente (ID: {result['id']})")
            return result
        else:
            print(f"✗ Error guardando feedback: {response.text}")
            return None


async def test_completo():
    """Ejecuta un test completo del flujo"""
    print("=" * 70)
    print("🚀 TEST DE INTEGRACIÓN CON N8N")
    print("=" * 70)
    
    # Nota: Ajusta estos IDs si ya tienes datos en tu base de datos
    # O comenta estas líneas y usa crear_campaña_ejemplo() y crear_metrica_ejemplo()
    
    CAMPAIGN_ID = 1  # Cambia esto por un ID existente
    METRIC_ID = 1    # Cambia esto por un ID existente
    
    # Opción 1: Usar datos existentes
    print(f"\n📌 Usando campaña existente (ID: {CAMPAIGN_ID})")
    
    # Opción 2: Crear nuevos datos (descomenta si lo necesitas)
    # CAMPAIGN_ID = await crear_campaña_ejemplo()
    # if CAMPAIGN_ID:
    #     METRIC_ID = await crear_metrica_ejemplo(CAMPAIGN_ID)
    
    if CAMPAIGN_ID and METRIC_ID:
        # Simular respuesta de n8n (para testing sin n8n configurado)
        print("\n" + "=" * 70)
        print("MODO: SIMULACIÓN (sin n8n real)")
        print("=" * 70)
        await simular_respuesta_n8n(CAMPAIGN_ID, METRIC_ID)
        
        # Obtener feedbacks
        await asyncio.sleep(1)  # Pequeña pausa
        await obtener_feedbacks_de_campaña(CAMPAIGN_ID)
        
        # Si quieres probar con n8n real, descomenta esto:
        # print("\n" + "=" * 70)
        # print("MODO: INTEGRACIÓN REAL CON N8N")
        # print("=" * 70)
        # await enviar_metricas_a_n8n(CAMPAIGN_ID, METRIC_ID)
        # await asyncio.sleep(5)  # Esperar a que n8n procese
        # await obtener_feedbacks_de_campaña(CAMPAIGN_ID)
    
    print("\n" + "=" * 70)
    print("✅ TEST COMPLETADO")
    print("=" * 70)


async def test_envio_n8n_real():
    """Test específico para envío real a n8n"""
    print("=" * 70)
    print("🔗 TEST DE ENVÍO A N8N REAL")
    print("=" * 70)
    
    CAMPAIGN_ID = 1  # Cambia esto
    METRIC_ID = None  # None = usa la métrica más reciente
    
    await enviar_metricas_a_n8n(CAMPAIGN_ID, METRIC_ID)
    
    print("\n⏳ Esperando 10 segundos para que n8n procese...")
    await asyncio.sleep(10)
    
    await obtener_feedbacks_de_campaña(CAMPAIGN_ID)


if __name__ == "__main__":
    # Ejecutar test completo (con simulación)
    asyncio.run(test_completo())
    
    # O ejecutar test con n8n real (descomenta la siguiente línea)
    # asyncio.run(test_envio_n8n_real())
