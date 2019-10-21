class SDPMessage(object):

    def __init__(self, v, o, s, t, m, c, i=None, u=None, e=None, p=None, b=None, r=None,
                 z=None, k=None, a=None):
        args = locals()  # gets a dict of all local variables
        for arg_name in args:
            if arg_name != "self" and args[arg_name] is not None:
                setattr(self, arg_name, args[arg_name])

    def serialize(self):
        #print(vars(self))
        lines = ""
        member_vars = vars(self)
        for i in member_vars:
            lines += i+"="+member_vars[i]+"\r\n"
        print(lines)
        return lines.encode('utf-8')

    @staticmethod
    def from_string(sdp_string: str):
        lines = sdp_string.split("\r\n")
        var_dict = {}
        print(lines)
        for i in lines:
            if i == "":
                continue
            line = i.split("=")
            var_name = line[0]
            var_val = line[1]
            var_dict[var_name] = var_val
        return SDPMessage(var_dict['v'], var_dict['o'], var_dict['s'], var_dict['t'], var_dict['m'], var_dict['c'],
                          var_dict.get('e'), var_dict.get('u'), var_dict.get('e'), var_dict.get('p'), var_dict.get('b'),
                          var_dict.get('r'), var_dict.get('z'), var_dict.get('k'), var_dict.get('a'))

"""a = SDPMessage("2", "OASD", "ASD", "ASDASD", "ASDAIUG", "ASUIDHO")
a.serialize()

z=SDPMessage.from_string(a.serialize().decode('utf-8'))
z.serialize()"""