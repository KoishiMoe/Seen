from parse import parse
from mcdreforged.api.types import Info, PluginServerInterface
from mcdreforged.api.decorator import new_thread

from mcd_seen_plus.constants import SEEN_PREFIX, META
from mcd_seen_plus.utils import verify_player_name, bot_name, tr, logger
from mcd_seen_plus.storage import storage, bot_list
from mcd_seen_plus.config import config
from mcd_seen_plus.interface import register_command


def on_info(server: PluginServerInterface, info: Info) -> None:
    if info.is_from_server:
        psd = parse('{name}[{ip}] logged in with entity id {id} at {loc}', info.content)
        if psd is not None and verify_player_name(psd['name']):
            player_name = bot_name(psd['name']) if psd['ip'] == 'local' and config.identify_bot else psd['name']
            storage.player_joined(player_name)
            server.as_plugin_server_interface()


def on_player_left(server: PluginServerInterface, player: str):
    server.get_instance()       # to satisfy pycharm >3
    storage.player_left(player)


def on_server_stop(*args, **kwargs):
    list(args).clear()          # to satisfy pycharm >3
    dict(kwargs).clear()
    storage.correct([])


@new_thread(META.name + '_PluginLoad')
def warn_first_load():
    logger.warning('Load Seen plugin when server is empty is suggested to make sure all the datas are right')


def on_load(server: PluginServerInterface, prev_module):
    server.register_help_message(SEEN_PREFIX, tr('mcd_seen_plus.text.reg_help_msg'))
    register_command(server)
    if prev_module is not None:
        try:
            bot_list.clear()
            for player in prev_module.bot_list:
                bot_list.append(player)
        except AttributeError:
            logger.info('Seems upgraded from a old version, welcome!')
    else:
        if server.is_server_running():
            warn_first_load()
