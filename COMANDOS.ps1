# Script de Comandos Útiles para Kafka CDC
# Copia y pega los comandos que necesites en PowerShell

# ============================================================
# 1. LEVANTAR CONTAINERS
# ============================================================

# KRAFT (3 brokers - Recomendado)
cd C:\Users\<usuario>\kafka\kraft
docker-compose up -d

# O Zookeeper (1 broker - Traditional)
cd C:\Users\<usuario>\kafka\zookeeper
docker-compose up -d

# ============================================================
# 2. VERIFICAR ESTADO
# ============================================================

# Ver containers corriendo
docker-compose ps

# Ver logs de Kafka Connect
docker-compose logs -f kafka-connect

# ============================================================
# 3. POSTGRESQL
# ============================================================

# Conectar a PostgreSQL interactivamente
docker exec -it postgres psql -U postgres -d demo

# Crear tabla (ejecutar desde PowerShell)
docker exec -it postgres psql -U postgres -d demo -c "
CREATE TABLE clientes (
  id SERIAL PRIMARY KEY,
  nombre VARCHAR(100) NOT NULL,
  email VARCHAR(100),
  fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);"

# Insertar datos
docker exec -it postgres psql -U postgres -d demo -c "
INSERT INTO clientes (nombre, email) VALUES ('Juan Pérez', 'juan@email.com');
INSERT INTO clientes (nombre, email) VALUES ('María García', 'maria@email.com');"

# Ver datos
docker exec -it postgres psql -U postgres -d demo -c "SELECT * FROM clientes;"

# Actualizar dato
docker exec -it postgres psql -U postgres -d demo -c "
UPDATE clientes SET email = 'juan.nuevo@email.com' WHERE id = 1;"

# Eliminar dato
docker exec -it postgres psql -U postgres -d demo -c "DELETE FROM clientes WHERE id = 2;"

# ============================================================
# 4. KAFKA CONNECT - CREAR CONNECTOR
# ============================================================

# Copiar todo y ejecutar de una vez
$body = @{
    "name" = "postgres-connector"
    "config" = @{
        "connector.class" = "io.debezium.connector.postgresql.PostgresConnector"
        "database.hostname" = "postgres"
        "database.port" = "5432"
        "database.user" = "postgres"
        "database.password" = "postgres"
        "database.dbname" = "demo"
        "topic.prefix" = "cdc"
        "table.include.list" = "public.clientes"
        "plugin.name" = "pgoutput"
        "publication.name" = "debezium"
        "slot.name" = "debezium"
    }
} | ConvertTo-Json

Invoke-WebRequest -Uri "http://localhost:8083/connectors" `
  -Method POST `
  -Headers @{ "Content-Type" = "application/json" } `
  -Body $body

# ============================================================
# 5. KAFKA CONNECT - VERIFICAR
# ============================================================

# Listar connectors
Invoke-WebRequest -Uri "http://localhost:8083/connectors" -Method GET

# Ver estado
Invoke-WebRequest -Uri "http://localhost:8083/connectors/postgres-connector/status" -Method GET

# ============================================================
# 6. KAFKA CONNECT - OPERACIONES
# ============================================================

# Pausar connector
Invoke-WebRequest -Uri "http://localhost:8083/connectors/postgres-connector/pause" -Method PUT

# Reanudar connector
Invoke-WebRequest -Uri "http://localhost:8083/connectors/postgres-connector/resume" -Method PUT

# Eliminar connector
Invoke-WebRequest -Uri "http://localhost:8083/connectors/postgres-connector" -Method DELETE

# ============================================================
# 7. PYTHON CONSUMER
# ============================================================

# Instalar dependencias (primera vez)
pip install -r requirements.txt

# Ejecutar consumer (escuchar todos los cambios)
cd C:\Users\<usuario>\kafka
python consumer.py

# Con opciones
python consumer.py --topic cdc.public.clientes --verbose
python consumer.py --max-messages 10
python consumer.py --filter c  # Solo CREATE

# ============================================================
# 8. LIMPIAR CONTAINERS
# ============================================================

# Detener sin borrar datos
docker-compose down

# Detener y borrar TODO (datos, volúmenes, networks)
docker-compose down -v

# ============================================================
# 9. URLS ÚTILES
# ============================================================

# Kafka UI
# http://localhost:51439

# Kafka Connect API
# http://localhost:8083

# PostgreSQL (desde GUI)
# Host: localhost:51438
# Usuario: postgres
# Contraseña: postgres
# Base de datos: demo
