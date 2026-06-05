# 🚀 QUICK START - Referencia Rápida

Inicia un sistema CDC Kafka completo en 5 minutos.

## 1️⃣ Levantar (3 comandos)

```powershell
# Elige KRAFT (nuevo) o Zookeeper (tradicional)
cd C:\Users\<usuario>\kafka\kraft      # KRAFT
# cd C:\Users\<usuario>\kafka\zookeeper  # O Zookeeper

docker-compose up -d
docker-compose ps  # Verifica que todo corre
```

⏱️ Espera 30 segundos a que todo inicie.

## 2️⃣ Crear Tabla

```powershell
docker exec -it postgres psql -U postgres -d demo -c "
CREATE TABLE clientes (id SERIAL PRIMARY KEY, nombre VARCHAR(100), email VARCHAR(100));
INSERT INTO clientes VALUES (1, 'Juan', 'juan@test.com'), (2, 'María', 'maria@test.com');"
```

## 3️⃣ Crear Connector

```powershell
$body = @{
    "name"="postgres-connector"
    "config"=@{
        "connector.class"="io.debezium.connector.postgresql.PostgresConnector"
        "database.hostname"="postgres"
        "database.port"="5432"
        "database.user"="postgres"
        "database.password"="postgres"
        "database.dbname"="demo"
        "topic.prefix"="cdc"
        "table.include.list"="public.clientes"
        "plugin.name"="pgoutput"
    }
} | ConvertTo-Json

Invoke-WebRequest -Uri "http://localhost:8083/connectors" -Method POST -Headers @{"Content-Type"="application/json"} -Body $body
```

## 4️⃣ Ver en Kafka UI

- Abre http://localhost:51439
- Topics → `cdc.public.clientes`
- Deberías ver 2 mensajes

## 5️⃣ Python Consumer

```powershell
cd C:\Users\<usuario>\kafka
pip install -r requirements.txt
python consumer.py
```

## 6️⃣ Prueba: Hacer un Cambio

En otra terminal:
```powershell
docker exec postgres psql -U postgres -d demo -c "INSERT INTO clientes VALUES (3, 'Carlos', 'carlos@test.com');"
```

✅ El consumer **en tiempo real** muestra:
```
➕ CREATE
Tabla: clientes
  Después: {'id': 3, 'nombre': 'Carlos', 'email': 'carlos@test.com'}
```

---

## 📋 Comandos Frecuentes

| Acción | Comando |
|--------|---------|
| **Levantar** | `docker-compose up -d` |
| **Detener** | `docker-compose down` |
| **Logs** | `docker-compose logs -f kafka-connect` |
| **Limpiar TODO** | `docker-compose down -v` |
| **Ver topics** | http://localhost:51439 |
| **Consumer** | `python consumer.py` |
| **Consumer (verbose)** | `python consumer.py --verbose` |
| **SQL en Postgres** | `docker exec -it postgres psql -U postgres -d demo` |
| **Connector status** | `Invoke-WebRequest http://localhost:8083/connectors/postgres-connector/status` |

---

## 🔌 URLs

| Servicio | URL | Credenciales |
|----------|-----|--------------|
| **Kafka UI** | http://localhost:51439 | - |
| **Kafka Connect API** | http://localhost:8083/connectors | - |
| **PostgreSQL** | localhost:51438 | postgres / postgres |

---

## 🐛 Problemas Rápidos

**"Connection refused on 8083"**
→ Espera 30 segundos, Kafka Connect está iniciando

**"Topic not found"**
→ Haz un cambio en PostgreSQL para generar el topic

**"Consumer no recibe mensajes"**
→ Verifica que el connector está RUNNING: `Invoke-WebRequest http://localhost:8083/connectors/postgres-connector/status`

---

## 📚 Documentación Completa

Ver [README.md](README.md) para:
- Explicación detallada de KRAFT vs Zookeeper
- Troubleshooting completo
- Ejemplos avanzados
- Referencias

---

**¿Primera vez?** → Ve a [CHECKLIST.md](CHECKLIST.md) para un paso a paso detallado.
