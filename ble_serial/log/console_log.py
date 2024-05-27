import logging
import coloredlogs

def setup_logger(verbosity: int):
    bleak_logger = logging.getLogger('bleak')
    bleak_logger.level = logging.DEBUG if verbosity > 1 else logging.INFO

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
    coloredlogs.install(
        level=logging.DEBUG if verbosity > 0 else logging.INFO,
        fmt='%(asctime)s.%(msecs)03d | %(levelname)s | %(filename)s: %(message)s',
        datefmt='%H:%M:%S',
        level_styles=level_colors,
        field_styles=field_colors,
    )