class SIPMessage(object):

    def __init__(self, headers: dict, first_line: str = "", body: str = ""):
        self.headers = headers
        self.first_line = first_line  # only used to turn into request/response
        self.body = body  # only used to turn into request/response

    @staticmethod
    def from_string(received_message: str):
        sections = received_message.split('\r\n')
        start_line = sections[0]
        headers = {}
        index = 1
        for i, line in enumerate(sections[1:]):
            if line == "":
                # found the empty line signaling end of headers
                index += 1
                break
            else:
                if line.find(":") >= 0:
                    split_header = line.split(":")
                    # print(split_header)
                    variable_name = split_header[0]
                    variable_val = split_header[1]
                    headers[variable_name] = variable_val
            index += 1

        body = "\r\n".join(sections[index:])
        # print("START-LINE:", start_line)
        # print("HEADERS:", headers)
        # print("Body:", body)
        return SIPMessage(headers=headers, first_line=start_line, body=body)