from mcdreforged.api.all import *
from openai import OpenAI
import os
import json
PLUGIN_METADATA = {
    'id': 'chat_with_AI',
    'version': '1.0.0',
    'name': 'Chat with AI',
    'description': 'Let your server chat with AI',
    'author': 'gubai',
}

key = "YOUR_API_KEY"

class DataManager:
    def __init__(self, source: CommandSource, name: str):
        self.initial_message = [{"role": "system", "content": "你是一个Minecraft助手，负责解答玩家关于Minecraft相关问题。解答问题时，要联系上下文，给出精确的答案。"}]
        self.source = source
        self.name = name
        self.history_path = './config/DeepSeek/' + name + '.json'
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

        
def on_load(server: ServerInterface, old_module):
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

def get_help(source: CommandSource, context: CommandContext):
    source.reply("§a[DeepSeek]§r 命令：\n"
                 "§6!!dsp help§r 查看帮助\n"
                 "§6!!dsp history§r 查看历史消息\n"
                 "§6!!dsp clear§r 清空历史消息\n"
                 "§6!!dsp <message>§r 与DeepSeek对话")
    
def get_user_content(source: CommandSource, context: CommandContext):
    message = context['message']
    if source.is_player:
        player_data = DataManager(source, source.player)
        player_data.add_message("user", message)
        # 给玩家直接回复
        source.reply(f"§a[DeepSeek]§r 收到你的消息：{message}")
        # DeepSeek回复
        send_message = player_data.get_send_message()
        response = send_message_to_ds(send_message)
        source.reply(f"§a[DeepSeek]§r {response}")
        player_data.add_message("assistant", response)
        # 广播给所有玩家
        # source.get_server().execute(f'tellraw @a {{"text":"§6[系统广播]§r {source.player} 对DeepSeek说：{message}"}}')
    else:
        source.reply("§c该命令只能由玩家使用")

def get_history(source: CommandSource):
    player_data = DataManager(source, source.player)
    player_data.get_history()

def clear_history(source: CommandSource):
    player_data = DataManager(source, source.player)
    player_data.clear_history()

def send_message_to_ds(send_message: str):
    client = OpenAI(api_key=key, base_url="https://api.deepseek.com")
    response = client.chat.completions.create(
    model="deepseek-chat",
    messages=send_message,
    stream=False
    )
    return response.choices[0].message.content


