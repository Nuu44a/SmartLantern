import asyncio

SERVER_ADDRESS = '127.0.0.1'
SERVER_PORT = 9999

COMMAND_LIST = ['0x12', '0x13', '0x20']
HELLO_MESSAGE = '''
    Send command to lantern in HEX.
    Avaliable commands:
    0x00 - Disconnect
    0x12 - Turn light ON
    0x13 - Turn light OFF
    0x20 - Change COLOR of the light
    '''

async def handle_echo(reader, writer):
    '''
        Функция обслуживания клиента
    '''
    command_to_client = '0x00'
    # Ждем клиента, читаем его статус
    data = await reader.read()
    status = data.decode()
    # Получаем адрес клиента
    await writer.drain()
    addr = writer.get_extra_info('peername')
    # Выводим сообщение о соединении и статус клиента
    print(f'Esteblished conection with {addr!r}, status is {status!r}')
    
    # В этом цикле отправляем команды клиенту
    while command_to_client:
        # Выводим краткую инструкцию и получаем команду для клиента
        tlv = ''
        print(HELLO_MESSAGE)
        command_to_client = input('Write command to Client -> ')
        
        # Если команда существует, то обрабатываем ее
        if command_to_client in COMMAND_LIST:
            # Формируем TLV-строку для отправки клиенту
            if command_to_client == '0x20':
            
            else:
                tlv += hex(int(command_to_client, 16))
                
            print(f'Send: {command_to_client!r}')
            writer.write(command_to_client.encode())
            await writer.drain()
            
            # Получаем подтверждение от клиента
            data = await reader.read()
            message = data.decode()
            print(f'Command recieved, new status is {status!r}')
        # Команда на отключение от клиента
        elif command_to_client == '0x00':
            command_to_client = ''
        # Проверка на дурака и повторяем цикл
        else:
            print('Unsupported command!')
        
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