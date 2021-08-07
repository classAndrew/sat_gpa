from abc import abstractmethod
from typing import List

class Config:
    """
    Configurations and values
    """

    flag_to_attrib = {
        "-n": "names", "--name": "names",
        "-f": "file_list", "--file": "file_list",
        "-o": "out_dir", "--output": "out_dir",
        "-l": "load_file", "--load": "load_file",
        "-p": "is_predict", "--predict": "is_predict",
        "-g": "gpa", "--gpa": "gpa",
        "-a": "act", "--act": "act",
        "-s": "sat", "--sat": "sat",
        "-i": "in_state", "--instate": "in_state",
        "-m": "major", "--major": "major",
        "-r": "do_rank", "--rank": "do_rank"
    }

    bools = {
        "in_state", "is_predict", "do_rank"
    }

    def __init__(self, arglist: List[str]):
        self.names = ConfigList()
        self.file_list = ConfigValue()
        self.out_dir = ConfigValue()
        self.load_file = ConfigValue()
        self.is_predict = False
        self.gpa = ConfigValue()
        self.sat = ConfigValue()
        self.act = ConfigValue()
        self.in_state = False
        self.major = ConfigValue()
        self.do_rank = False

        i = 0
        attrib = ""
        while i < len(arglist):
            # is flag
            if arglist[i].startswith("-") or arglist[i].startswith("--"):
                if not arglist[i] in Config.flag_to_attrib:
                    raise Exception(f"{arglist[i]} unknown flag")

                attrib = Config.flag_to_attrib[arglist[i]]

                # if it's just an option then directly set it to true
                if attrib in Config.bools:
                    self.__setattr__(attrib, True)
                
                i += 1
                continue
            
            # only reason is that arguments show before a flag
            if not attrib:
                raise Exception("Incorrect Usage")

            self.__getattribute__(attrib).update(arglist[i])
            i += 1
        
        # convert them all into Lists or strings
        for attrib in set(Config.flag_to_attrib.values()):
            if not attrib in Config.bools:
                self.__setattr__(attrib, self.__getattribute__(attrib).val)
        
        if self.act:
            self.sat = round(int(self.sat)/36*1600, -1)
        if self.sat and self.gpa:
            self.sat = int(self.sat)
            self.gpa = float(self.gpa)

        if self.file_list:
            with open(self.file_list) as f:
                self.names = f.read().split('\n')

class ConfigField:
    """
    Abstract class of configuration

    @ivar val: value
    """
    
    def __init__(self, val=None):
        self.val = val

    @abstractmethod
    def update(self, new):
        pass

class ConfigList(ConfigField):
    """
    List value

    @type val: List
    """

    def __init__(self, val=None):
        super().__init__(val=[])
    
    def update(self, new):
        self.val.append(new)

class ConfigValue(ConfigField):
    """
    Single value
    """

    def __init__(self, val=None):
        super().__init__(val=val)
    
    def update(self, new):
        self.val = new