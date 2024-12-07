import logging
import coloredlogs

def _map_role_to_lib(role: str):
    return {
        'client': 'bleak',
        'server': 'bless'
    }[role]

def setup_logger(verbosity: int, role: str, prefix_id: str):
    ble_lib_name = _map_role_to_lib(role)
    ble_logger = logging.getLogger(ble_lib_name)
    ble_logger.level = logging.DEBUG if verbosity > 1 else logging.INFO

    level_colors = {
        'critical': {'bold': True, 'color': 'red'},
        'error': {'color': 'red'},
        'warning': {'color': 'yellow'},
        'info': {'color': 'green'},
        'debug': {'color': 'cyan'},
        'success': {'bold': True, 'color': 'green'},
    }
    field_colors = {
        'asctime': {},
        'levelname': {'color': 'magenta'},
        'filename': {'color': 'white', 'faint': True},
    }

    prefix = f'[{coloredlogs.ansi_wrap(prefix_id, bold=True)}] ' if prefix_id else ''
    coloredlogs.install(
        level=logging.DEBUG if verbosity > 0 else logging.INFO,
        fmt=prefix+'%(asctime)s.%(msecs)03d | %(levelname)s | %(filename)s: %(message)s',
        datefmt='%H:%M:%S',
        level_styles=level_colors,
        field_styles=field_colors,
    )