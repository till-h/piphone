#!/bin/env python
class Controller:

    def __init__(self):
        self._fsm_table = {
            'ready': {
                'event': {
                    'receiver_lifted': {
                        'action': None,
                        'next_state': 'lifted'
                    },
                    'receiver_replaced': {
                        'action': None,
                        'next_state': 'ready'
                    }
                }
            },
            'lifted': {
                'event': {
                    'dialpad_activated': {
                        'action': None,
                        'next_state': 'dialling' #dialpad.states['dialling'] # dialpad fsm
                    }
                }
            },
            'calling': {
                'event': {
                    'receiver_replaced': {
                        'action': self.end_call,
                        'next_state': 'ready'
                    }
                }
            },
            'dialling': { # for development
                'event': {
                    'dialpad_deactivated': {}
                    'number_dialled': {}
            }
        }
        self.state = self._fsm_table['ready']

    def end_call():
        print("Asked browser to end call")
        
    def run(self):
        
