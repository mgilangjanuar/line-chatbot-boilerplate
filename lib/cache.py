import redis
import json

class RedisCache():

    def __init__(self, event):
        self.event = event
        self.redis = redis.StrictRedis()

    @property
    def _key(self):
        return '{}/{}'.format(self.event.source.type, self._message_id)

    @property
    def _message_id(self):
        if (self.event.source.type == 'room'):
            return self.event.source.room_id
        elif (self.event.source.type == 'group'):
            return self.event.source.group_id
        else:
            return self.event.source.user_id

    def get_state(self):
        state = self.redis.get(self._key)
        return state.decode('utf-8') if state else None

    def set_state(self, value):
        if (value):
            self.redis.set(self._key, value)
        else:
            self.delete()

    def get_data(self):
        state = self.redis.get('{}/data'.format(self._key))
        return json.loads(state.decode('utf-8')) if state else None
    
    def set_data(self, data):
        self.redis.set('{}/data'.format(self._key), json.dumps(data))

    def delete(self):
        self.redis.delete(self._key)
