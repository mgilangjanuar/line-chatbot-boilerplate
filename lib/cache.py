import redis as r
import json

class RedisCache():

    def __init__(self, event, redis=None):
        self.event = event
        self.redis = r.StrictRedis() if redis is None else redis

    @property
    def _state_key(self):
        return '{}/{}'.format(self.event.source.type, self._message_id)

    @property
    def _data_key(self):
        return '{}/data'.format(self._state_key)

    @property
    def _message_id(self):
        if (self.event.source.type == 'room'):
            return self.event.source.room_id
        elif (self.event.source.type == 'group'):
            return self.event.source.group_id
        else:
            return self.event.source.user_id

    def get_state(self):
        state = self.redis.get(self._state_key)
        return state.decode('utf-8') if state else None

    def set_state(self, value):
        if (value):
            self.redis.set(self._state_key, value)
        else:
            self.delete()

    def delete_state(self):
        self.redis.delete(self._state_key)

    def get_data(self):
        state = self.redis.get(self._data_key)
        return json.loads(state.decode('utf-8')) if state else None
    
    def set_data(self, data):
        self.redis.set(self._data_key, json.dumps(data))

    def delete_data(self):
        self.redis.delete(self._data_key)
