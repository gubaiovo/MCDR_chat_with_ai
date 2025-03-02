from mcdreforged.api.all import *
from pathlib import Path
from typing import Dict, Any
import os
import json

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
            "prefix": "§a[DeepSeek]§r"
        }
        self._ensure_config()

    def _ensure_config(self):
        # 确保配置文件存在
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
        if not self.config_path.exists():
            self.save_config(self.default_config)
            self.server.logger.warning(f"Created default config at {self.config_path}")

    def load_config(self) -> Dict[str, Any]:
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
                return self.config
        except Exception as e:
            self.server.logger.error(f"Failed to load config: {str(e)}")
            return self.default_config

    def save_config(self, config: Dict[str, Any]):
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4, ensure_ascii=False)