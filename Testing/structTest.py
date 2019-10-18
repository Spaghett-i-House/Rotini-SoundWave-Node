import struct
import time
import numpy as np


def test_struct_decode(float_to_encode):
    packed = struct.pack("!f", float_to_encode)
    (unpacked_float,) = struct.unpack("!f", packed)
    print(float_to_encode, unpacked_float)
    assert(float_to_encode == unpacked_float)



if __name__ == "__main__":
    # run tests
    test_struct_decode(time.time()-float(1571300000.0))