import asyncio
import struct

SERVER_ADDRESS = '127.0.0.1'
SERVER_PORT = 9999

# inner instructions to rule a lantern
def on():
    print('Function ON')
    return 'ON'

def off():
    print('Function OFF')
    return 'OFF'

def color(rgb):
    print('Color chahged to ' + rgb)
    return rgb

# functions to check and start recieved commands
def parse_on(bb):
    code, length = struct.unpack('>bh', bb)
    assert code == 0x12
    assert length == 0
    assert len(bb) == 3
    return on()

def parse_off(bb):
    code, length = struct.unpack('>bh', bb)
    assert code == 0x13
    assert length == 0
    assert len(bb) == 3
    return off()

def parse_color(bb):
    code, length = struct.unpack('>bh', bb[0:3])
    assert code == 0x20
    assert length == 3
    
    format_string = '>' + 'b' * length
    rgb = struct.unpack(format_string, bb[3 : 3 + length])
    rgb = [i + 128 for i in rgb]
    rgb = f'#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}'
    
    return color(rgb)

# list of existing commands
COMMANDS = {
    0x12: parse_on,
    0x13: parse_off,
    0x20: parse_color,
    } 

# parse bytecode of single TLV-packet
def parse_command(bb):
    code = bb[0]
    result = 'SILENT'
    parse = None
    
    parse = COMMANDS.get(code)
        
    if parse is not None:
        # cmd = parse(bb)
        # result = exec(cmd)
        result = parse(bb)
    return result

# Parse recieved bytecode to TLV-packets
def parse_data(bb):
    offset = 0
    while offset < len(bb) and len(bb) > 3:
        # head have length of 3 bytes. We need length of body
        head = bb[offset : offset + 3]
        command, length = struct.unpack('>bh', head)

        # taking body with length 'length'        
        if length != 0:
            body = bb[offset + 3 : offset + 3 + length]
        else:
            body = b''

        # stickign head and body and take to parse single TLV-packet
        status = parse_command(head + body)
        offset += 3 + length

# describe tha actions of lantern in every situation
class EchoClientProtocol(asyncio.Protocol):
    def __init__(self, on_con_lost):
        # self.message = message
        self.on_con_lost = on_con_lost
    
    # on connection print status of connetion    
    def connection_made(self, transport):
        addr = transport.get_extra_info('peername')
        print(f'Connected to {addr!r}')
    
    # on data receive we parse the data
    def data_received(self, data):
        # print(f'Data recieved: \n{data!r}')
        parse_data(data)
    
    # on connection lost write message and set the Flag
    def connection_lost(self, exc):
        print('Server closed connection')
        self.on_con_lost.set_result(True)

# Start the client
async def main():
    loop = asyncio.get_running_loop()
    
    on_con_lost = loop.create_future()
        
    transport, protocol = await loop.create_connection(
        lambda: EchoClientProtocol(on_con_lost), 
        SERVER_ADDRESS, SERVER_PORT)
    
    # action on connection lost - close connection on lantern
    try:
        await on_con_lost
    finally:
        transport.close()
        print('Lantern closed connection')

asyncio.run(main())