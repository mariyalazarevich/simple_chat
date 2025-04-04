import socket
import threading

def handle_client(client_socket, client_address, clients, names):
    client_name = client_socket.recv(1024).decode('utf-8')
    names[client_socket] = client_name
    print(f"[{client_name}] подключился с {client_address}.")
    try:
        while True:
            message = client_socket.recv(1024).decode('utf-8')
            if not message:
                break
            print(f"[{client_name}]: {message}")
            broadcast_message(f"[{client_name}]: {message}", client_socket, clients)
    except ConnectionResetError:
        print(f"[{client_name}] отключился.")
    finally:
        remove_client(client_socket, clients, names)

def broadcast_message(message, sender_socket, clients):
    for client in clients:
        if client != sender_socket:
            try:
                client.send(message.encode('utf-8'))
            except:
                pass

def remove_client(client_socket, clients, names):
    clients.remove(client_socket)
    client_name = names.pop(client_socket, "Неизвестный клиент")
    print(f"[{client_name}] отключился.")
    client_socket.close()

def start_server(ip, port, server_socket):
    server_socket.listen(5)
    print(f"[Сервер] Запущен на {ip}:{port}.")
    print("Введите 'stop' для остановки сервера.")
    clients = []
    names = {}

    def accept_clients():
        while True:
            try:
                client_socket, client_address = server_socket.accept()
                clients.append(client_socket)
                print(f"[Сервер] Клиент подключился с {client_address}.")
                threading.Thread(
                    target=handle_client,
                    args=(client_socket, client_address, clients, names),
                    daemon=True
                ).start()
            except OSError:
                break

    threading.Thread(target=accept_clients, daemon=True).start()
    while True:
        command = input()
        if command.lower() == "stop":
            break

    print("[Сервер] Остановка...")
    for client in clients:
        client.close()
    server_socket.close()
    print("[Сервер] Остановлен.")

def start_client(server_ip, server_port, username, ip):
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.bind((ip, 0))
        client_socket.connect((server_ip, server_port))
    except ConnectionRefusedError:
        print("[Клиент] Не удалось подключиться к серверу. Проверьте адрес и порт.")
        return
    client_socket.send(username.encode('utf-8'))

    def receive_messages():
        while True:
            try:
                message = client_socket.recv(1024).decode('utf-8')
                if not message:
                    break
                print(message)
            except:
                print("[Клиент] Соединение с сервером потеряно.")
                break

    threading.Thread(target=receive_messages, daemon=True).start()

    try:
        while True:
            message = input()
            if message.lower() == "exit":
                break
            client_socket.send(message.encode('utf-8'))
    except:
        pass
    finally:
        client_socket.close()
        print("[Клиент] Отключен.")

def main():
    print("Выберите режим:\n1 - Сервер\n2 - Клиент")
    choice = input("Введите 1 или 2: ")
    if choice == "1":
        start = True
        while start:
            ip = input("Введите IP для сервера (по умолчанию 0.0.0.0): ") or "0.0.0.0"
            port = int(input("Введите порт для сервера: "))
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                server_socket.bind((ip, port))
                start_server(ip, port, server_socket)
                start = False
            except OSError:
                print(f"Порт {port} уже используется. Попробуйте другой порт.")
                start = True
    elif choice == "2":
        server_ip = input("Введите IP сервера: ")
        server_port = int(input("Введите порт сервера: "))
        username = input("Введите ваше имя пользователя: ")
        ip = input("Введите ваш ip-адрес: ")
        start_client(server_ip, server_port, username, ip)
    else:
        print("Неверный выбор. Завершение.")


if __name__ == "__main__":
    main()