Este proyecto implementa un sistema distribuido para procesar preguntas y respuestas basado en un dataset real de Yahoo Answers.
El sistema incluye generación de tráfico, caché con políticas configurables, integración con un modelo LLM (Gemini API), cálculo de métricas de similitud y almacenamiento en MongoDB.



# Arquitectura del sistema

El sistema está compuesto por 6 servicios en Docker:

- Traffic Generator = genera preguntas aleatorias desde el dataset y las envía al caché.

- Cache = responde preguntas si ya existen  o consulta al LLM en caso de miss.

- Políticas soportadas: LRU, FIFO.

- LLM Service = conecta con Gemini API  o puede devolver respuestas simuladas.

- Score Service = compara la respuesta del dataset con la del LLM y calcula un score de similitud.

- Storage = guarda los resultados en la base de datos.

- MongoDB = almacena los documentos con preguntas, respuestas, hits, misses, scores, etc.


# Requisitos previos

- Docker
- Docker Compose
- Una API Key de Google Gemini

# Instalación y uso
- Clonar el repositorio
```bash
git clone <link del github>
cd <carpeta raiz del repositorio>
```
- Colocar el dataset
Descargar el dataset train_10k.csv y dejarlo en la carpeta dataset/.
o ocupar el del repositorio

- Configurar variables de entorno
Crear un archivo .env en la raíz del proyecto y poner:
### API Key de Gemini
GEMINI_API_KEY=<tu_api_key_aqui>

- Levantar el sistema
```bash
docker compose up -d
```
- Verificar que los contenedores estén corriendo

```bash
docker ps
```
# Monitoreo del sistema
- Logs del tráfico
```bash
docker compose logs -f traffic
```
- Logs del caché
```bash
docker compose logs -f cache
```
- Logs del LLM
```bash
docker compose logs -f llm
```
- Logs del scoring
```bash
docker compose logs -f score
```
- Logs del almacenamiento
```bash
docker compose logs -f storage
```
# Cambios de politicas y distribuciones del sistema

```bash
CACHE_POLICY=<politoca o utilizar(FIFO o LRU)> CACHE_SIZE=<tamaño del cache> docker compose up -d cache
DIST=<distribucion a ocupar> RATE=<rate de consultas(ver dependiendo de el plan de geminis)> docker compose up -d traffic
```
# Verificación en MongoDB

Ingresar al contenedor de MongoDB:

```bash
docker exec -it mongo mongosh
```

Dentro del shell:

```bash
use yahoo_db
db.answers.countDocuments()
db.answers.findOne()
db.answers.find().limit(<cantidad de consultas a ver>).pretty()
```
Esto mostrará documentos con la pregunta, respuesta del dataset, respuesta del LLM, hits, misses y score.

# Apagar el sistema
```bash
docker compose down
```











