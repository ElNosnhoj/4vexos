import os
import json
from typing import Dict, TypedDict
_path = os.path.join(os.path.dirname(__file__), "module_settings.json")

class Module(TypedDict):
    version: int
    mod: int

ModuleMap = Dict[str, Module]


class ModuleSettingsMeta(type):
    def __getitem__(cls, key):
        try:
            return super().__getattribute__(key)
        except AttributeError:
            return {}

    def __getattr__(cls, key):
        return cls[key]
        
    def __setitem__(cls, key:str, value:Module):
        if not isinstance(value, dict):
            raise TypeError(f"{key} must be a Module (dict), got {type(value).__name__}")
        setattr(cls, key, value)

class Modules:
    MK7_XE910       : Module
    KIOSK_NFC       : Module
    MSPM_PWR        : Module
    KBD_CONTROLLER  : Module
    COIN_SHUTTER    : Module
    EMV_CONTACT     : Module
    KIOSK_III       : Module
    MK7_RFID        : Module
    PRINTER         : Module
    BNA             : Module
    MK7_VALIDATOR   : Module
    KEY_PAD_2       : Module

class ModuleSettings(Modules, metaclass=ModuleSettingsMeta):
    class ReadError(Exception): pass
    class WriteError(Exception): pass

    @classmethod
    def get_keys(cls) ->ModuleMap:
        data = {}
        for k in dir(cls):
            if k.startswith("__") or callable(getattr(cls, k)):
                continue
            val = getattr(cls, k)
            # ensure val is serializable (convert TypedDict/Module to dict)
            if isinstance(val, dict):
                data[k] = val
            else:
                # fallback for non-dict values
                data[k] = val
        return data

    @classmethod
    def __defaults(cls):
        keys = list(Modules.__annotations__.keys())
        # for key in keys: cls[key] = Module(version=-1,mod=-1)
        for key in keys: cls[key] = {}

    @classmethod
    def load(cls, filepath=_path):
        # cls.__defaults()
        try: 
            with open(_path) as f:
                data = json.load(f)
                for k,v in data.items():
                    setattr(cls,k,v)
        except Exception as e:
            raise cls.ReadError from e

    @classmethod
    def save(cls, filepath=_path):
        # collect all class attributes that aren't methods/dunder
        data =cls.get_keys()
        try:
            with open(filepath, "w") as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            raise cls.WriteError from e
        
    @classmethod
    def check(cls, key: str, val: Module) -> bool:
        stored = cls[key]  # returns {} if key doesn't exist
        return stored == val

ModuleSettings.load()

if __name__ == "__main__":
    # print(ModuleSettings["MK7_XE910"])
    # print(ModuleSettings["asd"])
    # print(ModuleSettings.MK7_XE910)
    # print(ModuleSettings.KEY_PAD_2)
    # print(ModuleSettings.check("MK7_XE910", {"version":2209,"mod":3}))
    print(ModuleSettings.get_keys())

