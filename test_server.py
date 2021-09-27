import asyncio
import struct
import random

SERVER_ADDRESS = '127.0.0.1'
SERVER_PORT = 9999

# Генерируем команды на отправку клиенту
dic = {1: 0x12, 2: 0x13, 3: 0x14, 4: 0x20}

def gc():
    x, y = -128, 127
    return random.randint(x, y)

def gen_com():
    num = random.randint(1, 4)
    x = struct.pack('>b', dic[num])
    if num == 4:
        x = x + struct.pack('>h', 3)
        x = x + struct.pack('>bbb', gc(), gc(), gc())
    else:
        x = x + struct.pack('>h', 0)
    print(f'{x!r}')
    return x

# Формируем пачку команд        
def gen_tlv(ln=5):
    tlv = b''
    for _ in range(ln):
        tlv = tlv + gen_com()
    return tlv

# Отправляем клиенту команды
async def handle_echo(reader, writer):
    flag = True
    
    addr = writer.get_extra_info('peername')
    print(f'Esteblished conection with {addr!r}')
    
    # В этом цикле отправляем команды клиенту
    while True:
        num = random.randint(5, 10)
        tlv = gen_tlv(num)
        
        # print(f'Send: {tlv!r}')
        writer.write(tlv)
        await writer.drain()
        
        # flag = int(input('Repeat - 1, exit - 0 -> '))
        if not flag:
            break
        # break
        
    # Прощаемся и закрываем соединение
    print('Close the connection')
    writer.close()


async def main():
    server = await asyncio.start_server(handle_echo, SERVER_ADDRESS, SERVER_PORT)
    
    addr = server.sockets[0].getsockname()
    print(f'Serving on {addr}')
    
    async with server:
        await server.serve_forever()
    
asyncio.run(main())