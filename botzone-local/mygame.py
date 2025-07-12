import sys
from copy import deepcopy
import execjs
import json
import os
import subprocess

from botzone import Env
from botzone.error import *
from botzone.online import games
from botzone.online.viewer.viewer import *
from botzone.online.game import GameConfig


class MyGame(Env):
    '''
    This class provides a universal wrapper for games online.
    '''

    metadata = {'render.modes': ['ansi']}

    def __init__(self, config):
        '''
        Create game instance from GameConfig.

        Parameters:
            config - GameConfig instance.
        '''
        self.agents = None
        assert isinstance(config, GameConfig), 'Parameter config must be GameConfig instance!'
        self.config = config
        self.judge_cmd = self.config.judge_path
        if sys.platform == "win32" and self.judge_cmd.endswith(".elfbin"):
            self.judge_cmd = self.judge_cmd.removesuffix(".elfbin") + ".exe"

        # internal state
        self.log = None
        self.requested_keep_running = True
        self.display = []
        self.viewer = None

    def run_judge(self, input_text):
        from judge_lib import judge
        stdout = judge(input_text)

        output = stdout.strip()
        return {
            'keep_running': True,
            'verdict': 'OK',
            'output': output
        }

    def run_judge_by_process(self, input_text):
        p = subprocess.Popen([self.judge_cmd], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        stdout, stderr = p.communicate(input_text, timeout=5)

        output = stdout.strip()
        return {
            'keep_running': True,
            'verdict': 'OK',
            'output': output
        }

    @property
    def player_num(self):
        return self.config.player

    def reset(self, initdata=''):
        if self.agents is None:
            raise AgentsNeeded()
        # Initialize each agent
        for agent in self.agents:
            agent.reset()

        # Run judge for the first time
        self.requested_keep_running = False
        if initdata is None: initdata = ''
        input = dict(log=[], initdata=initdata)
        input = json.dumps(input)
        output = self.run_judge(input)
        self.log = [output]
        self.display = []

        # parse output from wrapper
        print(output)
        if output['keep_running']:
            self.requested_keep_running = True
        if output['verdict'] != 'OK':
            print('Judge:', output['verdict'], ', Log:')
            print(output)
            raise RuntimeError('Unexpected judge failure')
        response = output['output']
        try:
            response = json.loads(response)
        except:
            print('Judge: Malformed Json, Log:')
            print(response)
            raise RuntimeError('Unexpected judge failure')
        output['output'] = response

        # parse output from judge: command+content+display+initdata
        self.display.append(response.get('display', None))
        if response['command'] == 'finish':
            # game over, return score
            self.log = None
            return tuple(response['content'][str(i)] for i in range(self.config.player))
        if response['command'] != 'request':
            print('Judge: Unrecognized command, Log:')
            print(response)
            raise RuntimeError('Unexpected judge failure')
        if 'initdata' in response:
            # initdata from judge override original one
            self.initdata = response['initdata']
        else:
            self.initdata = initdata

        if self.viewer: self.viewer.reset(self.initdata)

    def step(self):
        if self.log is None:
            raise ResetNeeded()

        # run each agent
        responses = {}
        for i, request in self.log[-1]['output']['content'].items():
            # deepcopy for safety
            response = deepcopy(self.agents[int(i)].step(deepcopy(request)))
            responses[i] = dict(verdict='OK' if response is not None else 'ERR', response=response)
        self.log.append(responses)

        # run judge
        if self.requested_keep_running:
            input = responses
        else:
            input = dict(log=self.log, initdata=self.initdata)
        input = json.dumps(input)
        output = self.run_judge(input)
        self.log.append(output)

        # parse output from wrapper
        if output['keep_running']:
            self.requested_keep_running = True
        if output['verdict'] != 'OK':
            print('Judge:', output['verdict'], ', Log:')
            print(output)
            raise RuntimeError('Unexpected judge failure')
        response = output['output']
        try:
            response = json.loads(response)
        except:
            print('Judge: Malformed Json, Log:')
            print(response)
            raise RuntimeError('Unexpected judge failure')
        output['output'] = response

        # parse output from judge: command+content+display+initdata
        self.display.append(response.get('display', None))
        if response['command'] == 'finish':
            # game over, return score
            self.log = None
            return tuple(response['content'][str(i)] for i in range(self.config.player))
        if response['command'] != 'request':
            print('Judge: Unrecognized command, Log:')
            print(response)
            raise RuntimeError('Unexpected judge failure')

    def close(self):
        pass

    def render(self, mode='ansi'):
        if mode == 'ansi':
            if self.viewer is None:
                self.viewer = TextViewer.make(self.config.name)
                if self.viewer: self.viewer.reset(self.initdata)
            if self.viewer:
                self.viewer.render(self.display)
                self.display = []
            else:
                print(self.display[-1])
        else:
            super(MyGame, self).render(mode)
