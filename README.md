# Guía Completa: Kafka con Change Data Capture (CDC)

Una guía paso a paso para implementar Kafka con Debezium y PostgreSQL. Diseñada para profesionales técnicos sin experiencia profunda en Kafka.

---

## 📋 Tabla de Contenidos

1. [Requisitos](#requisitos)
2. [Conceptos Clave](#conceptos-clave)
3. [Estructura del Proyecto](#estructura-del-proyecto)
4. [Instalación y Levantamiento](#instalación-y-levantamiento)
5. [Configuración de Kafka Connect](#configuración-de-kafka-connect)
6. [Pruebas Prácticas](#pruebas-prácticas)
7. [Consumir Mensajes con Python](#consumir-mensajes-con-python)
8. [Troubleshooting](#troubleshooting)

---

## 🔧 Requisitos

### Software Obligatorio

- **Docker Desktop** (v4.0+)
  - Descargar: https://www.docker.com/products/docker-desktop
  - Requiere Windows 10/11 Pro, Enterprise o Home (con WSL2)
  - Debe estar corriendo durante todo el proceso

- **Python 3.8+** (opcional, solo para consumir mensajes)
  - Descargar: https://www.python.org/downloads
  - La librería `confluent-kafka` necesita instalarse

- **PowerShell 7+** (recomendado) o cmd
  - Para ejecutar comandos curl/Invoke-WebRequest

- **Cliente PostgreSQL** (opcional, para conectar a la BD)
  - pgAdmin, DBeaver, o CLI `psql`

### Requisitos del Sistema

- **RAM**: Mínimo 4GB disponibles (recomendado 8GB)
- **Espacio en disco**: Mínimo 2GB disponibles
- **Red**: Puerto 8080, 8083, 5432, 9092 disponibles (o similares)

---

## 💡 Conceptos Clave

### KRAFT vs Zookeeper

Kafka tiene dos modos de operación para la coordinación del cluster:

| Aspecto | **KRAFT** | **Zookeeper** |
|--------|---------|-------------|
| **Dependencias** | Ninguna (integrado en Kafka) | Requiere Zookeeper externo |
| **Complejidad** | Más simple | Más componentes |
| **Performance** | Más rápido | Ligeramente más lento |
| **Casos de Uso** | Nueva, producción (Kafka 4.0+) | Legacy, migración |
| **Cluster Size** | 3+ brokers (HA recomendado) | Flexible |
| **Este proyecto** | `kraft/docker-compose.yml` | `zookeeper/docker-compose.yml` |

**Recomendación**: Usa **KRAFT** para nuevos proyectos. Usa **Zookeeper** si necesitas compatibilidad con sistemas legacy.

### Componentes Principales

1. **Kafka Brokers**: Almacenan y sirven los mensajes
2. **Kafka Connect + Debezium**: Capturan cambios de PostgreSQL en tiempo real
3. **PostgreSQL**: Base de datos fuente (cambios se replican a Kafka)
4. **Kafka UI**: Panel web para monitorear topics y mensajes

---

## 📁 Estructura del Proyecto

```
kafka/
├── README.md                          # Esta guía
├── Guia.txt                           # Notas originales
├── kraft/
│   └── docker-compose.yml             # KRAFT: 3 brokers, sin Zookeeper
├── zookeeper/
│   └── docker-compose.yml             # Zookeeper: 1 broker con Zookeeper
├── consumer.py                        # Script Python para consumir (TÚ LO CREARÁS)
└── requirements.txt                   # Dependencias Python (TÚ LO CREARÁS)
```

---

## 🚀 Instalación y Levantamiento

### Opción 1: KRAFT (Recomendado - 3 Brokers)

**Paso 1**: Navega a la carpeta KRAFT

```powershell
cd C:\Users\<usuario>\kafka\kraft
```

**Paso 2**: Levanta los containers

```powershell
docker-compose up -d
```

**Paso 3**: Verifica que todo esté corriendo

```powershell
docker-compose ps
```

Deberías ver:
```
CONTAINER ID   NAMES              STATUS
...            kafka1_kraft       Up ...
...            kafka2_kraft       Up ...
...            kafka3_kraft       Up ...
...            postgres_kraft     Up ...
...            kafka-connect-kraft Up ...
...            kafka-ui-kraft     Up ...
```

**Paso 4**: Accede a los servicios

| Servicio | URL |
|----------|-----|
| Kafka UI | http://localhost:51439 |
| Kafka Connect | http://localhost:8083 |
| PostgreSQL | localhost:51438 (usuario: `postgres`, contraseña: `postgres`) |

---

### Opción 2: Zookeeper (Traditional - 1 Broker)

**Paso 1**: Navega a la carpeta Zookeeper

```powershell
cd C:\Users\<usuario>\kafka\zookeeper
```

**Paso 2**: Levanta los containers

```powershell
docker-compose up -d
```

**Paso 3**: Verifica que todo esté corriendo

```powershell
docker-compose ps
```

**Paso 4**: Accede a los servicios

| Servicio | URL |
|----------|-----|
| Kafka UI | http://localhost:51439 |
| Kafka Connect | http://localhost:8083 |
| PostgreSQL | localhost:51438 |

---

### Detener los Containers

**Para detener sin borrar volúmenes**:
```powershell
docker-compose down
```

**Para detener y borrar TODO (datos, volúmenes, networks)**:
```powershell
docker-compose down -v
```

⚠️ **ADVERTENCIA**: `down -v` elimina toda la base de datos y los datos de Kafka.

---

## 🔗 Configuración de Kafka Connect

Kafka Connect captura cambios de PostgreSQL automáticamente.

### Paso 1: Crear la Tabla en PostgreSQL

Conéctate a PostgreSQL:

```powershell
# Opción 1: Usando cmd directo
docker exec -it postgres psql -U postgres -d demo

# Opción 2: O usa una GUI como DBeaver/pgAdmin
# Host: localhost:51438, Usuario: postgres, Contraseña: postgres, BD: demo
```

Ejecuta este SQL:

```sql
-- Crear tabla de ejemplo
CREATE TABLE clientes (
  id SERIAL PRIMARY KEY,
  nombre VARCHAR(100) NOT NULL,
  email VARCHAR(100),
  fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insertar datos de prueba
INSERT INTO clientes (nombre, email) VALUES ('Juan Pérez', 'juan@email.com');
INSERT INTO clientes (nombre, email) VALUES ('María García', 'maria@email.com');

-- Verificar
SELECT * FROM clientes;
```

### Paso 2: Configurar Debezium Connector en Kafka Connect

Abre **PowerShell** y ejecuta este comando:

```powershell
# Copiar y pegar todo esto de una vez
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
```

**Respuesta esperada** (en JSON):
```json
{
  "name": "postgres-connector",
  "config": { ... }
}
```

### Paso 3: Verificar que el Connector se Creó

```powershell
Invoke-WebRequest -Uri "http://localhost:8083/connectors/postgres-connector/status" -Method GET | ConvertTo-Json
```

Deberías ver `"state": "RUNNING"`.

### Paso 4: Verificar Topics en Kafka UI

1. Abre http://localhost:51439
2. Haz clic en **Topics** en el sidebar
3. Deberías ver:
   - `cdc-configs`
   - `cdc-offsets`
   - `cdc-status`
   - `cdc.public.clientes` ← **Este es el topic de datos**

---

## 🧪 Pruebas Prácticas

### Test 1: Ver Cambios en Kafka UI

**Paso 1**: Realiza cambios en PostgreSQL

```sql
-- Conecta a PostgreSQL (ver Configuración de Kafka Connect, Paso 1)
INSERT INTO clientes (nombre, email) VALUES ('Carlos López', 'carlos@email.com');
UPDATE clientes SET email = 'juan.nuevo@email.com' WHERE id = 1;
DELETE FROM clientes WHERE id = 2;
```

**Paso 2**: Abre Kafka UI y visualiza

1. Ve a http://localhost:51439
2. Click en el topic `cdc.public.clientes`
3. Deberías ver **3 mensajes** (insert, update, delete)
4. Cada mensaje contiene:
   - `before`: Valor anterior
   - `after`: Valor nuevo
   - `op`: Tipo de operación (c=create, u=update, d=delete)

---

### Test 2: Consumir Mensajes con Python

#### Opción A: Quick Test (Una línea)

```powershell
# Descarga la librería Confluent Kafka
pip install confluent-kafka

# Ejecuta el consumer (ver archivo consumer.py abajo)
python consumer.py
```

#### Opción B: Crear el Script Python

**Paso 1**: Crea el archivo `consumer.py` en la carpeta `kafka/`:

```python
#!/usr/bin/env python3
"""
Consumer de Kafka para CDC de PostgreSQL
Captura cambios en tiempo real desde la tabla clientes
"""

import json
from confluent_kafka import Consumer, KafkaError
import sys

# Configuración del Consumer
config = {
    'bootstrap.servers': 'localhost:9092',  # Zookeeper: 9092, KRAFT: 9092
    'group.id': 'python-consumer-group',
    'auto.offset.reset': 'earliest',
    'enable.auto.commit': True
}

# Crear consumer
consumer = Consumer(config)

# Suscribirse al topic de clientes
topics = ['cdc.public.clientes']  # Asegúrate que coincida con tu topic
consumer.subscribe(topics)

print(f"✅ Conectado a Kafka. Escuchando topics: {topics}")
print("📥 Esperando mensajes... (Ctrl+C para salir)\n")

try:
    while True:
        msg = consumer.poll(timeout=1.0)
        
        if msg is None:
            continue
        
        if msg.error():
            if msg.error().code() == KafkaError._PARTITION_EOF:
                continue
            else:
                print(f"❌ Error: {msg.error()}")
                break
        
        # Parsear el mensaje
        value = json.loads(msg.value().decode('utf-8'))
        
        # Extraer información
        payload = value.get('payload', {})
        before = payload.get('before')
        after = payload.get('after')
        op = payload.get('op')
        
        # Traducir operación
        operation_map = {
            'c': '➕ CREATE (Insert)',
            'u': '🔄 UPDATE',
            'd': '❌ DELETE',
            'r': '📖 READ'
        }
        operation_text = operation_map.get(op, op)
        
        # Mostrar resultado
        print(f"\n{operation_text}")
        print(f"{'─' * 50}")
        
        if before:
            print(f"Antes:  {before}")
        if after:
            print(f"Después: {after}")
        
        print(f"Topic: {msg.topic()} | Partition: {msg.partition()} | Offset: {msg.offset()}")

except KeyboardInterrupt:
    print("\n\n👋 Consumer detenido por el usuario")
finally:
    consumer.close()
```

**Paso 2**: Instala la dependencia

```powershell
pip install confluent-kafka
```

**Paso 3**: Ejecuta el consumer

```powershell
cd C:\Users\luisp\windows-code\kafka
python consumer.py
```

**Paso 4**: En otra terminal, haz cambios en PostgreSQL

```powershell
docker exec -it postgres psql -U postgres -d demo -c "INSERT INTO clientes (nombre, email) VALUES ('David Rodríguez', 'david@email.com');"
```

**Resultado esperado en Python**: Deberías ver el mensaje capturado en tiempo real:
```
➕ CREATE (Insert)
──────────────────────────────────
Después: {'id': 4, 'nombre': 'David Rodríguez', 'email': 'david@email.com', 'fecha_creacion': ...}
Topic: cdc.public.clientes | Partition: 0 | Offset: 3
```

---

## 🐍 Consumir Mensajes con Python

### Instalación de Dependencias

Crea `requirements.txt` en la carpeta raíz:

```
confluent-kafka==2.3.0
```

Instala:

```powershell
pip install -r requirements.txt
```

### Script Consumer Mejorado

Opcionalmente, crea un `consumer.py` más robusto con filtering:

```python
#!/usr/bin/env python3
import json
from confluent_kafka import Consumer, KafkaError
from datetime import datetime

class KafkaConsumer:
    def __init__(self, bootstrap_servers='localhost:9092', topic='cdc.public.clientes'):
        self.config = {
            'bootstrap.servers': bootstrap_servers,
            'group.id': f'python-consumer-{datetime.now().timestamp()}',
            'auto.offset.reset': 'earliest',
            'enable.auto.commit': True
        }
        self.consumer = Consumer(self.config)
        self.topic = topic
        self.consumer.subscribe([topic])
    
    def handle_message(self, msg):
        """Procesa un mensaje de Kafka"""
        value = json.loads(msg.value().decode('utf-8'))
        payload = value.get('payload', {})
        
        return {
            'operation': payload.get('op'),
            'before': payload.get('before'),
            'after': payload.get('after'),
            'timestamp': payload.get('ts_ms'),
            'database': value.get('database'),
        }
    
    def consume(self, filter_op=None):
        """
        Consume mensajes
        filter_op: None (todos), 'c' (create), 'u' (update), 'd' (delete)
        """
        print(f"Escuchando {self.topic}...")
        try:
            while True:
                msg = self.consumer.poll(timeout=1.0)
                if msg is None:
                    continue
                if msg.error():
                    print(f"Error: {msg.error()}")
                    break
                
                data = self.handle_message(msg)
                if filter_op is None or data['operation'] == filter_op:
                    print(json.dumps(data, indent=2))
        except KeyboardInterrupt:
            print("\nDetenido")
        finally:
            self.consumer.close()

if __name__ == '__main__':
    consumer = KafkaConsumer()
    consumer.consume()
```

---

## 🔍 Troubleshooting

### ❌ Error: "Connection refused on 8083"

**Causa**: Kafka Connect no está corriendo.

**Solución**:
```powershell
docker-compose ps  # Verifica estado
docker-compose logs kafka-connect  # Ve los logs
docker-compose up -d kafka-connect  # Reinicia
```

---

### ❌ Error: "Topic 'cdc.public.clientes' not found"

**Causa**: El connector no está configurado o no ha procesado cambios.

**Solución**:
```powershell
# Verifica connector
Invoke-WebRequest -Uri "http://localhost:8083/connectors" -Method GET

# Si no existe, vuelve a crear (ver Configuración de Kafka Connect)
# Si existe, genera un cambio en PostgreSQL:
docker exec -it postgres psql -U postgres -d demo -c "INSERT INTO clientes (nombre, email) VALUES ('Test', 'test@email.com');"
```

---

### ❌ Error en Python: "broker: Unknown member"

**Causa**: El consumer group está desincronizado.

**Solución**:
```python
# En consumer.py, cambia group.id cada ejecución:
'group.id': f'python-consumer-{int(time.time())}',

# O resetea el group:
docker exec kafka kafka-consumer-groups --bootstrap-server localhost:9092 --group my-group --reset-offsets --to-earliest --execute
```

---

### ❌ PostgreSQL no conecta desde fuera

**Causa**: Puerto incorrecto o credenciales.

**Solución**:
```powershell
# Verifica puerto en docker-compose.yml
# KRAFT: 51438
# Zookeeper: 51438

# Prueba conexión:
docker exec -it postgres psql -U postgres -d demo -c "SELECT 1;"
```

---

### ⚠️ Consumer recibe mensajes vacíos

**Causa**: Offset al final del topic.

**Solución**:
```python
# En consumer.py:
'auto.offset.reset': 'earliest'  # Cambia de 'latest' a 'earliest'
```

---

## 📚 Comandos Útiles

### Docker Compose

```powershell
# Levanta todo
docker-compose up -d

# Detiene sin borrar
docker-compose down

# Detiene y borra todo
docker-compose down -v

# Ver logs
docker-compose logs -f kafka-connect

# Ver estado
docker-compose ps
```

### Kafka Connect

```powershell
# Listar connectors
Invoke-WebRequest -Uri "http://localhost:8083/connectors" -Method GET

# Ver estado de un connector
Invoke-WebRequest -Uri "http://localhost:8083/connectors/postgres-connector/status" -Method GET

# Pausar connector
Invoke-WebRequest -Uri "http://localhost:8083/connectors/postgres-connector/pause" -Method PUT

# Reanudar connector
Invoke-WebRequest -Uri "http://localhost:8083/connectors/postgres-connector/resume" -Method PUT

# Eliminar connector
Invoke-WebRequest -Uri "http://localhost:8083/connectors/postgres-connector" -Method DELETE
```

### PostgreSQL

```powershell
# Conectar a la BD
docker exec -it postgres psql -U postgres -d demo

# Ejecutar SQL directo
docker exec -it postgres psql -U postgres -d demo -c "SELECT * FROM clientes;"

# Listar tablas
docker exec -it postgres psql -U postgres -d demo -c "\dt"
```

---

## 📖 Resumen del Flujo Completo

```
PostgreSQL (Change)
        ↓
Debezium/Kafka Connect (Captura)
        ↓
Kafka Brokers (Almacenamiento)
        ↓
Kafka UI (Visualización)    ← http://localhost:51439
        ↓
Python Consumer (Lectura)   ← consumer.py
```

---

## 🎓 Próximos Pasos

1. **Escalabilidad**: Añade múltiples consumers para procesar en paralelo
2. **Transformaciones**: Usa Kafka Streams para transformar datos
3. **Persistencia**: Conecta Kafka a bases de datos (ksqlDB)
4. **Monitoreo**: Configura alertas con Prometheus + Grafana
5. **Seguridad**: Añade autenticación SSL/SASL

---

## 📞 Referencias

- [Kafka Documentation](https://kafka.apache.org/documentation/)
- [Debezium PostgreSQL Connector](https://debezium.io/documentation/reference/stable/connectors/postgresql.html)
- [Confluent Python Client](https://docs.confluent.io/kafka-clients/python/current/overview.html)
- [Kafka UI Docs](https://docs.kafka-ui.arenadata.io/)

---

**Última actualización**: Junio 2024 | **Versiones**: Kafka 7.5.0, Debezium 2.5, Python 3.8+
