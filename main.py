#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SSH工具 - Android版本
使用Kivy框架构建移动端界面
"""

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.clock import Clock
from kivy.utils import platform
import threading
import queue
import json
import os
import base64
from datetime import datetime

try:
    import paramiko
    HAS_PARAMIKO = True
except ImportError:
    HAS_PARAMIKO = False

# 密码加密密钥（与桌面版保持一致）
_PASSWORD_ENCRYPTION_KEY = "liulang_gm_tool_2024_encrypt_key_v1.0.1"

# 全局输出队列
output_queue = queue.Queue()


def encrypt_password(password):
    """加密密码（与桌面版兼容）"""
    if not password:
        return ""
    try:
        # 使用XOR加密 + Base64编码
        key = _PASSWORD_ENCRYPTION_KEY
        encrypted = bytearray()
        for i, char in enumerate(password):
            key_char = key[i % len(key)]
            encrypted.append(ord(char) ^ ord(key_char))
        return base64.b64encode(encrypted).decode('utf-8')
    except:
        return password  # 加密失败则返回原密码


def decrypt_password(encrypted_password):
    """解密密码（与桌面版兼容）"""
    if not encrypted_password:
        return ""
    try:
        # 先尝试解密（Base64解码 + XOR解密）
        key = _PASSWORD_ENCRYPTION_KEY
        encrypted_bytes = base64.b64decode(encrypted_password.encode('utf-8'))
        decrypted = bytearray()
        for i, byte in enumerate(encrypted_bytes):
            key_char = key[i % len(key)]
            decrypted.append(byte ^ ord(key_char))
        return decrypted.decode('utf-8')
    except:
        # 如果解密失败，可能是旧格式的明文密码，直接返回
        return encrypted_password


class ConnectionScreen(Screen):
    """连接界面"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app = None
        
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # 标题
        title = Label(text='SSH连接工具', size_hint_y=None, height=50, font_size=24)
        layout.add_widget(title)
        
        # 连接信息输入
        form_layout = GridLayout(cols=2, spacing=10, size_hint_y=None, height=200)
        
        form_layout.add_widget(Label(text='主机地址:', size_hint_x=0.3))
        self.host_input = TextInput(multiline=False, size_hint_x=0.7)
        form_layout.add_widget(self.host_input)
        
        form_layout.add_widget(Label(text='端口:', size_hint_x=0.3))
        self.port_input = TextInput(multiline=False, text='22', size_hint_x=0.7)
        form_layout.add_widget(self.port_input)
        
        form_layout.add_widget(Label(text='用户名:', size_hint_x=0.3))
        self.username_input = TextInput(multiline=False, size_hint_x=0.7)
        form_layout.add_widget(self.username_input)
        
        form_layout.add_widget(Label(text='密码:', size_hint_x=0.3))
        self.password_input = TextInput(multiline=False, password=True, size_hint_x=0.7)
        form_layout.add_widget(self.password_input)
        
        layout.add_widget(form_layout)
        
        # 连接按钮
        btn_layout = BoxLayout(size_hint_y=None, height=50, spacing=10)
        self.connect_btn = Button(text='连接', size_hint_x=0.5)
        self.connect_btn.bind(on_press=self.connect_ssh)
        btn_layout.add_widget(self.connect_btn)
        
        self.load_btn = Button(text='加载记录', size_hint_x=0.5)
        self.load_btn.bind(on_press=self.load_connections)
        btn_layout.add_widget(self.load_btn)
        
        layout.add_widget(btn_layout)
        
        # 连接记录列表
        record_label = Label(text='连接记录:', size_hint_y=None, height=30)
        layout.add_widget(record_label)
        
        scroll = ScrollView()
        self.records_list = GridLayout(cols=1, spacing=5, size_hint_y=None)
        self.records_list.bind(minimum_height=self.records_list.setter('height'))
        scroll.add_widget(self.records_list)
        layout.add_widget(scroll)
        
        self.add_widget(layout)
        self.load_connection_records()
    
    def set_app(self, app):
        """设置应用引用"""
        self.app = app
    
    def load_connection_records(self):
        """加载连接记录"""
        self.records_list.clear_widgets()
        try:
            app_dir = self.get_app_dir()
            connections_file = os.path.join(app_dir, 'connections.json')
            if os.path.exists(connections_file):
                with open(connections_file, 'r', encoding='utf-8') as f:
                    connections = json.load(f)
                    for conn in connections:
                        btn = Button(
                            text=f"{conn.get('name', '未命名')} - {conn.get('host', '')}",
                            size_hint_y=None,
                            height=40
                        )
                        btn.bind(on_press=lambda instance, c=conn: self.load_connection(c))
                        self.records_list.add_widget(btn)
        except Exception as e:
            print(f"加载连接记录失败: {e}")
    
    def load_connection(self, conn):
        """加载连接信息到输入框"""
        self.host_input.text = conn.get('host', '')
        self.port_input.text = str(conn.get('port', 22))
        self.username_input.text = conn.get('username', '')
        # 密码需要解密
        password = conn.get('password', '')
        try:
            password = decrypt_password(password)
        except:
            pass
        self.password_input.text = password
    
    def load_connections(self, instance):
        """加载连接记录"""
        self.load_connection_records()
    
    def connect_ssh(self, instance):
        """连接SSH"""
        if not HAS_PARAMIKO:
            self.show_error("错误", "缺少paramiko库，无法连接SSH")
            return
        
        host = self.host_input.text.strip()
        port = self.port_input.text.strip() or '22'
        username = self.username_input.text.strip()
        password = self.password_input.text
        
        if not host or not username:
            self.show_error("错误", "请填写主机地址和用户名")
            return
        
        try:
            port = int(port)
        except:
            port = 22
        
        # 切换到命令界面
        if self.app:
            self.app.connect_to_server(host, port, username, password)
            self.app.screen_manager.current = 'command'
    
    def show_error(self, title, message):
        """显示错误弹窗"""
        popup = Popup(
            title=title,
            content=Label(text=message),
            size_hint=(0.8, 0.4)
        )
        popup.open()
    
    def get_app_dir(self):
        """获取应用目录"""
        if platform == 'android':
            from android.storage import app_storage_path
            return app_storage_path()
        else:
            return os.path.dirname(os.path.abspath(__file__))


class CommandScreen(Screen):
    """命令执行界面"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app = None
        self.client = None
        self.is_connected = False
        
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # 连接信息显示
        self.connection_info = Label(
            text='未连接',
            size_hint_y=None,
            height=40,
            text_size=(None, None),
            halign='left'
        )
        layout.add_widget(self.connection_info)
        
        # 输出区域
        output_label = Label(text='输出:', size_hint_y=None, height=30)
        layout.add_widget(output_label)
        
        scroll = ScrollView()
        self.output_text = TextInput(
            multiline=True,
            readonly=True,
            background_color=(0.1, 0.1, 0.1, 1),
            foreground_color=(0, 1, 0, 1),
            font_name='Courier'
        )
        scroll.add_widget(self.output_text)
        layout.add_widget(scroll)
        
        # 命令输入
        cmd_label = Label(text='命令:', size_hint_y=None, height=30)
        layout.add_widget(cmd_label)
        
        cmd_layout = BoxLayout(size_hint_y=None, height=50, spacing=10)
        self.cmd_input = TextInput(multiline=False, size_hint_x=0.7)
        self.cmd_input.bind(on_text_validate=self.send_command)
        cmd_layout.add_widget(self.cmd_input)
        
        send_btn = Button(text='发送', size_hint_x=0.15)
        send_btn.bind(on_press=lambda x: self.send_command(self.cmd_input))
        cmd_layout.add_widget(send_btn)
        
        disconnect_btn = Button(text='断开', size_hint_x=0.15)
        disconnect_btn.bind(on_press=self.disconnect)
        cmd_layout.add_widget(disconnect_btn)
        
        layout.add_widget(cmd_layout)
        
        self.add_widget(layout)
        
        # 定时器更新输出
        Clock.schedule_interval(self.update_output, 0.1)
    
    def set_app(self, app):
        """设置应用引用"""
        self.app = app
    
    def connect(self, host, port, username, password):
        """建立SSH连接"""
        try:
            self.append_output(f"正在连接 {host}:{port}...")
            self.connection_info.text = f"连接中: {host}:{port}"
            
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(host, port=port, username=username, password=password, timeout=10)
            
            self.client = client
            self.is_connected = True
            self.connection_info.text = f"已连接: {host}:{port} ({username})"
            self.append_output(f"✓ 连接成功！\n")
            
            # 保存连接记录
            self.save_connection(host, port, username, password)
            
        except Exception as e:
            self.append_output(f"✗ 连接失败: {str(e)}\n")
            self.connection_info.text = "连接失败"
            self.is_connected = False
    
    def send_command(self, instance):
        """发送命令"""
        if not self.is_connected or not self.client:
            self.append_output("✗ 未连接，请先连接服务器\n")
            return
        
        command = self.cmd_input.text.strip()
        if not command:
            return
        
        self.append_output(f"$ {command}\n")
        self.cmd_input.text = ''
        
        # 在后台线程执行命令
        threading.Thread(target=self.execute_command, args=(command,), daemon=True).start()
    
    def execute_command(self, command):
        """执行命令"""
        try:
            stdin, stdout, stderr = self.client.exec_command(command, get_pty=True)
            stdout.channel.settimeout(10)
            
            # 读取输出
            output = stdout.read().decode('utf-8', errors='ignore')
            error = stderr.read().decode('utf-8', errors='ignore')
            
            if output:
                output_queue.put(('output', output))
            if error:
                output_queue.put(('error', error))
            
            exit_status = stdout.channel.recv_exit_status()
            if exit_status != 0:
                output_queue.put(('error', f'\n[退出码: {exit_status}]\n'))
        
        except Exception as e:
            output_queue.put(('error', f'执行命令失败: {str(e)}\n'))
    
    def disconnect(self, instance):
        """断开连接"""
        if self.client:
            try:
                self.client.close()
            except:
                pass
            self.client = None
            self.is_connected = False
            self.connection_info.text = "未连接"
            self.append_output("\n已断开连接\n")
        
        # 返回连接界面
        if self.app:
            self.app.screen_manager.current = 'connection'
    
    def append_output(self, text):
        """追加输出"""
        self.output_text.text += text
        # 滚动到底部
        self.output_text.cursor = (len(self.output_text.text), 0)
    
    def update_output(self, dt):
        """更新输出（从队列读取）"""
        try:
            while True:
                msg_type, content = output_queue.get_nowait()
                if msg_type == 'output':
                    self.append_output(content)
                elif msg_type == 'error':
                    self.append_output(f"[错误] {content}")
        except queue.Empty:
            pass
    
    def save_connection(self, host, port, username, password):
        """保存连接记录"""
        try:
            app_dir = self.get_app_dir()
            connections_file = os.path.join(app_dir, 'connections.json')
            
            # 读取现有记录
            connections = []
            if os.path.exists(connections_file):
                with open(connections_file, 'r', encoding='utf-8') as f:
                    connections = json.load(f)
            
            # 检查是否已存在
            encrypted_password = encrypt_password(password)
            
            # 添加新记录
            conn = {
                'name': f"{host}",
                'host': host,
                'port': port,
                'username': username,
                'password': encrypted_password
            }
            
            # 检查是否已存在相同连接
            exists = False
            for i, c in enumerate(connections):
                if c.get('host') == host and c.get('username') == username:
                    connections[i] = conn
                    exists = True
                    break
            
            if not exists:
                connections.append(conn)
            
            # 保存
            with open(connections_file, 'w', encoding='utf-8') as f:
                json.dump(connections, f, ensure_ascii=False, indent=2)
        
        except Exception as e:
            print(f"保存连接记录失败: {e}")
    
    def get_app_dir(self):
        """获取应用目录"""
        if platform == 'android':
            from android.storage import app_storage_path
            return app_storage_path()
        else:
            return os.path.dirname(os.path.abspath(__file__))


class SSHToolApp(App):
    """SSH工具应用主类"""
    
    def build(self):
        """构建应用界面"""
        self.screen_manager = ScreenManager()
        
        # 连接界面
        self.connection_screen = ConnectionScreen(name='connection')
        self.connection_screen.set_app(self)
        self.screen_manager.add_widget(self.connection_screen)
        
        # 命令界面
        self.command_screen = CommandScreen(name='command')
        self.command_screen.set_app(self)
        self.screen_manager.add_widget(self.command_screen)
        
        return self.screen_manager
    
    def connect_to_server(self, host, port, username, password):
        """连接到服务器"""
        self.command_screen.connect(host, port, username, password)


if __name__ == '__main__':
    SSHToolApp().run()

