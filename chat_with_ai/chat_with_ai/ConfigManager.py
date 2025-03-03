from mcdreforged.api.all import *
from pathlib import Path
from typing import Dict, Any
import os
import json

def tr(key, *args):
    return ServerInterface.get_instance().tr(f"chat_with_ai.{key}", *args)

class ConfigManager:
    def __init__(self, server: ServerInterface):
        self.server = server
        self.config_path = Path(self.server.get_data_folder()) / 'config.json'
        self.config: Dict[str, Any] = {}
        self.default_config = {
            "api_key": "",
            "base_url": "https://api.deepseek.com",
            "model": "deepseek-chat",
            "system_prompt": "你是一个Minecraft助手，负责解答玩家关于Minecraft相关问题。解答问题时，要联系上下文，给出精确的答案。",
            "prefix": "§a[DeepSeek]§r",
            "permission":
            {
		        "help": 1,
		        "history": 1,
		        "clear": 1,
		        "system": 1,
		        "prefix": 1,
		        "init system": 1,
		        "init prefix": 1,
		        "init all": 1,
		        "msg": 1
            }
        }
        self._ensure_config()

    def _ensure_config(self):
        # 确保配置文件存在
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
        if not self.config_path.exists():
            self.save_config(self.default_config)
            self.server.logger.warning(tr("create_config"), self.config_path)

    def load_config(self) -> Dict[str, Any]:
        if self.check_config_when_running():
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
                return self.config
        else:
            return self.default_config


    def save_config(self, config: Dict[str, Any]):
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4, ensure_ascii=False)

    def check_config_when_running(self):
        try:
            json_data = json.loads(open(self.config_path, 'r', encoding='utf-8').read())
            # self.server.logger.info("§a[Chat with AI]§r "+tr("correct_config"))
            self.config = json_data
            required_keys = {
                "api_key": "API Key",
                "base_url": "base url",
                "model": "model",
                "system_prompt": "system prompt",
                "prefix": "prefix"
            }
            for key, name in required_keys.items():
                if not json_data.get(key):
                    self.server.logger.error(tr("error.check_empty") + name +", "+ tr("error.please_check_config"))
                    return False
                # else:
                #     self.server.logger.info("§a[Chat with AI]§r "+tr("check_not_empty")+name)
            return True
        except Exception as e:
            self.server.logger.error(tr("error.config_error")+str(e))
            return False
        
    def check_config_when_loading(self):
        try:
            json_data = json.loads(open(self.config_path, 'r', encoding='utf-8').read())
            self.server.logger.info("§a[Chat with AI]§r "+tr("correct_config"))
            self.config = json_data
            required_keys = {
                "api_key": "API Key",
                "base_url": "base url",
                "model": "model",
                "system_prompt": "system prompt",
                "prefix": "prefix"
            }
            for key, name in required_keys.items():
                if not json_data.get(key):
                    self.server.logger.error(tr("error.check_empty") + name +", "+ tr("error.please_check_config"))
                    return False
                else:
                    self.server.logger.info("§a[Chat with AI]§r "+tr("check_not_empty")+name)
            return True
        except Exception as e:
            self.server.logger.error(tr("error.config_error")+str(e))
            return False


        