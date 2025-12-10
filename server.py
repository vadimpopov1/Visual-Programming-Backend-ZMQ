import zmq
import json
import os
import sys
import select
import signal
import atexit

class Server:
    def __init__(self):
        self.counter = 0
        self.data_dir = "/app/data"
        self.data_file = os.path.join(self.data_dir, "android_data.json")
        
        os.makedirs(self.data_dir, exist_ok=True)
        
        if not os.path.exists(self.data_file):
            with open(self.data_file, 'w') as f:
                json.dump([], f)
    
    def save_data(self, data):
        try:
            with open(self.data_file, 'r') as f:
                all_data = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            all_data = []
        
        all_data.append(data)
        
        with open(self.data_file, 'w') as f:
            json.dump(all_data, f, indent=2)
        
        self.counter += 1
    
    def cleanup(self):
        print("\nСервер останавливается...")
        print(f"Всего обработано сообщений: {self.counter}")
    
    def start(self):
        atexit.register(self.cleanup)
        
        context = zmq.Context()
        socket = context.socket(zmq.REP)
        socket.bind("tcp://0.0.0.0:5555")
        
        print("Сервер запущен на порту 5555")
        print(f"Данные сохраняются в: {self.data_file}")
        
        socket.RCVTIMEO = 100
        
        while True:
            try:
                message = socket.recv_string()
                print(f"GET: {message}")
                
                self.save_data(message)
                
                response = f"Hello from Server! {self.counter}"
                socket.send_string(response)
                
                print(f"SEND: {response}")
                
            except zmq.Again:
                pass
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"Ошибка: {e}")

if __name__ == "__main__":
    server = Server()
    server.start()