# 📚 Documentación Kafka CDC - Índice

Bienvenido a la guía completa de Kafka con Change Data Capture (CDC).

---

## 🎯 ¿Por Dónde Empiezo?

### 👤 Soy completamente nuevo en esto
1. Lee [QUICK_START.md](QUICK_START.md) - 5 minutos
2. Sigue [CHECKLIST.md](CHECKLIST.md) - Paso a paso

### 👨‍💼 Necesito implementar rápido
1. [QUICK_START.md](QUICK_START.md) - Comandos listos para copiar/pegar
2. [COMANDOS.ps1](COMANDOS.ps1) - Script con todos los comandos

### 📖 Quiero entender en profundidad
1. [README.md](README.md) - Guía completa con conceptos
2. Ver secciones específicas:
   - [Conceptos Clave](README.md#💡-conceptos-clave)
   - [KRAFT vs Zookeeper](README.md#kraft-vs-zookeeper)
   - [Troubleshooting](README.md#🔍-troubleshooting)

### 🐍 Solo necesito el Consumer Python
1. Ver [consumer.py](consumer.py) - Script completo
2. Instalar: `pip install -r requirements.txt`
3. Ejecutar: `python consumer.py --help`

---

## 📁 Archivos del Proyecto

| Archivo | Propósito | Para Quién |
|---------|-----------|-----------|
| **QUICK_START.md** | Inicia en 5 minutos | Todos |
| **README.md** | Guía completa | Aprendizaje profundo |
| **CHECKLIST.md** | Paso a paso verificable | Implementación rigurosa |
| **COMANDOS.ps1** | Comandos PowerShell listos | Copia/pega rápido |
| **consumer.py** | Script Python CDC | Consumidores |
| **requirements.txt** | Dependencias Python | `pip install` |
| **kraft/** | Docker Compose KRAFT | 3 brokers (nuevo) |
| **zookeeper/** | Docker Compose Zookeeper | 1 broker (tradicional) |

---

## 🏗️ Estructura General

```
📊 Flujo de Datos:
┌─────────────┐
│ PostgreSQL  │  ← Cambios en tabla "clientes"
└──────┬──────┘
       │
       ↓
┌──────────────────┐
│ Debezium/        │  ← Captura cambios en tiempo real
│ Kafka Connect    │
└──────┬───────────┘
       │
       ↓
┌──────────────────┐
│ Kafka Brokers    │  ← Almacena mensajes
│ (KRAFT o ZK)     │
└──────┬───────────┘
       │
       ├─→ Kafka UI          ← Visualizar en web
       │   (http://51439)
       │
       └─→ Python Consumer  ← Leer en tiempo real
           (consumer.py)
```

---

## ⚡ Operaciones Comunes

### Levantar el Sistema
```powershell
cd kraft  # o zookeeper
docker-compose up -d
```
📖 Ver: [QUICK_START.md](QUICK_START.md#1️⃣-levantar-3-comandos)

### Monitorear Topics
Abre http://localhost:51439 en el navegador

### Consumir en Python
```powershell
python consumer.py
```
📖 Ver: [README.md - Consumir Mensajes con Python](README.md#🐍-consumir-mensajes-con-python)

### Hacer Cambios en BD y Verlos en Kafka
```powershell
# Terminal 1: Consumer corriendo
python consumer.py

# Terminal 2: Hacer cambios
docker exec postgres psql -U postgres -d demo -c "INSERT INTO clientes VALUES (...);"
```
📖 Ver: [CHECKLIST.md - Paso 5](CHECKLIST.md#🧪-paso-5--prueba-1---cambios-en-tiempo-real)

---

## 🔧 Requisitos

- Docker Desktop corriendo
- Python 3.8+ (opcional, para consumer)
- PowerShell 7+ o cmd
- 4GB RAM mínimo
- 2GB espacio en disco

📖 Ver: [README.md - Requisitos](README.md#🔧-requisitos)

---

## 🆘 Ayuda Rápida

| Problema | Solución |
|----------|----------|
| No sé por dónde empezar | → [QUICK_START.md](QUICK_START.md) |
| Paso a paso verificable | → [CHECKLIST.md](CHECKLIST.md) |
| Comando específico | → [COMANDOS.ps1](COMANDOS.ps1) |
| Error/Troubleshooting | → [README.md#🔍-troubleshooting](README.md#🔍-troubleshooting) |
| Consumer no funciona | → [consumer.py --help](consumer.py) |
| KRAFT vs Zookeeper | → [README.md#kraft-vs-zookeeper](README.md#kraft-vs-zookeeper) |

---

## 📊 Rutas de Aprendizaje

### 🚀 Inicio Rápido (15 minutos)
1. [QUICK_START.md](QUICK_START.md)
2. Levantar contenedores
3. Hacer un cambio en PostgreSQL
4. Ver en Kafka UI

### 📚 Completo (1-2 horas)
1. [README.md](README.md) - Leer conceptos
2. [CHECKLIST.md](CHECKLIST.md) - Implementar
3. [consumer.py](consumer.py) - Adaptar consumer

### 🏗️ Personalización (Según necesidad)
- Añadir más tablas: Modificar `table.include.list` en connector
- Cambiar BD: Modificar `database.dbname` en PostgreSQL
- Múltiples consumers: Ejecutar `consumer.py` con diferentes `--group-id`

---

## 🔗 Referencias Externas

- **Kafka**: https://kafka.apache.org/
- **Debezium**: https://debezium.io/
- **Confluent Kafka Python**: https://docs.confluent.io/kafka-clients/python/
- **Docker**: https://docs.docker.com/

---

## 💾 Versiones

| Componente | Versión |
|-----------|---------|
| Kafka | 7.5.0 |
| Debezium | 2.5 |
| PostgreSQL | 15 |
| Python | 3.8+ |
| Docker Compose | 3.9 |

---

## 🎓 Tips Profesionales

1. **Siempre usa KRAFT para nuevos proyectos** - Es más moderno y se convertirá en estándar
2. **Monitorea Kafka UI** - Es más útil que comandos para debuggear
3. **Guarda tus connectors** - Documenta la configuración JSON
4. **Usa group_id único** - Evita conflictos entre consumers
5. **Automátiza scripts** - Crea tareas programadas para procesos batch

---

## ✅ Checklist Final

- [ ] He leído [QUICK_START.md](QUICK_START.md)
- [ ] He levantado los containers
- [ ] He creado la tabla de prueba
- [ ] He configurado el connector
- [ ] He visto mensajes en Kafka UI
- [ ] He ejecutado el consumer Python
- [ ] He hecho un cambio y lo vi en tiempo real

---

**¿Preguntas?** Consulta [README.md](README.md) o [CHECKLIST.md](CHECKLIST.md)

**Última actualización**: Junio 2026
