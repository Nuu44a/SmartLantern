import asyncio
import struct

SERVER_ADDRESS = '127.0.0.1'
SERVER_PORT = 9999

HELLO_MESSAGE = '''
    Send command to lantern.
    Avaliable commands:
    1 - Turn light ON
    2 - Change COLOR of the light
    3 - Unavailable command
    0 - Turn light OFF
'''


def command_on():
    # Команда на включение фонаря
    return struct.pack('>bh', 0x12, 0)

def command_off():
    # Команда на выключение фонаря
    return struct.pack('>bh', 0x13, 0)

def command_error():
    # Несуществующая команда
    return struct.pack('>bh', 0x14, 0)

def command_color():
    # Изменение цвета фонаря
    print('Input color in format "#RRGGBB" (00-FF)')
    color = input().lstrip('#')
    r, g, b = [int(color[i:i+2], 16) for i in [0, 2, 4]]
    # bytearr = struct.pack('>bhbbb', 0x20, 0, r-128, g-128, b-128)
    return struct.pack('>bhbbb', 0x20, 3, r-128, g-128, b-128)


async def handle_echo(reader, writer):
    data = await reader.read(10)
    status = data.decode()
    addr = writer.get_extra_info('peername')
    print(f'Esteblished conection with {addr!r}, status is {status!r}')
    
    # В этом цикле отправляем команды клиенту
    while True:
        # Выводим краткую инструкцию и получаем команду для клиента
        tlv = ''
        
        print(HELLO_MESSAGE)
        command_to_client = input('Choose command to Client -> ')
        
        # Формируем TLV-строку для отправки клиенту
        if command_to_client == '1':
            tlv = command_on()
        elif command_to_client == '2':
            tlv = command_color()
        elif command_to_client == '3':
            tlv = command_error()
        elif command_to_client == '0':
            tlv = command_off()
        else:
            print('Wrong command. Try again.')
            continue
            
        print(f'Send: {tlv!r}')
        writer.write(tlv)
        await writer.drain()

        # Получаем подтверждение от клиента
        data = await reader.read(10)
        status = data
        print(f'Command recieved, new status is {status!r}')
        
        if command_to_client == '0':
            break
        
    # Прощаемся и закрываем соединение
    print('Close the connection')
    writer.close()


async def main():
    server = await asyncio.start_server(handle_echo, SERVER_ADDRESS, SERVER_PORT)
    
    addr = server.sockets[0].getsockname()
    print(f'Serving on {addr}')
    
    async with server:
        await server.serve_forever()
    
# Close the server
    server.close()
    print('Server SHUTDOWN')

asyncio.run(main())