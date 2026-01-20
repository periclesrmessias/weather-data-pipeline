import azure.functions as func
import logging
import requests
import os
import json
import time
from datetime import datetime
from azure.storage.blob import BlobServiceClient

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

# Função TESTE (opcional - pode remover se quiser)
@app.route(route="hello")
def hello_world(req: func.HttpRequest) -> func.HttpResponse:
    """Função simples para teste"""
    return func.HttpResponse("Azure Functions está funcionando!", status_code=200)


@app.function_name(name="CollectAllCapitals")
@app.route(route="collect/all")
def collect_all_capitals(req: func.HttpRequest) -> func.HttpResponse:
    """Coleta dados de TODAS as capitais brasileiras"""
    logging.info("Iniciando coleta de todas as capitais brasileiras...")
    
    capitais_brasil = [
        "Rio Branco", "Maceió", "Macapá", "Manaus", "Salvador",
        "Fortaleza", "Brasília", "Vitória", "Goiânia", "São Luís",
        "Cuiabá", "Campo Grande", "Belo Horizonte", "Belém",
        "João Pessoa", "Curitiba", "Recife", "Teresina",
        "Rio de Janeiro", "Natal", "Porto Alegre", "Boa Vista",
        "Florianópolis", "São Paulo", "Aracaju", "Palmas"
    ]
    
    resultados = []
    api_key = os.environ.get("OpenWeather_ApiKey")
    
    if not api_key:
        return func.HttpResponse(
            json.dumps({"error": "Chave API não configurada em OpenWeather_ApiKey"}),
            status_code=500,
            mimetype="application/json"
        )
    
    connection_string = os.environ.get("AzureWebJobsStorage")
    if not connection_string or connection_string.strip() == "":
        return func.HttpResponse(
            json.dumps({"error": "String de conexão do Azure Storage não configurada"}),
            status_code=500,
            mimetype="application/json"
        )
    
    for cidade in capitais_brasil:
        try:
            logging.info(f"Coletando dados de: {cidade}")
            
            # Chamada à API
            url = f"https://api.openweathermap.org/data/2.5/weather?q={cidade}&appid={api_key}&units=metric&lang=pt"
            response = requests.get(url)
            response.raise_for_status()  # Lança erro para respostas 4xx/5xx
            data = response.json()
            
            # Salva no Blob Storage
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            cidade_formatada = cidade.lower().replace(' ', '-').replace('ã', 'a').replace('ç', 'c')
            blob_name = f"capitais-batch/{cidade_formatada}/{timestamp}.json"
            
            # Enriquecer dados com metadados
            dados_completos = {
                "extraction_timestamp": datetime.utcnow().isoformat() + "Z",
                "source_system": "OpenWeatherMap",
                "city_requested": cidade,
                "weather_data": data
            }
            
            blob_service_client = BlobServiceClient.from_connection_string(connection_string)
            blob_client = blob_service_client.get_blob_client(container="weather-container", blob=blob_name)
            blob_client.upload_blob(json.dumps(dados_completos, indent=2), overwrite=True)
            
            resultados.append({
                "cidade": cidade,
                "status": "sucesso",
                "blob_path": blob_name,
                "temperatura": data.get('main', {}).get('temp'),
                "clima": data.get('weather', [{}])[0].get('description', 'N/A')
            })
            
            logging.info(f"  ✅ {cidade} salvo em: {blob_name}")
            time.sleep(1.2)  # Respeita rate limit da API (60 chamadas/minuto)
            
        except requests.exceptions.RequestException as e:
            logging.error(f"  ❌ Erro API para {cidade}: {e}")
            resultados.append({
                "cidade": cidade,
                "status": "erro",
                "erro": f"Erro na API: {str(e)}"
            })
        except Exception as e:
            logging.error(f"  ❌ Erro geral para {cidade}: {e}")
            resultados.append({
                "cidade": cidade,
                "status": "erro",
                "erro": f"Erro interno: {str(e)}"
            })
    
    # Resumo final
    sucessos = len([r for r in resultados if r["status"] == "sucesso"])
    
    logging.info(f"Coleta concluída: {sucessos}/{len(capitais_brasil)} capitais coletadas")
    
    return func.HttpResponse(
        json.dumps({
            "total_capitais": len(capitais_brasil),
            "coletadas_com_sucesso": sucessos,
            "com_erro": len(capitais_brasil) - sucessos,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "resultados": resultados
        }, indent=2),
        mimetype="application/json",
        status_code=200
    )
# Adicionando Timer

@app.function_name(name="AutoWeatherCollector")
@app.timer_trigger(schedule="0 */10 * * * *", arg_name="mytimer", run_on_startup=False)
def auto_weather_collector(mytimer: func.TimerRequest) -> None:
    """Coleta automática das capitais - roda sozinho"""
    logging.info("🔄 TIMER ACIONADO: Iniciando coleta automática...")
    
    # MESMA lista de capitais (copie da função anterior)
    capitais_brasil = [
        "Rio Branco", "Maceió", "Macapá", "Manaus", "Salvador",
        "Fortaleza", "Brasília", "Vitória", "Goiânia", "São Luís",
        "Cuiabá", "Campo Grande", "Belo Horizonte", "Belém",
        "João Pessoa", "Curitiba", "Recife", "Teresina",
        "Rio de Janeiro", "Natal", "Porto Alegre", "Boa Vista",
        "Florianópolis", "São Paulo", "Aracaju", "Palmas"
    ]
    
    api_key = os.environ.get("OpenWeather_ApiKey")
    connection_string = os.environ.get("AzureWebJobsStorage")
    
    if not api_key or not connection_string:
        logging.error("❌ Configurações não encontradas no Timer")
        return
    
    sucessos = 0
    
    for cidade in capitais_brasil:
        try:
            logging.info(f"⏳ Timer coletando: {cidade}")
            
            url = f"https://api.openweathermap.org/data/2.5/weather?q={cidade}&appid={api_key}&units=metric&lang=pt"
            response = requests.get(url)
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
            logging.info(f"✅ Timer: {cidade} salvo")
            time.sleep(1.2)
            
        except Exception as e:
            logging.error(f"❌ Timer erro em {cidade}: {e}")
    
    logging.info(f"🏁 Timer concluído: {sucessos}/{len(capitais_brasil)} capitais")

