from mcdreforged.api.all import *
from pathlib import Path
import uuid_api
import os
import json
import hashlib
import time


def tr(key, *args):
    return ServerInterface.get_instance().tr(f"chat_with_ai.{key}", *args)

def hash_name_with_timestamp(name: str) -> str:
    timestamp = str(int(time.time()))
    combined_string = name + timestamp
    hash_object = hashlib.sha256(combined_string.encode())
    hash_hex = hash_object.hexdigest()
    return hash_hex[:60]

class DataManager:
    def __init__(self, source: CommandSource, name: str, config: dict = None):
        uuid_path = './config/chat_with_ai/uuid.json'
        data_path = './config/chat_with_ai/data/'
        # uuid存储
        if not os.path.exists(uuid_path):
            with open(uuid_path, 'w') as file:
                json.dump({}, file)
        with open(uuid_path, 'r') as file:
            uuid_data = json.load(file)
        if name in uuid_data:
            uuid = uuid_data[name]
        else:
            try:
                uuid = uuid_api.get_uuid(name)

            except Exception as e:
                self.server.logger.error(str(e))
                uuid = hash_name_with_timestamp(name)
            uuid_data[name] = uuid
            with open(uuid_path, 'w') as file:
                json.dump(uuid_data, file, indent=4)

        self.config = config if config is not None else {}
        self.source = source
        self.history_path = data_path + f'{uuid}.json'
        self.system_prompt_path = data_path + f'{uuid}_system_prompt.json'
        self.prefix_path = data_path + f'{uuid}_prefixe.txt'

        self.initial_system_prompt = [{"role": "system", 
                                 "content": self.config.get("system_prompt")
        }]
        # 初始化
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
        history = "\n--------------------History--------------------\n"
        for index, message in enumerate(messages):
            history += f"##{index}##: {message['role']}: {message['content']}\n"
        history += "-----------------------------------------------\n"
        self.source.reply(history)

    def clear_history(self):
        with open(self.history_path, 'w') as file:
            json.dump([], file)
        self.source.reply(tr("history.clear_history"))
    

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
        self.source.reply(tr("system.set_system"))
    
    def set_prefix(self, prefix: str):
        self.prefix = f'§a[{prefix}]§r'
        with open(self.prefix_path, 'w') as file:
            file.write(self.prefix)
        self.source.reply(tr("prefix.set_prefix"))

    def init_system_prompt(self):
        with open(self.system_prompt_path, 'w') as file:
            json.dump(self.initial_system_prompt, file)
        self.source.reply(tr("system.init_system"))

    def init_prefix(self):
        self.prefix = self.config.get("prefix")
        with open(self.prefix_path, 'w') as file:
            file.write(self.prefix)
        self.source.reply(tr("prefix.init_prefix"))


    def init_all(self):
        self.init_prefix()
        self.init_system_prompt()
        self.clear_history()
        self.source.reply(tr("init_all_success"))

    def get_prefix(self):
        self.source.reply(tr("prefix.now_prefix")+self.prefix)

    def get_system_prompt(self):
        with open(self.system_prompt_path, 'r') as file:
            system_prompt = json.load(file)
        if system_prompt and isinstance(system_prompt, list) and len(system_prompt) > 0:
            content = system_prompt[0].get("content", "")
            self.source.reply(tr("system.now_system") + content)
        else:
            self.source.reply(tr("error.no_system"))