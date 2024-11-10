import sys
import socket
import json
import time
from PyQt6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QWidget, QTextEdit, 
                             QLabel, QTabWidget, QPushButton, QHBoxLayout)
from PyQt6.QtCore import QThread, pyqtSignal, QObject, Qt
from PyQt6.QtGui import QFont

MAX_RETRIES = 5
ACK_TIMEOUT = 1.0  # Timeout for acknowledgment in seconds

class SignalEmitter(QObject):
    log_update = pyqtSignal(str)
    request_update = pyqtSignal(str)
    response_update = pyqtSignal(str)

class RPCServer(QThread):
    def __init__(self, host='localhost', port=8000):
        super().__init__()
        self._methods = {}
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_socket.bind((self.host, self.port))
        self.signal_emitter = SignalEmitter()

    def register_method(self, name, method):
        self._methods[name] = method

    def run(self):
        self.signal_emitter.log_update.emit(f'UDP RPC Server listening on {self.host}:{self.port}')
        while True:
            data, client_address = self.server_socket.recvfrom(4096)
            client_ip, client_port = client_address
            self.signal_emitter.log_update.emit(f'Received request from {client_ip}:{client_port}')

            self.server_socket.sendto("ACK".encode(), client_address)
            self.signal_emitter.log_update.emit(f"Sent acknowledgment to client {client_ip}:{client_port} for request.")

            try:
                function_name, args, kwargs, sequence_number = json.loads(data.decode())
                self.signal_emitter.request_update.emit(f'Client: {client_ip}:{client_port}, Function: {function_name}, Args: {args}, Kwargs: {kwargs}, Sequence: {sequence_number}')
            except Exception as e:
                error_message = f"Error: Invalid request format from {client_ip}:{client_port}. {e}"
                self.server_socket.sendto(error_message.encode(), client_address)
                continue

            try:
                if function_name in self._methods:
                    response = self._methods[function_name](*args, **kwargs)
                else:
                    response = f"Error: Function '{function_name}' not found."
            except Exception as e:
                response = f"Error while executing function: {e}"

            response_data = json.dumps([response, sequence_number]).encode()
            attempts = 0

            while attempts < MAX_RETRIES:
                self.server_socket.sendto(response_data, client_address)
                self.signal_emitter.response_update.emit(f"Sent response to {client_ip}:{client_port}: {response}, Sequence: {sequence_number}, Attempt: {attempts + 1}")

                try:
                    self.server_socket.settimeout(ACK_TIMEOUT)
                    ack, _ = self.server_socket.recvfrom(4096)
                    if ack.decode() == "ACK":
                        self.signal_emitter.log_update.emit(f"Acknowledgment received from client {client_ip}:{client_port} for response (Sequence: {sequence_number}).")
                        break
                except socket.timeout:
                    self.signal_emitter.log_update.emit(f"No acknowledgment from client {client_ip}:{client_port}, resending response (Sequence: {sequence_number})...")
                    attempts += 1

            self.server_socket.settimeout(None)

            if attempts == MAX_RETRIES:
                self.signal_emitter.log_update.emit(f"Failed to receive acknowledgment from client {client_ip}:{client_port} after multiple attempts (Sequence: {sequence_number}).")

class ServerGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.startServer()

    def initUI(self):
        self.setWindowTitle('UDP RPC Server')
        self.setGeometry(100, 100, 800, 600)

        self.setStyleSheet("""
            QMainWindow, QWidget {
                background-color: #F0F4F8;
                color: #2D3748;
            }
            QLabel {
                font-size: 16px;
            }
            QTextEdit {
                background-color: #FFFFFF;
                border: 1px solid #E2E8F0;
                border-radius: 5px;
                padding: 5px;
                font-family: monospace;
                font-size: 14px;
            }
            QPushButton {
                background-color: #4299E1;
                color: white;
                border: none;
                padding: 10px 20px;
                font-size: 16px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #3182CE;
            }
            QTabWidget::pane {
                border: 1px solid #E2E8F0;
                background: white;
            }
            QTabWidget::tab-bar {
                left: 5px;
            }
            QTabBar::tab {
                background: #EDF2F7;
                border: 1px solid #E2E8F0;
                padding: 5px;
            }
            QTabBar::tab:selected {
                background: white;
            }
        """)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout()

        self.tab_widget = QTabWidget()
        
        # Log tab
        log_tab = QWidget()
        log_layout = QVBoxLayout()
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        log_layout.addWidget(self.log_text)
        log_tab.setLayout(log_layout)
        self.tab_widget.addTab(log_tab, "Log")

        # Requests tab
        requests_tab = QWidget()
        requests_layout = QVBoxLayout()
        self.requests_text = QTextEdit()
        self.requests_text.setReadOnly(True)
        requests_layout.addWidget(self.requests_text)
        requests_tab.setLayout(requests_layout)
        self.tab_widget.addTab(requests_tab, "Requests")

        # Responses tab
        responses_tab = QWidget()
        responses_layout = QVBoxLayout()
        self.responses_text = QTextEdit()
        self.responses_text.setReadOnly(True)
        responses_layout.addWidget(self.responses_text)
        responses_tab.setLayout(responses_layout)
        self.tab_widget.addTab(responses_tab, "Responses")

        layout.addWidget(self.tab_widget)

        status_layout = QHBoxLayout()
        self.status_label = QLabel("Server Status: Running")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        status_layout.addWidget(self.status_label)

        self.clear_button = QPushButton("Clear Logs")
        self.clear_button.clicked.connect(self.clear_logs)
        status_layout.addWidget(self.clear_button)

        layout.addLayout(status_layout)

        central_widget.setLayout(layout)

    def startServer(self):
        self.server = RPCServer()
        self.server.register_method("add", lambda *args: sum(args) if len(args) >= 2 else "Error: At least 2 arguments required")
        self.server.register_method("multiply", lambda *args: (lambda x: x if len(args) >= 2 else "Error: At least 2 arguments required")(
            __import__('functools').reduce(lambda x, y: x * y, args)))
        self.server.register_method("subtract", lambda *args: (lambda x: x if len(args) >= 2 else "Error: At least 2 arguments required")(
            args[0] - sum(args[1:])))
        self.server.signal_emitter.log_update.connect(self.update_log)
        self.server.signal_emitter.request_update.connect(self.update_requests)
        self.server.signal_emitter.response_update.connect(self.update_responses)
        self.server.start()

    def update_log(self, message):
        self.log_text.append(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - {message}")

    def update_requests(self, message):
        self.requests_text.append(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - {message}")

    def update_responses(self, message):
        self.responses_text.append(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - {message}")

    def clear_logs(self):
        self.log_text.clear()
        self.requests_text.clear()
        self.responses_text.clear()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    server_gui = ServerGUI()
    server_gui.show()
    sys.exit(app.exec())