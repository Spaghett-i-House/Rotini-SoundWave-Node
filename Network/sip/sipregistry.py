class SIPRegistry(object):

    def __init__(self):
        self.registry = {}

    def add_address(self, from_string: str):
        addr_split = from_string.split(" ")
        user_name = addr_split[0]
        address = addr_split[1].strip("<")
        address = address.strip(">")

        self.registry[user_name] = address
