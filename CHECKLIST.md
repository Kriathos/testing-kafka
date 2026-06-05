# ✅ CHECKLIST DE IMPLEMENTACIÓN - Kafka CDC

Sigue este checklist paso a paso para implementar Kafka con CDC.

## 🔧 PRE-REQUISITOS

### Software Instalado
- [ ] Docker Desktop corriendo
- [ ] Python 3.8+ instalado (verificar con `python --version`)
- [ ] PowerShell 7+ o cmd disponible
- [ ] Git (opcional pero recomendado)

### Espacio y Recursos
- [ ] Mínimo 4GB RAM disponibles
- [ ] Mínimo 2GB espacio en disco
- [ ] Puertos libres: 8080, 8083, 5432, 9092, 51438, 51439

---

## 🚀 PASO 1: LEVANTAR KAFKA + POSTGRESQL

### 1.1 Elegir la Configuración
- [ ] Decisión: ¿KRAFT (recomendado) o Zookeeper?
- [ ] KRAFT: Más moderno, 3 brokers
- [ ] Zookeeper: Tradicional, 1 broker

### 1.2 Navegar a la Carpeta
```powershell
# KRAFT
cd C:\Users\<usuario>\kafka\kraft

# O Zookeeper
cd C:\Users\<usuario>\kafka\zookeeper
```
- [ ] Estás en la carpeta correcta

### 1.3 Levantar Containers
```powershell
docker-compose up -d
```
- [ ] Comando ejecutado sin errores

### 1.4 Verificar que Todo Corre
```powershell
docker-compose ps
```
- [ ] Todos los containers tienen estado "Up"
  - kafka (o kafka1, kafka2, kafka3 en KRAFT)
  - postgres
  - kafka-connect
  - kafka-ui
  - zookeeper (si elegiste Zookeeper)

---

## 🗄️ PASO 2: CREAR TABLA EN POSTGRESQL

### 2.1 Conectar a PostgreSQL
```powershell
docker exec -it postgres psql -U postgres -d demo
```
- [ ] Estás dentro del prompt `postgres=#` o `demo=#`

### 2.2 Ejecutar SQL
```sql
CREATE TABLE clientes (
  id SERIAL PRIMARY KEY,
  nombre VARCHAR(100) NOT NULL,
  email VARCHAR(100),
  fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO clientes (nombre, email) VALUES ('Juan Pérez', 'juan@email.com');
INSERT INTO clientes (nombre, email) VALUES ('María García', 'maria@email.com');

SELECT * FROM clientes;
```
- [ ] Tabla creada sin errores
- [ ] 2 filas insertadas
- [ ] SELECT muestra los datos

### 2.3 Salir de PostgreSQL
```sql
\q
```
- [ ] De vuelta en PowerShell

---

## 🔗 PASO 3: CONFIGURAR KAFKA CONNECT

### 3.1 Crear Connector en PowerShell
```powershell
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
- [ ] Comando ejecutado
- [ ] Respuesta en JSON (sin errores)

### 3.2 Verificar que se Creó
```powershell
Invoke-WebRequest -Uri "http://localhost:8083/connectors/postgres-connector/status" -Method GET
```
- [ ] Estado muestra: `"state": "RUNNING"` (puede tardar 10 segundos)
- [ ] Si falla, espera 30 segundos y reintenta

---

## 👁️ PASO 4: VERIFICAR EN KAFKA UI

### 4.1 Abrir Kafka UI
- [ ] Abre en navegador: http://localhost:51439
- [ ] Se carga sin errores

### 4.2 Verificar Topics
- [ ] Click en "Topics" (sidebar izquierdo)
- [ ] Busca topics que empiezan con `cdc`
  - `cdc-configs` ✓
  - `cdc-offsets` ✓
  - `cdc-status` ✓
  - `cdc.public.clientes` ✓ (Este es el importante)

### 4.3 Verificar Mensajes Iniciales
- [ ] Click en `cdc.public.clientes`
- [ ] Deberías ver 2 mensajes (los inserts iniciales)
- [ ] Cada mensaje muestra el JSON con `payload.after` con los datos

---

## 🧪 PASO 5: PRUEBA 1 - CAMBIOS EN TIEMPO REAL

### 5.1 Hacer un Cambio en PostgreSQL
```powershell
docker exec -it postgres psql -U postgres -d demo -c "
INSERT INTO clientes (nombre, email) VALUES ('Carlos López', 'carlos@email.com');"
```
- [ ] Comando ejecutado

### 5.2 Ver en Kafka UI
- [ ] Actualiza Kafka UI (F5 o reload)
- [ ] El topic `cdc.public.clientes` ahora muestra 3 mensajes
- [ ] El nuevo mensaje contiene: `id=3, nombre='Carlos López', email='carlos@email.com'`

### 5.3 Más Cambios (Update y Delete)
```powershell
# Update
docker exec -it postgres psql -U postgres -d demo -c "
UPDATE clientes SET email = 'juan.nuevo@email.com' WHERE id = 1;"

# Delete
docker exec -it postgres psql -U postgres -d demo -c "DELETE FROM clientes WHERE id = 2;"
```
- [ ] UPDATE visible en Kafka UI (operación: "u")
- [ ] DELETE visible en Kafka UI (operación: "d")

---

## 🐍 PASO 6: PYTHON CONSUMER

### 6.1 Instalar Dependencias
```powershell
cd C:\Users\<usuario>\kafka
pip install -r requirements.txt
```
- [ ] `confluent-kafka` instalado sin errores

### 6.2 Ejecutar Consumer
```powershell
python consumer.py
```
- [ ] Se conecta a Kafka
- [ ] Se muestra: "✅ Conectado a Kafka en localhost:9092"
- [ ] Se muestra: "📥 Escuchando topic: cdc.public.clientes"

### 6.3 Ver Mensajes Anteriores
- [ ] El consumer muestra todos los mensajes previos (INSERT, UPDATE, DELETE)
- [ ] Formato: operación, antes, después

### 6.4 Generar Nuevos Cambios
En **otra terminal PowerShell**:
```powershell
docker exec -it postgres psql -U postgres -d demo -c "
INSERT INTO clientes (nombre, email) VALUES ('Rosa García', 'rosa@email.com');"
```

De vuelta en la terminal del consumer:
- [ ] Aparece el nuevo mensaje en **tiempo real**
- [ ] Formato: `➕ CREATE`, con los datos de Rosa

### 6.5 Detener Consumer
```powershell
Ctrl+C
```
- [ ] Se cierra gracefully con "👋 Consumer detenido"

---

## 🎯 PASO 7: PRUEBA COMPLETA (Opcional)

### 7.1 Crear Multiple Inserts
```powershell
# Terminal 1: Consumer corriendo
python consumer.py --verbose

# Terminal 2: Hacer cambios
docker exec postgres psql -U postgres -d demo -c "
INSERT INTO clientes (nombre, email) VALUES 
  ('Cliente 1', 'c1@test.com'),
  ('Cliente 2', 'c2@test.com'),
  ('Cliente 3', 'c3@test.com');"
```
- [ ] Consumer recibe y muestra todos los cambios en tiempo real

### 7.2 Probar Filtering (Opcional)
```powershell
# Solo CREATE
python consumer.py --filter c

# Solo UPDATE
python consumer.py --filter u

# Solo DELETE
python consumer.py --filter d
```
- [ ] Filtering funciona correctamente

### 7.3 Probar Verbose Mode (Opcional)
```powershell
python consumer.py --verbose
```
- [ ] Se muestra información adicional: timestamps, partition, offset

---

## 🧹 PASO 8: LIMPIEZA

### 8.1 Detener Containers (Sin Borrar Datos)
```powershell
docker-compose down
```
- [ ] Todos los containers detenidos

### 8.2 Reiniciar (Sin Perder Datos)
```powershell
docker-compose up -d
```
- [ ] Containers se reinician
- [ ] Datos persisten (mismos topics, mensajes, tabla)

### 8.3 Borrar Todo (Limpieza Completa)
```powershell
docker-compose down -v
```
- [ ] Todos los containers, volúmenes y networks eliminados
- [ ] Empieza desde cero

---

## ✅ CONCLUSIÓN

- [ ] Kafka levantado y corriendo
- [ ] PostgreSQL con tabla de prueba
- [ ] Kafka Connect capturando cambios
- [ ] Kafka UI mostrando mensajes
- [ ] Python consumer consumiendo en tiempo real
- [ ] Entiendes el flujo: PostgreSQL → Debezium → Kafka → Consumer

---

## 📝 NOTAS

- **Problema con permisos en PostgreSQL**: Ver [TROUBLESHOOTING](#troubleshooting) en README.md
- **Connector no inicia**: Verifica logs con `docker-compose logs kafka-connect`
- **Consumer no recibe mensajes**: Asegúrate que has insertado datos DESPUÉS de crear el connector
- **Puerto 8083 no responde**: Espera 30 segundos a que Kafka Connect inicie

---

**¡Listo! Ya tienes un sistema CDC funcional. 🎉**
