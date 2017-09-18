import logging
import traceback
import json
from kafka import KafkaConsumer
from app.config import XChatKafka

logger = logging.getLogger(__name__)


class XChatMsgsConsumer(object):
    def __init__(self, app=None, config=None):
        self._consumer = None
        self.app = app
        self.config: XChatKafka = config
        if app is not None:
            self.init_app(app, config)

    def init_app(self, app, config: XChatKafka):
        self.app = app
        self.config = config

    @property
    def consumer(self):
        if self._consumer:
            return self._consumer
        config = self.config
        if config.AUTO_OFFSET_RESET == 'latest':
            self._consumer = KafkaConsumer(config.CS_MSGS_TOPIC,
                                           group_id=config.CONSUMER_GROUP,
                                           auto_offset_reset=config.AUTO_OFFSET_RESET,
                                           bootstrap_servers=config.BOOTSTRAP_SERVERS,
                                           value_deserializer=lambda m: json.loads(m)
                                           )
        elif config.AUTO_OFFSET_RESET == 'earliest':
            self._consumer = KafkaConsumer(config.CS_MSGS_TOPIC,
                                           auto_offset_reset=config.AUTO_OFFSET_RESET,
                                           enable_auto_commit=False,
                                           bootstrap_servers=config.BOOTSTRAP_SERVERS,
                                           value_deserializer=lambda m: json.loads(m)
                                           )
        return self._consumer

    def start(self):
        with self.app.app_context():
            self.run()

    def run(self):
        """消费来自xchat的消息"""
        from app.biz.xchat import handle_xchat_msg

        for message in self.consumer:
            try:
                logger.info('%d, %s, %s', message.offset, message.key, message.value)
                # chat_id = str(message.key)
                handle_xchat_msg(message.value)
            except:
                traceback.print_exc()
