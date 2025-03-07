from PyQt5.QtCore import QObject

singleton = None

class Rtti(QObject):
    def __new__(cls):
        global singleton
        if singleton is None:
            singleton = super().__new__(cls)
        return singleton
    
    def __init__(self):
        self._rttiTypes = {}
       
    @staticmethod
    def types():
        return Rtti._instance()._types()
    
    def _types(self):
        return self._rttiTypes
        
    @staticmethod
    def add_type(scoped_name: str, Type):
        Rtti._instance()._add_type(scoped_name, Type)
        
    def _add_type(self, scoped_name: str, Type):        
        if scoped_name not in self._rttiTypes:
            self._rttiTypes[scoped_name] = set()
        self._rttiTypes[scoped_name].add(Type)
        
    @staticmethod
    def _instance():
        global singleton
        if singleton is None:
            singleton = Rtti()
        return singleton
        
        