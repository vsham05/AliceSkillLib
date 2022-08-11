from flask import Flask, request, Blueprint
from flask_classful import FlaskView, route
import logging
import requests
import json
import os
from random import choice

def build_default_response():
    return {'response_text': '', 'next_scene': '', 'photos': []}


post = Blueprint('post', __name__)


class Button():
    def __init__(self, title, payload=None, url=None, hide=False):
        self.title = title
        self.payload = payload
        self.url = url
        self.hide = hide
    
    def get_button_object(self):
        answer = {'title': self.title, 'hide': self.hide}
        if self.url is not None:
            answer['url'] = self.url
        if self.payload is not None:
            answer['payload'] = self.payload
        
        return answer


class AliceVariable():
    def __init__(self, name, value, skill):
        self.name = name
        self.value = value
        self.skill = skill
        
    def __iadd__(self, other):
        self.skill.dialogs[self.skill.current_id].variables[self.name].value += other
        return self
    
    def __isub__(self, other):
        self.skill.dialogs[self.skill.current_id].variables[self.name].value -= other
        return self
    
    def __imul__(self, other):
        self.skill.dialogs[self.skill.current_id].variables[self.name].value *= other
        return self
    
    def __ifloordiv__(self, other):
        self.skill.dialogs[self.skill.current_id].variables[self.name].value //= other
        return self

    def __idiv__(self, other):
        self.skill.dialogs[self.skill.current_id].variables[self.name].value /= other
        return self
    
    def __ipow__(self, other):
        self.skill.dialogs[self.skill.current_id].variables[self.name].value **= other
        return self
    
    def __imod_(self, other):
        self.skill.dialogs[self.skill.current_id].variables[self.name].value %= other
        return self
    
    def __str__(self):
        return self.value

    
class Scene():
    def __init__(self, name, skill, scenary, buttons=[]):
        self.name = name
        self.scenary = scenary
        skill.add_scene(self)
        self.buttons = [button.get_button_object() for button in buttons]
    
    def play(self, text, entities, dialog):
        variables = self.scenary.__code__.co_varnames[2:self.scenary.__code__.co_argcount]
        print(dialog.variables)
        result = [text, entities]
        for variable in variables:
            new_var = dialog.variables[variable]
            result += [new_var]
        
        response = self.scenary(*result)
        response['buttons'] = self.buttons 
        return response


class Dialog():
    def __init__(self, user_id, variables, scenes):
        self.user_id = user_id
        self.scenes = scenes
        self.start_scene = self.scenes[0]
        self.current_scene = self.start_scene
        self.variables = variables
        for variable in variables:
            new_value = 'self.' + variable
            exec(f"{new_value} = AliceVariable(variables[variable].name, variables[variable].value, variables[variable].skill)")
        
        self.response = {
                        'session': request.json['session'],
                        'version': request.json['version'],
                        'response': {
                        'end_session': False
                                    }
                    }

    
    def play_scene(self, req):
        text = req['request']['original_utterance']
        entities = req['request']['nlu']['entities']
        data = self.current_scene.play(text, entities, self)
        self.response['response']['text'] = data['response_text']
        self.response['response']['buttons'] = data['buttons']
        if data['next_scene'] == 'END':
            self.response['response']['end_session'] = True
            return
        for scene in self.scenes:
            if scene.name == data['next_scene']:
                self.current_scene = scene
        
        return 

    def add_variable(self, variable, value):
        exec("%s = %d" % (variable, value))
    
    def get_response(self):
        return self.response


class AliceView(FlaskView):
    def __init__(self):
        self.dialogs = {}
        self.variables = {}
        self.host = '127.0.0.1'
        self.port = 5000
        self.app = Flask(__name__)
        print(self.app.url_map)
        self.app.register_blueprint(post, url_prefix='/post')
        self.scenes = []
        self.start_scene = None
    
    def set_host(self, host):
        self.host = host
    
    def add_scene(self, *scenes):
        self.scenes += scenes

    def set_port(self, port):
        self.port = port

    def add_scene(self, *scenes):
        self.scenes += scenes

    def add_variables(self, **variables):
        self.variables = {**self.variables, **variables}
        for variable in variables:
            new_value = 'self.' + variable
            self.variables[variable] = AliceVariable(variable, variables[variable], self)
            exec(f"{new_value} = AliceVariable(variable, variables[variable], self)")
        
    
    def synhronize(self, dialogs, user_id):
        self.dialogs = dialogs
        self.current_id = user_id
    
        

skill = AliceView()
current_app = Flask(__name__)
dialogs = {}


@current_app.route('/post', methods=['POST', 'GET'])
def post():
    global skill, dialogs
    req = request.json
    response = str(len(skill.scenes))
    

    if request.method == "POST":
        req = request.json
        user_id = req['session']['user_id']
        skill.synhronize(dialogs, user_id)
        if req['session']['new']:
            dialogs[user_id] = Dialog(user_id=user_id, variables=skill.variables, scenes=skill.scenes)
            dialogs[user_id].play_scene(req)
        else:
            dialogs[user_id].play_scene(req)


        
        response = dialogs[user_id].get_response()
    print(response)
        
    return response

def start_skill(host, port):
    global current_app
    current_app.run(host=host, port=port)