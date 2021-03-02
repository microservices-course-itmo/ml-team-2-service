from kafka import KafkaConsumer
from json import loads

TOPIC = 'eventTopic'
BOOTSTRAP_SERVER = ['localhost:9092']
AUTO_OFFSET_RESET = 'earliest' # after breaking down consumer restarts reading at the latest commit offset
ENABLE_AUTO_COMMIT = True # makes sure the consumer commits its read offset every interval
AUTO_COMMIT_INTERVAL = 1 # 1 second
GROUP_ID = 'my-group' # consumer needs to be a part of a consumer group

consumer = KafkaConsumer(
    TOPIC,
    bootstrap_servers=BOOTSTRAP_SERVER,
    #auto_offset_reset=AUTO_OFFSET_RESET,
    #enable_auto_commit=ENABLE_AUTO_COMMIT,
    group_id=GROUP_ID,
)

for message in consumer:
    message = message.value
    print(message)