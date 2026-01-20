# timer_function.py
import azure.functions as func
import logging
import requests
import json
import time
from datetime import datetime
from azure.storage.blob import BlobServiceClient
import os

app = func.FunctionApp()

@app.function_name(name="AutoWeatherCollector")
@app.schedule(schedule="0 */2 * * *")  # ⚠️ MUDEI para 2h para TESTAR
def auto_weather_collector(mytimer: func.TimerRequest) -> None:
    """Coleta automática das capitais - roda automaticamente"""
    logging.info("🔄 TIMER ACIONADO: Iniciando coleta automática programada...")
    
    # SUA lista de capitais (COPIE A MESMA LISTA do function_app.py)
    capitais_brasil = [
        "Rio Branco", "Maceió", "Macapá", "Manaus", "Salvador",
        "Fortaleza", "Brasília", "Vitória", "Goiânia", "São Luís",
        "Cuiabá", "Campo Grande", "Belo Horizonte", "Belém",
        "João Pessoa", "Curitiba", "Recife", "Teresina",
        "Rio de Janeiro", "Natal", "Porto Alegre", "Boa Vista",
        "Florianópolis", "São Paulo", "Aracaju", "Palmas"
    ]
    
    api_key = os.environ.get("OpenWeather_ApiKey")
    if not api_key:
        logging.error("❌ Erro: OpenWeather_ApiKey não configurada")
        return
    
    connection_string = os.environ.get("AzureWebJobsStorage")
    if not connection_string:
        logging.error("❌ Erro: AzureWebJobsStorage não configurada")
        return
    
    sucessos = 0
    erros = 0
    
    for cidade in capitais_brasil:
        try:
            logging.info(f"⏳ Coletando: {cidade}")
            
            url = f"https://api.openweathermap.org/data/2.5/weather?q={cidade}&appid={api_key}&units=metric&lang=pt"
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            
            # Salva no Blob Storage
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            cidade_formatada = cidade.lower().replace(' ', '-').replace('ã', 'a').replace('ç', 'c')
            blob_name = f"timer-auto/{cidade_formatada}/{timestamp}.json"
            
            dados_completos = {
                "extraction_timestamp": datetime.utcnow().isoformat() + "Z",
                "source_system": "OpenWeatherMap",
                "city_requested": cidade,
                "weather_data": data
            }
            
            blob_service_client = BlobServiceClient.from_connection_string(connection_string)
            blob_client = blob_service_client.get_blob_client(container="weather-container", blob=blob_name)
            blob_client.upload_blob(json.dumps(dados_completos, indent=2), overwrite=True)
            
            sucessos += 1
            logging.info(f"✅ {cidade} salvo automaticamente")
            time.sleep(1.2)  # Respeita rate limit
            
        except Exception as e:
            erros += 1
            logging.error(f"❌ Erro em {cidade}: {str(e)}")
    
    logging.info(f"🏁 TIMER CONCLUÍDO: {sucessos} sucessos, {erros} erros, total: {len(capitais_brasil)} capitais")