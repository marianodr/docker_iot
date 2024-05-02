# docker

## Consigna
Crear una imagen con una aplicación asíncronica en python que se comunique con un broker mqtt.

*    recibe por variable de entorno la dirección del servidor (broker)
*    recibe por variables de entorno dos tópicos a los cuales suscribirse.
*    los mensajes de los distintos tópicos se atenderán en sus correspondientes corrutinas. (logg info)
*    recibe por variables de entorno un tópico en el cuál publica cada 5 segundos el estado de un contador.
*    el contador se incrementa cada 3 segundos en una corrutina (task) diferente.
*    no utilizar variables globales.
*    utilizar aiomqtt.
*    crear un solo objeto client.
*    en el formato del logging se deberá incluir el nombre de la corrutina (task) utilizando la etiqueta correspondiente del modulo logging.
*    capturar la excepción al detener con ctrl-c.
*    se crea el contenedor con docker-compose

## Variables de entorno:
- MQTT_SERVER: Servidor MQTT
- TOPIC_SUBSCRIBE_1: Topico 1 al cual se subscribe
- TOPIC_SUBSCRIBE_2: Topico 2 al cual se subscribe
- TOPIC_PUBLISH: Topico en el cual publicará el estado del contador cada 5 segundos

## Aclaración:
Comando para crear el contenedor:
```
docker compose up --build
```