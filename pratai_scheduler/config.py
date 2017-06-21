import configparser

config = configparser.ConfigParser()
config.read("/etc/pratai/pratai-scheduler.conf")


def parse_config(section: str) -> str:
    """Parse a config file into a dict
    :param section: string
    :return: a dict representing a config file
    """
    config_dict = {}
    options = config.options(section)
    for option in options:
        try:
            config_dict[option] = config.get(section, option)
            if config_dict[option] == -1:
                print("skip: {0}".format(option))
        except Exception:
            print("exception on {0}!".format(option))
            config_dict[option] = None
    return config_dict
