import re

import logging
logger = logging.getLogger(__name__)

class DotWriter:

    def __init__(self, fp):
        self.fp = fp

    def write_edge(self, data):

        if not data["is_available"]:
            return

        line = f'"{data["src"]}":e -> "{data["dst"]}"'

        if data["minlen"]:
            line += f' [minlen={data["minlen"]}]'

        line += ';'

        self.fp.write(line)
        self.fp.write("\n")

    def port_name(self, port):

        if port["ip"]:
            cluster = port["ip"]
        else:
            cluster = port["mac"]

        cluster = re.sub(r'[.:]', '_', cluster)

        return f'node_{cluster}_port{port["pnum"]}'
