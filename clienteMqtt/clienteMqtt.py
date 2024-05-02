import asyncio
import logging
import os
import ssl
import aiomqtt

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - Corrutina: %(funcName)s - Informacion: %(message)s',
                    level=logging.INFO,
                    datefmt='%d/%m/%Y %H:%M:%S %z')

async def counter_publisher(client, topic, counter_generator):
    async for current_counter in counter_generator():
        await asyncio.sleep(5)
        await client.publish(topic, str(current_counter).encode())

async def counter_incrementer():
    counter = 0
    while True:
        await asyncio.sleep(3)
        counter += 1
        logging.info(f'Counter value: {counter}')
        yield counter

async def topic1_consumer(topico):
    while True:
        message = await topic1_queue.get()
        payload = message.payload.decode("utf-8")
        logging.info(f"{topico} --> {payload}")

async def topic2_consumer(topico):
    while True:
        message = await topic2_queue.get()
        payload = message.payload.decode("utf-8")
        logging.info(f"{topico} --> {payload}")

topic1_queue = asyncio.Queue()
topic2_queue = asyncio.Queue()

async def distributor(client, topic_subs_1, topic_subs_2):
    # Sort messages into the appropriate queues
    async for message in client.messages:
        if message.topic.matches(topic_subs_1):
            topic1_queue.put_nowait(message)
        elif message.topic.matches(topic_subs_2):
            topic2_queue.put_nowait(message)

async def main():
    logging.info("Inicio del sistema...")
    
    servidor = os.environ['MQTT_SERVER']
    topic_subs_1 = os.environ['TOPIC_SUBSCRIBE_1']
    topic_subs_2 = os.environ['TOPIC_SUBSCRIBE_2']
    topic_pub = os.environ['TOPIC_PUBLISH']
    
    tls_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    tls_context.verify_mode = ssl.CERT_REQUIRED
    tls_context.check_hostname = True
    tls_context.load_default_certs()

    async with aiomqtt.Client(
        servidor,
        port=8883,
        tls_context=tls_context,
    ) as client:
        
        await client.subscribe(topic_subs_1)
        await client.subscribe(topic_subs_2)

        async with asyncio.TaskGroup() as tg:            
            tg.create_task(distributor(client, topic_subs_1, topic_subs_2))
            tg.create_task(topic1_consumer(topic_subs_1))
            tg.create_task(topic2_consumer(topic_subs_2))
            tg.create_task(counter_publisher(client, topic_pub, counter_incrementer))

        # Gestiona los mensajes recibidos de forma básica
        #async for message in client.messages:
        #    logging.info(str(message.topic) + ": " + message.payload.decode("utf-8"))

if __name__ == "__main__":
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Detenido por el usuario.")