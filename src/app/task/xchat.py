import logging
import traceback
import json
from kafka import KafkaConsumer
from app.config import XChatKafka


logger = logging.getLogger(__name__)


class XChatMsgsConsumer(object):
    def __init__(self, app=None, config=None):
        self.consumer = None
        self.app = app
        if app is not None:
            self.init_app(app, config)

    def init_app(self, app, config: XChatKafka):
        self.app = app
        self.consumer = KafkaConsumer(config.CS_MSGS_TOPIC,
                                      group_id=config.CONSUMER_GROUP,
                                      bootstrap_servers=config.BOOTSTRAP_SERVERS)

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
                data = json.loads(message.value)
                handle_xchat_msg(data)
            except:
                traceback.print_exc()
