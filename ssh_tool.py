#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SSH连接工具
支持交互式命令输入和复制粘贴功能
"""

import paramiko
import sys
import os
import json
import threading
import time
from pathlib import Path

# Windows兼容性处理
try:
    import select
    HAS_SELECT = True
except ImportError:
    HAS_SELECT = False

try:
    import termios
    import tty
    HAS_TERMIOS = True
except ImportError:
    HAS_TERMIOS = False


class SSHTool:
    def __init__(self, host, port=22, username=None, password=None, key_file=None):
        """
        初始化SSH连接
        
        Args:
            host: 主机地址
            port: 端口号，默认22
            username: 用户名
            password: 密码
            key_file: SSH密钥文件路径
        """
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.key_file = key_file
        self.client = None
        self.shell = None
        
    def connect(self):
        """建立SSH连接"""
        try:
            self.client = paramiko.SSHClient()
            self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            # 如果提供了密钥文件，使用密钥认证
            if self.key_file and os.path.exists(self.key_file):
                self.client.connect(
                    hostname=self.host,
                    port=self.port,
                    username=self.username,
                    key_filename=self.key_file,
                    timeout=10
                )
            else:
                # 使用密码认证
                self.client.connect(
                    hostname=self.host,
                    port=self.port,
                    username=self.username,
                    password=self.password,
                    timeout=10
                )
            
            # 创建交互式shell
            self.shell = self.client.invoke_shell()
            self.shell.settimeout(0.1)
            
            print(f"✓ 成功连接到 {self.host}:{self.port}")
            print("=" * 60)
            return True
            
        except paramiko.AuthenticationException:
            print("✗ 认证失败，请检查用户名和密码")
            return False
        except paramiko.SSHException as e:
            print(f"✗ SSH连接错误: {e}")
            return False
        except Exception as e:
            print(f"✗ 连接失败: {e}")
            return False
    
    def interactive_shell(self):
        """交互式shell，支持直接输入命令和复制粘贴"""
        if not self.shell:
            print("✗ 未建立SSH连接")
            return
        
        print("\n进入交互模式（输入 'exit' 或按 Ctrl+C 退出）")
        print("提示：可以直接粘贴命令，支持多行输入\n")
        
        # 使用线程处理输出，提高响应性
        self._running = True
        
        # 输出线程：接收远程数据并显示
        def output_thread():
            while self._running:
                try:
                    if self.shell.recv_ready():
                        data = self.shell.recv(4096)
                        if data:
                            sys.stdout.write(data.decode('utf-8', errors='ignore'))
                            sys.stdout.flush()
                    else:
                        time.sleep(0.05)
                except:
                    if self._running:
                        break
        
        # 启动输出线程
        output_t = threading.Thread(target=output_thread, daemon=True)
        output_t.start()
        
        try:
            # 主循环：处理用户输入
            while self._running:
                # 检查连接状态
                if self.shell.closed:
                    print("\n连接已关闭")
                    break
                
                # 读取用户输入（支持复制粘贴）
                try:
                    # 使用input()，Windows和Linux都支持，且支持粘贴
                    line = input()
                    if not line:
                        continue
                    
                    # 检查退出命令
                    if line.strip().lower() == 'exit':
                        self._running = False
                        break
                    
                    # 发送命令到远程服务器
                    self.shell.send(line + '\n')
                    
                except EOFError:
                    # Ctrl+D 或 Ctrl+Z
                    self._running = False
                    break
                except KeyboardInterrupt:
                    # Ctrl+C
                    print("\n\n中断连接")
                    self._running = False
                    break
                except Exception as e:
                    if self._running:
                        print(f"\n输入错误: {e}")
                    
        except KeyboardInterrupt:
            print("\n\n中断连接")
        except Exception as e:
            print(f"\n错误: {e}")
        finally:
            self._running = False
            time.sleep(0.2)  # 等待输出线程结束
            self.close()
    
    def execute_command(self, command):
        """执行单个命令并返回结果"""
        if not self.client:
            print("✗ 未建立SSH连接")
            return None
        
        try:
            stdin, stdout, stderr = self.client.exec_command(command)
            output = stdout.read().decode('utf-8')
            error = stderr.read().decode('utf-8')
            return output, error
        except Exception as e:
            print(f"✗ 执行命令失败: {e}")
            return None, str(e)
    
    def close(self):
        """关闭SSH连接"""
        if self.shell:
            self.shell.close()
        if self.client:
            self.client.close()
        print("\n连接已关闭")


def load_config(config_file='config.json'):
    """加载配置文件"""
    if os.path.exists(config_file):
        with open(config_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None


def load_gm_templates(template_file='gm_templates.json'):
    """加载GM命令模板"""
    if os.path.exists(template_file):
        with open(template_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}


def print_gm_templates(templates):
    """打印GM命令模板"""
    if not templates:
        print("未找到GM命令模板")
        return
    
    print("\n" + "=" * 60)
    print("GM命令模板:")
    print("=" * 60)
    for category, commands in templates.items():
        print(f"\n【{category}】")
        for cmd_name, cmd_info in commands.items():
            print(f"  {cmd_name}: {cmd_info.get('description', '')}")
            print(f"    命令: {cmd_info.get('command', '')}")
            if cmd_info.get('params'):
                print(f"    参数: {cmd_info.get('params', '')}")
            print()


def main():
    """主函数"""
    import argparse
    
    # 检查依赖
    try:
        import paramiko
    except ImportError:
        print("✗ 错误: 缺少 paramiko 库")
        print("请运行: pip install paramiko")
        print("\n或者安装所有依赖: pip install -r requirements.txt")
        input("\n按回车键退出...")
        sys.exit(1)
    
    parser = argparse.ArgumentParser(
        description='SSH连接工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
示例:
  # 查看GM命令模板
  python ssh_tool.py -t
  
  # 连接服务器
  python ssh_tool.py -H 192.168.1.100 -u root -p password
  
  # 使用配置文件
  python ssh_tool.py -c config.json
  
  # 执行单个命令
  python ssh_tool.py -H 192.168.1.100 -u root -p password -e "ls -la"
        '''
    )
    parser.add_argument('-H', '--host', help='主机地址')
    parser.add_argument('-P', '--port', type=int, default=22, help='端口号（默认22）')
    parser.add_argument('-u', '--username', help='用户名')
    parser.add_argument('-p', '--password', help='密码')
    parser.add_argument('-k', '--key', help='SSH密钥文件路径')
    parser.add_argument('-c', '--config', help='配置文件路径', default='config.json')
    parser.add_argument('-t', '--template', action='store_true', help='显示GM命令模板')
    parser.add_argument('-e', '--execute', help='执行单个命令后退出')
    
    args = parser.parse_args()
    
    # 显示GM模板
    if args.template:
        templates = load_gm_templates()
        print_gm_templates(templates)
        input("\n按回车键退出...")
        return
    
    # 尝试从配置文件加载
    config = load_config(args.config)
    if config:
        host = args.host or config.get('host')
        port = args.port or config.get('port', 22)
        username = args.username or config.get('username')
        password = args.password or config.get('password')
        key_file = args.key or config.get('key_file')
    else:
        host = args.host
        port = args.port
        username = args.username
        password = args.password
        key_file = args.key
    
    # 检查必需参数
    if not username:
        print("✗ 错误: 缺少用户名")
        print("使用方法: python ssh_tool.py -H <主机地址> -u <用户名> [-p <密码>]")
        input("\n按回车键退出...")
        sys.exit(1)
    
    # 如果没有密码且没有密钥文件，提示输入
    if not password and not key_file:
        try:
            import getpass
            password = getpass.getpass(f"请输入 {username}@{host} 的密码: ")
        except:
            password = input(f"请输入 {username}@{host} 的密码: ")
    
    # 创建SSH工具实例
    ssh = SSHTool(host, port, username, password, key_file)
    
    # 连接
    try:
        if not ssh.connect():
            input("\n按回车键退出...")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n用户取消连接")
        sys.exit(0)
    except Exception as e:
        print(f"\n✗ 连接时发生错误: {e}")
        import traceback
        traceback.print_exc()
        input("\n按回车键退出...")
        sys.exit(1)
    
    # 如果指定了执行命令，执行后退出
    if args.execute:
        try:
            output, error = ssh.execute_command(args.execute)
            if output:
                print(output)
            if error:
                print(f"错误: {error}", file=sys.stderr)
        except Exception as e:
            print(f"✗ 执行命令时发生错误: {e}")
        finally:
            ssh.close()
        return
    
    # 进入交互模式
    try:
        ssh.interactive_shell()
    except KeyboardInterrupt:
        print("\n\n用户中断")
    except Exception as e:
        print(f"\n✗ 发生错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        try:
            ssh.close()
        except:
            pass


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n程序被用户中断")
        sys.exit(0)
    except Exception as e:
        print(f"\n✗ 程序发生未预期的错误: {e}")
        import traceback
        traceback.print_exc()
        input("\n按回车键退出...")
        sys.exit(1)

