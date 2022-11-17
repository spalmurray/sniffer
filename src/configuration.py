import configparser


class Config:
    _path = 'config.ini'

    def __init__(self):
        config = self.read_config()
        self.token = config.get("sniffer", "token")

    @staticmethod
    def read_config() -> configparser.ConfigParser:
        """Return the config.properties file as a dictionary. If the file does not exist, generate a new one."""
        config = configparser.ConfigParser()
        config.read(Config._path)
        if not config.has_section("sniffer"):
            with open(Config._path, "w") as file:
                lines = ["[sniffer]\n", "token=enterTokenHere\n"]
                file.writelines(lines)
            return Config.read_config()
        return config
