import configparser


def read_config(path: str) -> configparser.ConfigParser:
    config = configparser.ConfigParser()
    config.read(path)


if __name__ == '__main__':

    config_path = 'configs/data.ini'