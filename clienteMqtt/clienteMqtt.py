import asyncio
import ssl
import os
import logging
import aiomqtt

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s: %(message)s %(task_name)s',
                    level=logging.INFO,
                    datefmt='%d/%m/%Y %H:%M:%S %z')
    
async def process_topic_1(message):
    logging.info(f'Received message in topic 1: {message.payload}')

async def process_topic_2(message):
    logging.info(f'Received message in topic 2: {message.payload}')


async def counter_publisher(topic, client):
    counter = 0
    while True:
        await asyncio.sleep(5)
        counter += 1
        await client.publish(topic, str(counter).encode())

async def counter_incrementer():
    counter = 0
    while True:
        await asyncio.sleep(3)
        counter += 1
        logging.info(f'Counter value: {counter}')

async def main():
    # Lee la variable de entorno para MQTT_SERVER
    server_address = os.environ.get('MQTT_SERVER')
    if not server_address:
        logging.error('MQTT_SERVER environment variable not set')
        return
    
    # Lee las variables de entorno para los tópicos
    topic_subscribe_1 = os.environ.get('TOPIC_SUBSCRIBE_1')
    topic_subscribe_2 = os.environ.get('TOPIC_SUBSCRIBE_2')
    topic_publish = os.environ.get('TOPIC_PUBLISH')
    
    if not topic_subscribe_1 or not topic_subscribe_2 or not topic_publish:
        logging.error('One or more required environment variables are not set')
        return
    
    # Crea la conexión tls
    tls_context = ssl.create_default_context()
    tls_context.verify_mode = ssl.CERT_REQUIRED
    tls_context.check_hostname = True
    tls_context.load_default_certs()

    # Crea el cliente
    async with aiomqtt.Client(
        server_address,
        port=8883,
        tls_context=tls_context,
    ) as client:
        
        await client.subscribe(topic_subscribe_1)
        await client.subscribe(topic_subscribe_2)

        async with asyncio.TaskGroup() as tg:
            # Definir las corrutinas para procesar los mensajes de los tópicos
            async def handle_topic_1():
                async for message in client.messages:
                    if message.topic == topic_subscribe_1:
                        await process_topic_1(message)
            
            async def handle_topic_2():
                async for message in client.messages:
                    if message.topic == topic_subscribe_2:
                        await process_topic_2(message)
            
            # Crear corrutinas específicas para manejar cada tópico
            tg.create_task(handle_topic_1())
            tg.create_task(handle_topic_2())

            # Corrutina para publicar el estado del contador
            tg.create_task(counter_publisher(topic_publish, client), name='counter_publisher')

            # Corrutina para incrementar el contador
            tg.create_task(counter_incrementer(), name='counter_incrementer')

if __name__ == "main":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info('Received keyboard interrupt, exiting...')