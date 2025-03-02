from mcdreforged.api.all import *
import uuid_api
import os
import json
class DataManager:
    def __init__(self, source: CommandSource, name: str, config: dict = None):
        uuid = uuid_api.get_uuid(name)
        self.config = config if config is not None else {}
        self.source = source
        self.history_path = './config/chat_with_ai/data/' + uuid + '.json'
        self.system_prompt_path = './config/chat_with_ai/data/' + uuid + '_system_prompt.json'
        self.prefix_path = './config/chat_with_ai/data/' + uuid + '_prefixe.txt'

        self.initial_system_prompt = [{"role": "system", 
                                 "content": self.config.get("system_prompt")
        }]
        
        if not os.path.exists(self.prefix_path):
            os.makedirs(os.path.dirname(self.prefix_path), exist_ok=True)
            with open(self.prefix_path, 'w') as file:
                file.write(self.config.get("prefix"))

        with open(self.prefix_path, 'r') as file:
            self.prefix = file.read().strip()
            if self.prefix is None:
                self.prefix = self.config.get("prefix")
                with open(self.prefix_path, 'w') as file:
                    file.write(self.prefix)

        if not os.path.exists(self.history_path):
            os.makedirs(os.path.dirname(self.history_path), exist_ok=True)
            with open(self.history_path, 'w') as file:
                json.dump([], file)

        if not os.path.exists(self.system_prompt_path):
            os.makedirs(os.path.dirname(self.system_prompt_path), exist_ok=True)
            with open(self.system_prompt_path, 'w') as file:
                json.dump(self.initial_system_prompt, file)

        with open(self.system_prompt_path, 'r') as file:
            system_prompt = json.load(file)
            if system_prompt is None:
                with open(self.system_prompt_path, 'w') as file:
                    json.dump(self.initial_system_prompt, file)
        

    
    def get_history(self):
        with open(self.history_path, 'r') as file:
            messages =  json.load(file)
        history = "\n--------------------history--------------------\n"
        for index, message in enumerate(messages):
            history += f"##{index}##: {message['role']}: {message['content']}\n"
        history += "-----------------------------------------------\n"
        self.source.reply(history)

    def clear_history(self):
        with open(self.history_path, 'w') as file:
            json.dump([], file)
        self.source.reply("Clear history")
    

    def add_message(self, role: str, user_input: str):
        with open(self.system_prompt_path, 'r') as file:
            system_prompt = json.load(file)
        with open(self.history_path, 'r') as file:
            messages = json.load(file)
        messages.append({"role": role, "content": user_input})
        with open(self.history_path, 'w') as file:
            json.dump(messages, file)
        return system_prompt + messages
    

    def set_system(self, system_prompt: str):
        with open(self.system_prompt_path, 'w') as file:
            json.dump([{"role": "system", "content": system_prompt}], file)
        self.source.reply("Set system prompt successfully")
    
    def set_prefix(self, prefix: str):
        self.prefix = f'§a[{prefix}]§r'
        with open(self.prefix_path, 'w') as file:
            file.write(self.prefix)
        self.source.reply("Set prefix successfully")

    def init_prefix(self):
        self.prefix = self.config.get("prefix")
        with open(self.prefix_path, 'w') as file:
            file.write(self.prefix)
        self.source.reply("Init prefix successfully")
    def init_system_prompt(self):
        with open(self.system_prompt_path, 'w') as file:
            json.dump(self.initial_system_prompt, file)
        self.source.reply("Init system prompt successfully")

    def init_all(self):
        self.init_prefix()
        self.init_system_prompt()
        self.clear_history()
        self.source.reply("Init all successfully")

    def get_prefix(self):
        self.source.reply(f"Prefix: {self.prefix}")

    def get_system_prompt(self):
        with open(self.system_prompt_path, 'r') as file:
            system_prompt = json.load(file)
        self.source.reply(f"System Prompt: {system_prompt}")