import sys
import json
import socket
import time
from PyQt6.QtWidgets import (QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QTextEdit, 
                             QLabel, QHBoxLayout, QLineEdit, QComboBox, QScrollArea, QFrame, QProgressDialog,
                             QDialog, QMessageBox, QTabWidget)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QObject

SIZE = 1024
ACK_TIMEOUT = 1 
MAX_RETRIES = 5 

class SignalEmitter(QObject):
    status_update = pyqtSignal(str)
    log_update = pyqtSignal(str)

class ReliableUDPClient:
    def __init__(self, server_address):
        self.server_address = server_address
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sequence_number = 0
        self.signal_emitter = SignalEmitter()

    def send_request(self, function_name, args=[], kwargs={}):
        request_packet = json.dumps([function_name, args, kwargs, self.sequence_number]).encode()
        start_time = time.time()

        self.signal_emitter.log_update.emit(f"--- Request {self.sequence_number} ---")
        self.signal_emitter.log_update.emit(f"Function: {function_name}")
        self.signal_emitter.log_update.emit(f"Arguments: {args}")
        self.signal_emitter.log_update.emit(f"Keyword Arguments: {kwargs}")

        for attempt in range(MAX_RETRIES):
            self.client_socket.sendto(request_packet, self.server_address)
            self.signal_emitter.log_update.emit(f'Sent request with sequence {self.sequence_number} (Attempt {attempt + 1}/{MAX_RETRIES})')

            self.client_socket.settimeout(ACK_TIMEOUT)
            try:
                ack, _ = self.client_socket.recvfrom(SIZE)
                if ack == b'ACK':
                    self.signal_emitter.log_update.emit(f'Received ACK for sequence {self.sequence_number}')
                    break
            except socket.timeout:
                self.signal_emitter.log_update.emit(f'No ACK, retrying... {attempt + 1}/{MAX_RETRIES}')

        if attempt == MAX_RETRIES - 1:
            self.signal_emitter.log_update.emit('Max retries reached. Request failed.')
            self.signal_emitter.log_update.emit("------------------------")
            return None, None

        self.client_socket.settimeout(None)
        response_packet, _ = self.client_socket.recvfrom(SIZE)
        end_time = time.time()
        response_time = (end_time - start_time) * 1000  # Convert to milliseconds

        response, seq = json.loads(response_packet.decode())

        if seq == self.sequence_number:
            self.signal_emitter.log_update.emit(f'Received response: {response}')
            self.signal_emitter.log_update.emit(f'Response time: {response_time:.2f} ms')
            
            # Send acknowledgment
            self.client_socket.sendto("ACK".encode(), self.server_address)
            self.signal_emitter.log_update.emit('Sent acknowledgment for response')
            
            self.sequence_number += 1
        else:
            self.signal_emitter.log_update.emit('Mismatched response sequence number.')
            response, response_time = None, None

        self.signal_emitter.log_update.emit("------------------------")
        return response, response_time

class LoginWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Login')
        self.setGeometry(200, 200, 300, 150)
        
        layout = QVBoxLayout()
        
        self.username_input = QLineEdit()
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        
        layout.addWidget(QLabel('Username:'))
        layout.addWidget(self.username_input)
        layout.addWidget(QLabel('Password:'))
        layout.addWidget(self.password_input)
        
        login_button = QPushButton('Login')
        login_button.clicked.connect(self.login)
        layout.addWidget(login_button)
        
        signup_button = QPushButton('Sign Up')
        signup_button.clicked.connect(self.show_signup)
        layout.addWidget(signup_button)
        
        self.setLayout(layout)
    
    def login(self):
        with open("login_data.txt", "r") as login_database:
            data = login_database.readlines()
            users = [line.strip().split() for line in data]
            for current_user, current_password in users:
                if current_user == self.username_input.text() and current_password == self.password_input.text():
                    QMessageBox.information(self, 'Login Successful', f'Welcome {self.username_input.text()}')
                    self.accept()
                    return
                elif current_user == self.username_input.text():
                    QMessageBox.warning(self, 'Login Failed', 'Password is wrong')
                    return 
        
        QMessageBox.warning(self, 'Login Failed', 'Username not found in database')

    def show_signup(self):
        self.hide()
        signup_window = SignupWindow(self.parent())
        if signup_window.exec() == QDialog.DialogCode.Accepted:
            self.show()
        else:
            self.show()

class SignupWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Sign Up')
        self.setGeometry(200, 200, 300, 200)
        
        layout = QVBoxLayout()
        
        self.username_input = QLineEdit()
        self.email_input = QLineEdit()
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.confirm_password_input = QLineEdit()
        self.confirm_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        
        layout.addWidget(QLabel('Username:'))
        layout.addWidget(self.username_input)
        layout.addWidget(QLabel('Email:'))
        layout.addWidget(self.email_input)
        layout.addWidget(QLabel('Password:'))
        layout.addWidget(self.password_input)
        layout.addWidget(QLabel('Confirm Password:'))
        layout.addWidget(self.confirm_password_input)
        
        signup_button = QPushButton('Sign Up')
        signup_button.clicked.connect(self.signup)
        layout.addWidget(signup_button)
        
        self.setLayout(layout)
    
    def signup(self):
        if self.password_input.text() != self.confirm_password_input.text():
            QMessageBox.warning(self, 'Sign Up Failed', 'Passwords do not match')
            return
        with open("login_data.txt", "a") as login_database:
            login_database.write(f"{self.username_input.text()} {self.password_input.text()}\n")
        QMessageBox.information(self, 'Sign Up Successful', 'You can now log in with your new account')
        self.accept()

class UDPRPCClient(QMainWindow):
    def __init__(self):
        super().__init__()
        self.logged_in_user = ""
        self.initUI()
        self.udp_client = ReliableUDPClient(('127.0.0.1', 8000))
        self.udp_client.signal_emitter.status_update.connect(self.update_status)
        self.udp_client.signal_emitter.log_update.connect(self.update_log)
        self.show_login()

    def initUI(self):
        self.setWindowTitle('UDP RPC Client')
        self.setGeometry(100, 100, 600, 700)

        self.setStyleSheet("""
            QMainWindow, QWidget {
                background-color: #F0F4F8;
                color: #2D3748;
            }
            QLabel {
                font-size: 16px;
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
            QTextEdit, QLineEdit {
                background-color: #EDF2F7;
                color: #2D3748;
                border: 1px solid #CBD5E0;
                border-radius: 5px;
                padding: 5px;
                font-size: 14px;
            }
            QComboBox {
                background-color: #EDF2F7;
                color: #2D3748;
                border: 1px solid #CBD5E0;
                border-radius: 5px;
                padding: 5px;
                font-size: 14px;
                min-height: 20px;
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 20px;
                border-left-width: 1px;
                border-left-color: #CBD5E0;
                border-left-style: solid;
            }
            QComboBox::down-arrow {
                image: url(down_arrow.png);
                width: 14px;
                height: 14px;
            }
            QScrollArea {
                border: none;
            }
            QTabWidget::pane {
                border: 1px solid #CBD5E0;
                background: white;
            }
            QTabWidget::tab-bar {
                left: 5px;
            }
            QTabBar::tab {
                background: #EDF2F7;
                border: 1px solid #CBD5E0;
                padding: 5px;
            }
            QTabBar::tab:selected {
                background: white;
            }
        """)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout()

        self.title_label = QLabel("UDP RPC Client")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setFont(QFont("Arial", 32, QFont.Weight.Bold))
        self.title_label.setStyleSheet("font-size: 40px; color: #2C5282; margin-bottom: 20px;")
        main_layout.addWidget(self.title_label)

        header_layout = QHBoxLayout()
        header_layout.addStretch()  # This pushes everything to the right

        header_right = QHBoxLayout()
        self.user_info_label = QLabel(f"Welcome, {self.logged_in_user}")
        self.user_info_label.setStyleSheet("font-size: 20px; color: #4A5568; padding-right: 10px;")
        self.logout_button = QPushButton("Logout")
        self.logout_button.clicked.connect(self.logout)
        self.logout_button.setStyleSheet("""
            QPushButton {
                background-color: #E53E3E;
                color: white;
                border: none;
                padding: 5px 10px;
                font-size: 14px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #C53030;
            }
        """)
        header_right.addWidget(self.user_info_label)
        header_right.addWidget(self.logout_button)

        header_layout.addLayout(header_right)
        main_layout.addLayout(header_layout)

        function_layout = QHBoxLayout()
        function_layout.addStretch()
        function_label = QLabel("Function:")
        function_label.setFont(QFont("Arial", 32, QFont.Weight.Bold))

        function_label.setStyleSheet("font-size: 30px; margin-right: 10px;")
        self.function_combo = QComboBox()
        self.function_combo.addItems(["add", "multiply", "subtract"])
        self.function_combo.setStyleSheet("""
            QComboBox {
                background-color: #EBF8FF;
                color: #2B6CB0;
                border: 1px solid #90CDF4;
                border-radius: 5px;
                padding: 5px 30px 5px 10px;
                font-size: 14px;
                min-height: 30px;
                min-width: 150px;
            }
            QComboBox::drop-down {
                border: none;
                width: 30px;
            }
            QComboBox::down-arrow {
                image: url(down_arrow.png);
                width: 12px;
                height: 12px;
                margin-right: 15px;
            }
            QComboBox::down-arrow:on {
                top: 1px;
            }
            QComboBox:hover {
                background-color: #BEE3F8;
            }
            QComboBox QAbstractItemView {
                background-color: #EBF8FF;
                border: 1px solid #90CDF4;
                selection-background-color: #90CDF4;
            }
        """)
        function_layout.addWidget(function_label)
        function_layout.addWidget(self.function_combo)
        function_layout.addStretch()
        main_layout.addLayout(function_layout)
        main_layout.addSpacing(20)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_content = QWidget()
        self.param_layout = QVBoxLayout(scroll_content)
        scroll.setWidget(scroll_content)
        main_layout.addWidget(scroll)

        self.add_parameter()
        self.add_parameter()

        add_param_button = QPushButton("Add Parameter")
        add_param_button.clicked.connect(self.add_parameter)
        add_param_button.setStyleSheet("""
            QPushButton {
                background-color: #4299E1;
                color: white;
                border: none;
                padding: 8px 16px;
                font-size: 14px;
                border-radius: 5px;
                max-width: 150px;
            }
            QPushButton:hover {
                background-color: #3182CE;
            }
        """)
        main_layout.addWidget(add_param_button, alignment=Qt.AlignmentFlag.AlignCenter)

        self.call_button = QPushButton("Call Remote Function")
        self.call_button.clicked.connect(self.call_remote_function)
        self.call_button.setStyleSheet("""
            QPushButton {
                background-color: #48BB78;
                color: white;
                border: none;
                padding: 10px 20px;
                font-size: 16px;
                border-radius: 5px;
                min-width: 200px;
            }
            QPushButton:hover {
                background-color: #38A169;
            }
        """)
        main_layout.addWidget(self.call_button)

        self.tab_widget = QTabWidget()
        
        # Result tab
        result_tab = QWidget()
        result_layout = QVBoxLayout()
        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        result_layout.addWidget(self.result_text)
        result_tab.setLayout(result_layout)
        self.tab_widget.addTab(result_tab, "Result")

        # Log tab
        log_tab = QWidget()
        log_layout = QVBoxLayout()
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        log_layout.addWidget(self.log_text)
        log_tab.setLayout(log_layout)
        self.tab_widget.addTab(log_tab, "Log")

        summary_tab = QWidget()
        summary_layout = QVBoxLayout()
        self.summary_table = QTextEdit()
        self.summary_table.setReadOnly(True)
        summary_layout.addWidget(self.summary_table)
        summary_tab.setLayout(summary_layout)
        self.tab_widget.addTab(summary_tab, "Summary")

        main_layout.addWidget(self.tab_widget)

        self.status_label = QLabel("Status: Ready")
        main_layout.addWidget(self.status_label)


        central_widget.setLayout(main_layout)

    def show_login(self):
        login_window = LoginWindow(self)
        if login_window.exec() == QDialog.DialogCode.Accepted:
            self.logged_in_user = login_window.username_input.text()
            self.update_user_info()
            self.show()
        else:
            self.close()

    def logout(self):
        self.logged_in_user = ""
        self.hide()
        self.show_login()

    def add_parameter(self):
        param_widget = QFrame()
        param_widget.setFrameShape(QFrame.Shape.StyledPanel)
        param_widget.setFrameShadow(QFrame.Shadow.Raised)
        param_layout = QHBoxLayout(param_widget)
        
        param_label = QLabel(f"Parameter {self.param_layout.count() + 1}:")
        param_input = QLineEdit()
        remove_button = QPushButton("Remove")
        remove_button.clicked.connect(lambda: self.remove_parameter(param_widget))
        
        param_layout.addWidget(param_label)
        param_layout.addWidget(param_input)
        param_layout.addWidget(remove_button)
        
        self.param_layout.addWidget(param_widget)

    def remove_parameter(self, param_widget):
        if self.param_layout.count() > 2:  
            self.param_layout.removeWidget(param_widget)
            param_widget.deleteLater()
            self.update_param_labels()
        else:
            self.status_label.setText("Status: Minimum 2 parameters required")

    def update_param_labels(self):
        for i in range(self.param_layout.count()):
            widget = self.param_layout.itemAt(i).widget()
            label = widget.layout().itemAt(0).widget()
            label.setText(f"Parameter {i + 1}:")

    def call_remote_function(self):
        self.call_button.setEnabled(False)
        self.status_label.setText("Status: Preparing to call remote function...")
        self.result_text.clear()

        function = self.function_combo.currentText()
        params = []

        for i in range(self.param_layout.count()):
            widget = self.param_layout.itemAt(i).widget()
            param_input = widget.layout().itemAt(1).widget()
            try:
                param_value = float(param_input.text())
                params.append(param_value)
            except ValueError:
                self.result_text.setPlainText(f"Error: Parameter {i + 1} must be a number")
                self.status_label.setText("Status: Invalid parameters")
                self.call_button.setEnabled(True)
                return

        self.progress = QProgressDialog("Calling remote function...", "Cancel", 0, 100, self)
        self.progress.setWindowModality(Qt.WindowModality.WindowModal)
        self.progress.setAutoReset(False)
        self.progress.setAutoClose(False)
        self.progress.setValue(0)
        self.progress.show()

        self.timer = QTimer(self)
        self.timer.timeout.connect(lambda: self.update_progress(function, params))
        self.timer.start(100) 

    def update_progress(self, function, params):
        if self.progress.wasCanceled():
            self.status_label.setText("Status: Operation canceled")
            self.call_button.setEnabled(True)
            self.timer.stop()
            return

        current_value = self.progress.value()
        if current_value < 100:
            self.progress.setValue(current_value + 5)
        else:
            self.timer.stop()
            self.status_label.setText("Status: Waiting for response...")

            response, response_time = self.udp_client.send_request(function, args=params)

            if response is not None:
                self.result_text.setPlainText(f"Result: {response}\nResponse time: {response_time:.2f} ms")
                summary = f"""
                <table border='1' cellpadding='5'>
                <tr><th>Function</th><td>{function}</td></tr>
                <tr><th>Arguments</th><td>{', '.join(map(str, params))}</td></tr>
                <tr><th>Response</th><td>{response}</td></tr>
                <tr><th>Response Time</th><td>{response_time:.2f} ms</td></tr>
                </table>
                """
                self.summary_table.setHtml(summary)
                self.status_label.setText("Status: Function call successful, sent acknowledgment")
            else:
                self.result_text.setPlainText("Error: Function call failed")
                self.status_label.setText("Status: Function call failed")

            self.call_button.setEnabled(True)
            self.progress.close()

    def update_status(self, message):
        self.status_label.setText(f"Status: {message}")

        if hasattr(self, 'progress') and self.progress.isVisible():
            self.progress.setLabelText(message)

        QApplication.processEvents()

    def update_log(self, message):
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
        formatted_message = f"{timestamp} - {message}"
        self.log_text.append(formatted_message)
        self.log_text.ensureCursorVisible()
        QApplication.processEvents()

    def update_user_info(self):
        self.user_info_label.setText(f"Welcome, {self.logged_in_user}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    client = UDPRPCClient()
    sys.exit(app.exec())