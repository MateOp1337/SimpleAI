import json, random, os, shutil, time
from datetime import datetime
from typing import Callable, List

class TrainMode:
    @classmethod
    def chat(self):
        return 'chat'
    
    @classmethod
    def man(self):
        return 'man'

class IfUnknownType:
    @classmethod
    def random_response(self):
        return 'random_response'
    
    @classmethod
    def return_error(self):
        return 'return_error'

class Monitor:
    def __init__(self, *, limit: int = 100):
        self.limit = limit
        self.monitor = {
            "questions": [],
            "response_time": [],
            "knowledge_records": []
        }
    
    def update(
        self, *,
        question: str,
        response_time: float | int,
        knowledge_records: bool
    ):
        entries = {
            'questions': question,
            'response_time': response_time,
            'knowledge_records': knowledge_records
        }
        
        for key in self.monitor.keys():
            if key in entries:
                self.monitor[key].append(entries[key])
                if len(self.monitor[key]) > self.limit:
                    self.monitor[key].pop(0)
    
    def clear(self):
        self.monitor = {
            "questions": [],
            "response_time": [],
            "knowledge_records": []
        }
    
    def get(self):
        try:
            average_response_time = sum(self.monitor['response_time']) / len(self.monitor['response_time'])
        except ZeroDivisionError:
            average_response_time = None
            
        result = self.monitor.copy()
        result['average_response_time'] = average_response_time
        return result

class Configuration:
    def __init__(
        self, *,
        models_path: str = '',
        train_mode: 'TrainMode' = TrainMode.chat(),
        learning: bool = True,
        case_insensitive: bool = True,
        case_insensitive_in_responses: bool = False,
        interpunction: bool = True,
        ignore_polish_characters: bool = True,
        ignore_discord_invites: bool = False,
        ignore_links: bool = False,
        encoding: str = 'utf-8',
        ensure_ascii: bool = False,
        monitor: Monitor = None,
        learn_filter: Callable = None,
        learn_filters: List[Callable] = [],
        custom_response_handler: Callable = None,
        custom_response_handlers: List[Callable] = [],
        extension: str = 'basic-model',
        if_unknown: IfUnknownType = IfUnknownType.random_response()
    ):
        self.models_path = models_path
        self.train_mode = train_mode
        self.learning = learning
        self.case_insensitive = case_insensitive
        self.case_insensitive_in_responses = case_insensitive_in_responses
        self.interpunction = interpunction
        self.ignore_polish_characters = ignore_polish_characters
        self.ignore_discord_invites = ignore_discord_invites
        self.ignore_links = ignore_links
        self.encoding = encoding
        self.ensure_ascii = ensure_ascii
        self.monitor = monitor
        self.learn_filter = learn_filter
        self.learn_filters = learn_filters
        self.custom_response_handler = custom_response_handler
        self.custom_response_handlers = custom_response_handlers
        self.extension = extension
        self.if_unknown = if_unknown
    
    @staticmethod
    def default():
        """
        Default configuration.
        """
        config = Configuration()
        config.models_path = ''
        config.train_mode = TrainMode.chat()
        config.learning = True
        config.case_insensitive = True
        config.ignore_polish_characters = True
        config.case_insensitive_in_responses = False
        config.interpunction = True
        config.ignore_polish_characters = True
        config.ignore_discord_invites = False
        config.ignore_links = False
        config.encoding = 'utf-8'
        config.ensure_ascii = False
        return config
    
    @staticmethod
    def secure():
        """
        Default configuration, but with maximum security, ignores Discord invites and links.
        """
        config = Configuration.default()
        config.ignore_discord_invites = True
        config.ignore_links = True
        return config
    
    @staticmethod
    def chat_only():
        """
        Default configuration, but with the learning function disabled.
        """
        config = Configuration.default()
        config.learning = False
        return config
    
    @staticmethod
    def manual_learning():
        """
        Default configuration, but with "Man (manual)" training mode enabled.
        """
        config = Configuration.default()
        config.train_mode = TrainMode.man()
        return config

class AI:
    def __init__(
            self, *,
            model: str,
            configuration: Configuration = Configuration.default()
        ):
        """
        AI object for chatting.

        Args:
            model: The name of the model you want to chat with.
            configuration: Model configuration.
        """
        
        if configuration.learn_filter is not None and configuration.learn_filters is not []:
            raise ValueError('You cannot use the `learn_filter` and `learn_filters` argument. Choose just one of them.')
        if configuration.custom_response_handler is not None and configuration.custom_response_handlers != []:
            raise ValueError('You cannot use the `custom_response_handler` and `custom_response_handlers` argument. Choose just one of them.')

        self.config: Configuration

        self.model = model
        self.config = configuration
        self.session_data = {'backup_created': False}
        self.monitor = self.config.monitor
        
        def getModels():
            files = os.listdir(self.config.models_path)
            return files

        models = getModels()
        if f'{model}.basic-model' not in models:
            raise FileNotFoundError(f"AI model '{model}.{self.config.extension}' not found. Make sure it is in the 'models' folder and the file extension is '{self.config.extension}'.")

        self.model_path = f'{self.config.models_path}/{model}.{self.config.extension}'
        
        self.ai_data: dict = self.readFile()
        
    def make_backup(self):
        conf = self.config
        model = self.model
        models_path = conf.models_path
        
        now = datetime.now()
        dt = now.strftime("%d-%m-%Y_%H:%M:%S")
        backup_path = f'{models_path}/backups/{model}/{model}-{dt}.basic-model.backup'
        
        if not os.path.exists(os.path.dirname(backup_path)):
            os.makedirs(os.path.dirname(backup_path))

        shutil.copy(f'{models_path}/{model}.basic-model', backup_path)

        self.session_data['backup_created'] = True
    
    def readFile(self):
        conf = self.config
        with open(f'{conf.models_path}/{self.model}.{conf.extension}', 'r') as f:
            return json.load(f)
        
    def saveData(self, data):
        conf = self.config
        if not self.session_data['backup_created']:
            self.make_backup()
            
        with open(f'{conf.models_path}/{self.model}.{conf.extension}', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False)

    def remove_polish_characters(self, inp):
        charmap = str.maketrans({'ą': 'a', 'ć': 'c', 'ę': 'e', 'ł': 'l', 'ń': 'n', 'ó': 'o', 'ś': 's', 'ż': 'z', 'ź': 'z'})
        out = inp.translate(charmap)
        return out
    
    def learn(self, inp, out):
        conf = self.config
        ai_data = self.ai_data
        
        if ('discord.gg' not in inp.lower() and 'discord.com/invite' not in inp.lower()) or not conf.ignore_discord_invites:
            if conf.interpunction:
                if not any(inp.endswith(znak) for znak in ['.', '!', '?']):
                    inp = inp+'.'
                if not conf.case_insensitive:
                    inp = inp.capitalize()
                
            if ai_data.get(inp):
                if out not in ai_data[inp] and inp != out:
                    ai_data[inp].append(out)
            else:
                if inp != out:
                    ai_data[inp] = [out]
            
        self.saveData(ai_data)
    
    def ask(self, inp, prev_ai_msg=None, out=None, learn_v=True):
        start_time = time.time()
        
        conf = self.config
        if conf.train_mode == TrainMode.man():
            inp: str
            out: str
            
            if not out:
                raise TypeError('In MAN training mode "out" argument is REQUIRED.')
            
            self.learn(inp, out)
            return f'Added new phrase. `{inp}` => `{out}`'

        inp2 = inp.lower()
        inp2 = self.remove_polish_characters(inp2)
        
        learn_filter_failed = None
        
        # Handle single learn_filter if it exists
        if self.config.learn_filter:
            learn_filter_passed = self.config.learn_filter(inp2)
            
            if isinstance(learn_filter_passed, bool):
                learn_filter_failed = not learn_filter_passed
            else:
                learn_filter_failed = learn_filter_passed
        
        # Handle multiple learn_filters if they exist
        if self.config.learn_filters:
            for filter in self.config.learn_filters:
                learn_filter_passed = filter(inp2)
                
                if isinstance(learn_filter_passed, bool):
                    learn_filter_failed = not learn_filter_passed
                else:
                    learn_filter_failed = learn_filter_passed
                
                # Break loop if any filter fails
                if isinstance(learn_filter_failed, bool) and learn_filter_failed:
                    break
        
        if self.config.custom_response_handler:
            custom_response = self.config.custom_response_handler(inp2)
        
        elif self.config.custom_response_handlers:
            for handler in self.config.custom_response_handlers:
                custom_response = handler(inp2)
                if custom_response is not None:
                    break
        
        else:
            custom_response = None
            
        # Default behavior if no filters failed
        if learn_filter_failed is None:
            learn_filter_failed = True
        
        if prev_ai_msg and conf.learning:
            if learn_v and learn_filter_failed:
                self.learn(prev_ai_msg, inp2 if conf.case_insensitive_in_responses else inp)
        
        resps = self.ai_data.get(inp2 if conf.case_insensitive else inp)
        
        if resps:
            resp: str = random.choice(resps)
            knowledge_record = True
        else:
            knowledge_record = False
            if conf.if_unknown == IfUnknownType.random_response():
                all_resps = list(self.ai_data.keys())
                randresp = random.choice(all_resps)
                resp = random.choice(self.ai_data.get(randresp))
            elif conf.if_unknown == IfUnknownType.return_error():
                return 404
                
        resp = resp.capitalize()
        if not resp.endswith(('.', '!', '?')):
            resp = resp + '.'
            
        end_time = time.time()
        if self.monitor is not None:
            execution_time = end_time - start_time
            self.monitor.update(
                question=inp,
                response_time=execution_time,
                knowledge_records=knowledge_record
            )
        
        return (custom_response if custom_response is not None else resp), {'learned': bool(learn_v and learn_filter_failed and custom_response is None and self.config.learning)}
