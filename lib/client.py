import abc
import os
import sys
import inspect
import re
from lib import RedisCache


ACTION_PREFIX = 'action_'
ALL_SOURCES = ['user', 'group', 'room']
TEXT_CLIENT_COMMAND_PREFIX = '/'

class Term():

    def __init__(self, function, sources=ALL_SOURCES, search=[]):
        self.function = function
        self.sources = sources
        self.search = search


class BaseClient(metaclass=abc.ABCMeta):

    def __init__(self, module):
        self.module = module
        self.commands = {}
        self.states = {}
    
    def _load(self):
        for name, action in inspect.getmembers(sys.modules[self.module]):
            if re.compile("^{}([a-zA-Z0-9\_])*$".format(ACTION_PREFIX)).match(name):
                action()

    def before_start(self, bot, event):
        self._load()
        self.bot = bot
        self.event = event
        self.state = RedisCache(event)

    @abc.abstractmethod
    def run_from_command(self, options={}):
        return False

    def run(self, bot, event, options={}):
        self.before_start(bot, event)
        if (not self.run_from_state()):
            return self.run_from_command(options)
        return True

    def run_from_state(self):
        state = self.state.get_state()
        if (state and state in self.states):
            if (self.event.source.type in self.states[state].sources):
                self.states[state].function()
                return True
        return False

    def on_state(self, state, sources=ALL_SOURCES):
        def decorate(function):
            def wrapper(*args):
                self.states[state] = Term(function, sources=sources)
            return wrapper
        return decorate


class StandardClient(BaseClient):

    def run_from_command(self, options={}):
        if (self.event.source.type in self.command.sources):
            self.command.function()
            return True
        return False

    def on_command(self, sources=ALL_SOURCES):
        def decorate(function):
            def wrapper(*args):
                self.command = Term(function, sources=sources)
            return wrapper
        return decorate


class TextClient(BaseClient):

    def run_from_command(self, options={}):
        message_text = options['message_text'] if 'message_text' in options else self.event.message.text
        messages = message_text.split()
        command = messages[0].lower()
        if (command in self.commands):
            if (self.event.source.type in self.commands[command].sources):
                if (len(messages) > 1):
                    self.commands[command].function(' '.join(messages[1:]))
                else:
                    self.commands[command].function()
                return True
        return False

    def on_command(self, command, sources=ALL_SOURCES):
        command = '{}{}'.format(TEXT_CLIENT_COMMAND_PREFIX, command)
        def decorate(function):
            def wrapper(*args):
                self.commands[command] = Term(function, sources=sources)
            return wrapper
        return decorate


class SimpleWitClient(BaseClient):

    def run_from_command(self, options={}):
        if (not 'wit_response' in options):
            raise Exception('wit_response not found in options')
        
        self.wit_response = options['wit_response']
        entity_objects = self.wit_response.get('entities')
        for entity, value_objects in entity_objects.items():
            if (entity in self.commands):
                if (self.event.source.type in self.commands[entity].sources):
                    self.commands[entity].function(value_objects[0]['value'])
                    return True
        return False

    def on_command(self, command, sources=ALL_SOURCES):
        def decorate(function):
            def wrapper(*args):
                self.commands[command] = Term(function, sources=sources)
            return wrapper
        return decorate


class AdvancedWitClient(BaseClient):

    def run_from_command(self, options={}):
        if (not 'wit_response' in options):
            raise Exception('wit_response not found in options')

        # get entities from resp
        self.wit_response = options['wit_response']
        entity_objects = self.wit_response.get('entities')
        for entity, value_objects in entity_objects.items():

            # check entity in commands
            if (entity in self.commands):

                # loop all values in value_objects
                for value_object in value_objects:

                    # get the real value
                    value = value_object.get('value', None)
                    if (value in self.commands[entity]):

                        # check event source type
                        if (self.event.source.type in self.commands[entity][value].sources):

                            # build arguments from search entities that define in route()
                            arguments = {}
                            for arg in self.commands[entity][value].search:
                                arguments[arg] = entity_objects[arg][0]['value'] if arg in entity_objects else None

                            # execute function based on arguments
                            if (arguments):
                                self.commands[entity][value].function(arguments)
                            else:
                                self.commands[entity][value].function()
                            return True
        return False

    def on_command(self, entity, value, search=[], sources=ALL_SOURCES):
        def decorate(function):
            def wrapper(*args):
                if (not entity in self.commands):
                    self.commands[entity] = {}
                self.commands[entity][value] = Term(function, sources=sources, search=search)
            return wrapper
        return decorate
