#!/usr/bin/env python3
"""
Consumer de Kafka para CDC de PostgreSQL
Captura cambios en tiempo real desde la tabla clientes

Uso:
    python consumer.py
    python consumer.py --topic cdc.public.clientes
    python consumer.py --bootstrap-servers localhost:9092
"""

import json
import argparse
import sys
from confluent_kafka import Consumer, KafkaError
from datetime import datetime


class CDCConsumer:
    """Consumidor de cambios de datos de Kafka + Debezium"""
    
    def __init__(self, bootstrap_servers='localhost:9092', topic='cdc.public.clientes', group_id=None):
        """
        Inicializa el consumer
        
        Args:
            bootstrap_servers: Dirección del broker Kafka
            topic: Topic a consumir
            group_id: Group ID (si es None, genera uno automático)
        """
        self.topic = topic
        self.bootstrap_servers = bootstrap_servers
        
        if group_id is None:
            group_id = f'python-consumer-{int(datetime.now().timestamp() * 1000)}'
        
        self.config = {
            'bootstrap.servers': bootstrap_servers,
            'group.id': group_id,
            'auto.offset.reset': 'earliest',
            'enable.auto.commit': True,
            'session.timeout.ms': 6000,
        }
        
        try:
            self.consumer = Consumer(self.config)
            print(f"✅ Conectado a Kafka en {bootstrap_servers}")
        except Exception as e:
            print(f"❌ Error al conectar a Kafka: {e}")
            sys.exit(1)
    
    def _format_message(self, msg):
        """Parsea y formatea un mensaje de Debezium"""
        try:
            value = json.loads(msg.value().decode('utf-8'))
        except json.JSONDecodeError:
            return None
        
        payload = value.get('payload', {})
        
        # Mapeo de operaciones
        op_map = {
            'c': '➕ CREATE',
            'u': '🔄 UPDATE',
            'd': '❌ DELETE',
            'r': '📖 READ'
        }
        
        operation = payload.get('op', 'unknown')
        operation_text = op_map.get(operation, operation)
        
        return {
            'operation': operation_text,
            'before': payload.get('before'),
            'after': payload.get('after'),
            'timestamp_ms': payload.get('ts_ms'),
            'table': payload.get('table'),
            'database': payload.get('source', {}).get('db'),
        }
    
    def consume(self, max_messages=None, filter_operation=None, verbose=False):
        """
        Consume mensajes del topic
        
        Args:
            max_messages: Número máximo de mensajes a consumir (None = infinito)
            filter_operation: Filtrar por operación ('c', 'u', 'd') o None para todas
            verbose: Mostrar toda la información del mensaje
        """
        self.consumer.subscribe([self.topic])
        print(f"📥 Escuchando topic: {self.topic}")
        print(f"🔧 Group ID: {self.config['group.id']}")
        print(f"⏸️  Presiona Ctrl+C para salir\n")
        print("─" * 70)
        
        message_count = 0
        
        try:
            while True:
                msg = self.consumer.poll(timeout=1.0)
                
                if msg is None:
                    continue
                
                if msg.error():
                    if msg.error().code() == KafkaError._PARTITION_EOF:
                        continue
                    else:
                        print(f"❌ Error de Kafka: {msg.error()}")
                        break
                
                # Formatear mensaje
                formatted = self._format_message(msg)
                if formatted is None:
                    print("⚠️  No se pudo parsear el mensaje")
                    continue
                
                # Filtrar si es necesario
                if filter_operation and not formatted['operation'].startswith(filter_operation):
                    continue
                
                message_count += 1
                
                # Mostrar mensaje
                print(f"\n{formatted['operation']}")
                print(f"Tabla: {formatted['table']} | Base de datos: {formatted['database']}")
                
                if formatted['before'] or formatted['after']:
                    if formatted['before']:
                        print(f"  Antes:  {formatted['before']}")
                    if formatted['after']:
                        print(f"  Después: {formatted['after']}")
                else:
                    print("  (Sin datos)")
                
                if verbose:
                    print(f"  Timestamp: {formatted['timestamp_ms']}")
                    print(f"  Partition: {msg.partition()} | Offset: {msg.offset()}")
                
                print("─" * 70)
                
                if max_messages and message_count >= max_messages:
                    print(f"\n✅ Se alcanzó el límite de {max_messages} mensajes")
                    break
        
        except KeyboardInterrupt:
            print(f"\n\n👋 Consumer detenido. Mensajes procesados: {message_count}")
        
        finally:
            self.consumer.close()
            print("🔌 Conexión cerrada")


def main():
    parser = argparse.ArgumentParser(
        description='Consumer de CDC para Kafka + Debezium',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  python consumer.py
  python consumer.py --topic cdc.public.clientes
  python consumer.py --bootstrap-servers localhost:9092 --verbose
  python consumer.py --max-messages 10
        """
    )
    
    parser.add_argument(
        '--bootstrap-servers',
        default='localhost:9092',
        help='Dirección del broker Kafka (default: localhost:9092)'
    )
    
    parser.add_argument(
        '--topic',
        default='cdc.public.clientes',
        help='Topic a consumir (default: cdc.public.clientes)'
    )
    
    parser.add_argument(
        '--group-id',
        default=None,
        help='Consumer group ID (si no se especifica, genera uno automático)'
    )
    
    parser.add_argument(
        '--max-messages',
        type=int,
        default=None,
        help='Número máximo de mensajes a consumir (default: infinito)'
    )
    
    parser.add_argument(
        '--filter',
        choices=['c', 'u', 'd'],
        default=None,
        help='Filtrar por tipo de operación: c=CREATE, u=UPDATE, d=DELETE'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Mostrar información detallada de los mensajes'
    )
    
    args = parser.parse_args()
    
    # Crear y ejecutar consumer
    consumer = CDCConsumer(
        bootstrap_servers=args.bootstrap_servers,
        topic=args.topic,
        group_id=args.group_id
    )
    
    consumer.consume(
        max_messages=args.max_messages,
        filter_operation=args.filter,
        verbose=args.verbose
    )


if __name__ == '__main__':
    main()
