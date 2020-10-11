import os
from abc import ABC, abstractmethod
from typing import final, List


class MenuEntry(ABC):
    def __init__(self, prompt='', action=lambda: None):
        self._prompt = prompt
        self._action = action
        
    @property
    def prompt(self) -> str:
        return self._prompt
        
    def call(self):
        self._action()
        

class MenuLayer(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        pass
    
    def __init__(self):
        name_len = len(self.name)
        self._header = '\n'.join(
            (
                '=' * (name_len + 6),
                f'-- {self.name} --',
                '=' * (name_len + 6),
            )
        )
        
        self._tail = '=' * (name_len + 6)
        
        self._entries: List[MenuEntry] = list()
    
    @final
    def clear_entries(self):
        self._entries.clear()
        
    @final
    def add_entry(self, entry: MenuEntry):
        self._entries.append(entry)
    
    def _clear(self):
        os.system('clear' if os.name == 'nt' else 'cls')
    
    def call(self):
        self._clear()
        print(self._header)
        for key, entry in enumerate(self._entries, start=1):
            print(f'{key}: {entry.prompt}')
        print(self._tail)
