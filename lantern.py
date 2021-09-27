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

# functions to parse recieved commands
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

# parse recieved bytecode
def parse_command(bb):
    code = bb[0]
    result = 'SILENT'
    parse = None
    
    parse = COMMANDS.get(code)
        
    if parse is not None:
        cmd = parse(bb)
        # result = exec(cmd)
        result = cmd
    return result


async def tcp_echo_client():
    reader, writer = await asyncio.open_connection(SERVER_ADDRESS, SERVER_PORT)
    
    addr = writer.get_extra_info('peername')
    print(f'Esteblished conection with {addr!r}')

    while True:
        # addr = writer.get_extra_info('peername')
        head =  await reader.read(3)
                
        command, length = struct.unpack('>bh', head)
        # command, length = data[0], data[1:]
        if length != 0:
            data = await reader.read(length)
        else:
            data = b''
        # print(f'{command!r}, {length!r}, {head+data!r}')
        
        status = parse_command(head + data)
            
        print(f'Status: {status}')
        # if status == 'OFF':
        #     break
    
    print('Close the connection')
    writer.close()
    

asyncio.run(tcp_echo_client())