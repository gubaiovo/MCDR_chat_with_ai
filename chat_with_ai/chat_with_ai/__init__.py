from mcdreforged.api.all import *
from openai import OpenAI
from chat_with_ai.DataManager import DataManager
from chat_with_ai.ConfigManager import ConfigManager


def command_register(server: ServerInterface, config: dict):
    builder = SimpleCommandBuilder()
    require = Requirements()
    level_dict = config.get("permission", {})
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
    builder.command('!!dsp msg <message>', get_user_content)

    builder.arg('prefix', GreedyText)
    builder.arg('message', GreedyText)
    builder.arg('system', GreedyText)

    for literal in level_dict:
        permission = level_dict[literal]

        builder.literal(literal).requires(
            require.has_permission(permission),
            failure_message_getter=lambda err, p=permission: "lack_permission"
        )

    builder.register(server)
    


def tr(key, *args):
    return ServerInterface.get_instance().tr(f"chat_with_ai.{key}", *args)

def on_load(server: ServerInterface, old_module):
    global config_manager
    config_manager = ConfigManager(server)
    config = config_manager.load_config()
    config_manager.check_config_when_loading()
    command_register(server, config)


def set_system_prompt(source: CommandSource, context: CommandContext):
    if not source.is_player:
        source.reply(tr("only_by_player"))
        return
    system_prompt = context['system']
    player_data = DataManager(source=source, name=source.player)
    player_data.set_system(system_prompt)


def get_help(source: CommandSource):
    source.reply(tr("help_message"))
    
@new_thread
def get_user_content(source: CommandSource, context: CommandContext):
    message = context['message']
    if not source.is_player:
        source.reply(tr("only_by_player"))
        return
    config = config_manager.load_config()
    player_data = DataManager(source=source, name=source.player, config=config)
    prefix = player_data.prefix
    if not config.get("api_key"):
        source.reply(tr("error.no_key"))
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
        source.reply(tr("only_by_player"))
        return
    prefix = context['prefix']
    if not prefix :
        source.reply(tr("error.input_prefix_is_empty"))
        return
    if len(prefix) > 8:
        source.reply(tr("error.input_prefix_too_long"))
        return
    player_data = DataManager(source=source, name=source.player, config=config_manager.load_config())
    player_data.set_prefix(prefix)

def get_system_prompt(source: CommandSource):
    if not source.is_player:
        source.reply(tr("only_by_player"))
        return
    player_data = DataManager(source=source, name=source.player, config=config_manager.load_config())
    player_data.get_system_prompt()

def get_prefix(source: CommandSource):
    if not source.is_player:
        source.reply(tr("only_by_player"))
        return
    player_data = DataManager(source=source, name=source.player, config=config_manager.load_config())
    player_data.get_prefix()

def get_history(source: CommandSource):
    if not source.is_player:
        source.reply(tr("only_by_player"))
        return
    player_data = DataManager(source=source, name=source.player, config=config_manager.load_config())
    player_data.get_history()

def clear_history(source: CommandSource):
    if not source.is_player:
        source.reply(tr("only_by_player"))
        return
    player_data = DataManager(source=source, name=source.player, config=config_manager.load_config())
    player_data.clear_history()

def init_system_prompt(source: CommandSource):
    if not source.is_player:
        source.reply(tr("only_by_player"))
        return
    player_data = DataManager(source=source, name=source.player, config=config_manager.load_config())
    player_data.init_system_prompt()

def init_prefix(source: CommandSource):
    if not source.is_player:
        source.reply(tr("only_by_player"))
        return
    player_data = DataManager(source=source, name=source.player, config=config_manager.load_config())
    player_data.init_prefix()
    
def init_all(source: CommandSource, ):
    if not source.is_player:
        source.reply(tr("only_by_player"))
        return
    player_data = DataManager(source=source, name=source.player, config=config_manager.load_config())
    player_data.init_all()


    