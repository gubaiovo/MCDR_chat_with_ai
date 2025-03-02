from mcdreforged.api.all import *
from openai import OpenAI
from chat_with_ai.DataManager import DataManager
from chat_with_ai.ConfigManager import ConfigManager


def command_register(server: ServerInterface):
    builder = SimpleCommandBuilder()
    builder.command('!!dsp', get_help)
    builder.command('!!dsp help', get_help)
    builder.command('!!dsp history', get_history)
    builder.command('!!dsp clear', clear_history)
    builder.command('!!dsp system', get_system_prompt)
    builder.command('!!dsp prefix', get_prefix)
    builder.command('!!dsp system <system>', set_system_prompt)
    builder.command('!!dsp prefix <prefix>', set_prefix)
    builder.command('!!dsp init system', init_system_prompt)
    builder.command('!!dsp init prefix', init_prefix)
    builder.command('!!dsp init all', init_all)
    builder.command('!!dsp <message>', get_user_content)

    builder.arg('prefix', GreedyText)
    builder.arg('message', GreedyText)
    builder.arg('system', GreedyText)
    builder.register(server)

def on_load(server: ServerInterface, old_module):
    global config_manager
    config_manager = ConfigManager(server)
    config = config_manager.load_config()
    if not config.get("api_key"):
        server.logger.error("未配置API Key! 请编辑 config.json 文件")

    command_register(server)

def set_system_prompt(source: CommandSource, context: CommandContext):
    if not source.is_player:
        source.reply("§c该命令只能由玩家使用")
        return
    system_prompt = context['system']
    player_data = DataManager(source, source.player)
    player_data.set_system(system_prompt)


def get_help(source: CommandSource):
    source.reply("§a[Chat with AI]§r 命令：\n"
                 "§6!!dsp help§r 查看帮助\n"
                 "§6!!dsp history§r 查看历史消息\n"
                 "§6!!dsp clear§r 清空历史消息\n"
                 "§6!!dsp system§r 查看ai预设\n"
                 "§6!!dsp system <system>§r 设置ai预设\n"
                 "§6!!dsp prefix§r 查看ai名称\n"
                 "§6!!dsp prefix <prefix>§r 设置ai名称\n"
                 "§6!!dsp init system§r 初始化角色预设\n"
                 "§6!!dsp init prefix§r 初始化角色预设\n"
                 "§6!!dsp init all§r 全部初始化且清空历史记录\n"
                 "§6!!dsp <message>§r 与AI对话")
    
def get_user_content(source: CommandSource, context: CommandContext):
    message = context['message']
    if not source.is_player:
        source.reply("§c该命令只能由玩家使用")
        return
    config = config_manager.load_config()
    player_data = DataManager(source, source.player, config)
    prefix = player_data.prefix
    if not config.get("api_key"):
        source.reply("§cAPI Key未配置，请联系管理员")
        return
    message = player_data.add_message("user", message)
    response = send_message_to_ds(message, config)
    source.reply(f"{prefix} {response}")
    player_data.add_message("assistant", response)


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

def set_prefix(source: CommandSource, context: CommandContext):
    if not source.is_player:
        source.reply("§c该命令只能由玩家使用")
        return
    prefix = context['prefix']
    if not prefix :
        source.reply("请输入AI名称")
        return
    if len(prefix) > 8:
        source.reply("AI名称不能超过8个字符")
        return
    player_data = DataManager(source, source.player, config_manager.load_config())
    player_data.set_prefix(prefix)

def get_system_prompt(source: CommandSource):
    if not source.is_player:
        source.reply("§c该命令只能由玩家使用")
        return
    player_data = DataManager(source, source.player, config_manager.load_config())
    player_data.get_system_prompt()

def get_prefix(source: CommandSource):
    if not source.is_player:
        source.reply("§c该命令只能由玩家使用")
        return
    player_data = DataManager(source, source.player, config_manager.load_config())
    player_data.get_prefix()

def get_history(source: CommandSource):
    if not source.is_player:
        source.reply("§c该命令只能由玩家使用")
        return
    player_data = DataManager(source, source.player, config_manager.load_config())
    player_data.get_history()

def clear_history(source: CommandSource):
    if not source.is_player:
        source.reply("§c该命令只能由玩家使用")
        return
    player_data = DataManager(source, source.player, config_manager.load_config())
    player_data.clear_history()

def init_system_prompt(source: CommandSource):
    if not source.is_player:
        source.reply("§c该命令只能由玩家使用")
        return
    player_data = DataManager(source, source.player, config_manager.load_config())
    player_data.init_system_prompt()

def init_prefix(source: CommandSource):
    if not source.is_player:
        source.reply("§c该命令只能由玩家使用")
        return
    player_data = DataManager(source, source.player, config_manager.load_config())
    player_data.init_prefix()
    
def init_all(source: CommandSource, ):
    if not source.is_player:
        source.reply("§c该命令只能由玩家使用")
        return
    player_data = DataManager(source, source.player, config_manager.load_config())
    player_data.init_all()