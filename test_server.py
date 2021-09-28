import asyncio
import struct
import random

SERVER_ADDRESS = '127.0.0.1'
SERVER_PORT = 9999


# Генерируем команды на отправку клиенту
# Словарь доступных команд
dic = {1: 0x12, 2: 0x13, 3: 0x14, 4: 0x20}

# Генератор цветов RGB
def gc():
    x, y = -128, 127
    return random.randint(x, y)

# Генератор случайных команд
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


# Действия сервера при подключении клиента
class EchoServerProtocol(asyncio.Protocol):
    def connection_made(self, transport):
        peername = transport.get_extra_info('peername')
        print('Connection from {}'.format(peername))
        
        self.transport = transport
        sock = transport.get_extra_info('socket')
        
        flag = 1
        while flag:
            flag = int(input('Send pack of commands to client - 1, exit - 0 -> '))
            num = random.randint(5, 10)
            tlv = gen_tlv(num)
            sock.sendall(tlv)
            
            if not flag:
                break
        
        print('Close the client socket')
        self.transport.close()


# Запуск сервера
async def main():
    loop = asyncio.get_running_loop()

    server = await loop.create_server(
        lambda: EchoServerProtocol(),
        '127.0.0.1', 9999)
    
    addr = server.sockets[0].getsockname()
    print(f'Serving on {addr}')

    async with server:
        await server.serve_forever()


# Обработка CTRL+C
try:
    asyncio.run(main())
except KeyboardInterrupt:
    print('ServerSHUTDOWN')