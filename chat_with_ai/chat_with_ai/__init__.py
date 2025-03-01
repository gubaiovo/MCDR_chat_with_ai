from mcdreforged.api.all import *
from openai import OpenAI
from pathlib import Path
from typing import Dict, Any
import os
import json

class DataManager:
    def __init__(self, source: CommandSource, name: str, config: dict):
        self.initial_message = [{"role": "system", 
                                 "content": config.get("system_prompt", "你是一个Minecraft助手，负责解答玩家关于Minecraft相关问题。解答问题时，要联系上下文，给出精确的答案。")
        }]
        self.source = source
        self.name = name
        self.history_path = './config/chat_with_ai/data/' + name + '.json'
        if not os.path.exists(self.history_path):
            os.makedirs(os.path.dirname(self.history_path), exist_ok=True)
            with open(self.history_path, 'w') as file:
                json.dump(self.initial_message, file)
    
    def get_send_message(self):
        with open(self.history_path, 'r') as file:
            messages =  json.load(file)
        return messages

    def get_history(self):
        with open(self.history_path, 'r') as file:
            messages =  json.load(file)
        history = "\n--------------------history--------------------\n"
        for index, message in enumerate(messages):
            history += f"##{index}##: {message['role']}: {message['content']}\n"
        history += "-----------------------------------------------\n"
        self.source.reply(history)
    
    def add_message(self, role: str, user_input: str):
        with open(self.history_path, 'r') as file:
            messages = json.load(file)
        messages.append({"role": role, "content": user_input})
        with open(self.history_path, 'w') as file:
            json.dump(messages, file)
    
    def clear_history(self):
        with open(self.history_path, 'w') as file:
            json.dump(self.initial_message, file)
        self.source.reply("Clear history")

class ConfigManager:
    def __init__(self, server: ServerInterface):
        self.server = server
        self.config_path = Path(self.server.get_data_folder()) / 'config.json'
        self.config: Dict[str, Any] = {}
        self.default_config = {
            "api_key": "",
            "base_url": "https://api.deepseek.com",
            "model": "deepseek-chat",
            "system_prompt": "你是一个Minecraft助手，负责解答玩家关于Minecraft相关问题。解答问题时，要联系上下文，给出精确的答案。"
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


def on_load(server: ServerInterface, old_module):
    global config_manager
    config_manager = ConfigManager(server)
    config = config_manager.load_config()
    if not config.get("api_key"):
        server.logger.error("未配置API Key! 请编辑 config.json 文件")
        
    server.register_help_message('!!ds <message>', '与DeepSeek对话')
    # 使用现代命令构建方式
    server.register_command(
        Literal('!!dsp').then(
            Literal('help').runs(get_help)
        ).then(
            Literal('history').runs(get_history)
        ).then(
            Literal('clear').runs(clear_history)
        ).then(
            GreedyText('message').runs(get_user_content)
        )
    )

def get_help(source: CommandSource):
    source.reply("§a[DeepSeek]§r 命令：\n"
                 "§6!!dsp help§r 查看帮助\n"
                 "§6!!dsp history§r 查看历史消息\n"
                 "§6!!dsp clear§r 清空历史消息\n"
                 "§6!!dsp <message>§r 与DeepSeek对话")
    
def get_user_content(source: CommandSource, context: CommandContext):
    message = context['message']
    if source.is_player:
        config = config_manager.load_config()
        if not config.get("api_key"):
            source.reply("§cAPI Key未配置，请联系管理员")
            return
        
        player_data = DataManager(source, source.player, config)
        player_data.add_message("user", message)
        # 给玩家直接回复
        source.reply(f"§a[DeepSeek]§r 收到你的消息：{message}")
        # DeepSeek回复
        send_message = player_data.get_send_message()
        response = send_message_to_ds(send_message, config)
        source.reply(f"§a[DeepSeek]§r {response}")
        player_data.add_message("assistant", response)
        # 广播给所有玩家
        # source.get_server().execute(f'tellraw @a {{"text":"§6[系统广播]§r {source.player} 对DeepSeek说：{message}"}}')
    else:
        source.reply("§c该命令只能由玩家使用")

def get_history(source: CommandSource):
    player_data = DataManager(source, source.player, config_manager.load_config())
    player_data.get_history()

def clear_history(source: CommandSource):
    player_data = DataManager(source, source.player, config_manager.load_config())
    player_data.clear_history()

def send_message_to_ds(send_message: str, config: dict):
    client = OpenAI(
        api_key=config["api_key"],
        base_url=config.get("base_url", "https://api.deepseek.com")
    )
    response = client.chat.completions.create(
        model=config.get("model", "deepseek-chat"),
        messages=send_message,
        stream=False
    )
    return response.choices[0].message.content


