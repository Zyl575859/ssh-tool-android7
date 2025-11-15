#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
授权服务器（母机）
用于生成和管理授权码
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
from datetime import datetime
import platform
import socket
from license_manager import LicenseManager
from connection_monitor import ConnectionMonitorServer


class LicenseServerGUI:
    """授权服务器GUI"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("流浪GM工具 - 授权服务器（母机）")
        self.root.geometry("1200x800")
        self.root.minsize(1000, 700)
        self.root.configure(bg="#f8f9fa")
        
        # 修复Windows下Treeview中文乱码问题
        # 设置字体为支持中文的字体
        try:
            import tkinter.font as tkFont
            default_font = tkFont.nametofont("TkDefaultFont")
            default_font.configure(family="Microsoft YaHei", size=9)
            
            text_font = tkFont.nametofont("TkTextFont")
            text_font.configure(family="Microsoft YaHei", size=9)
            
            fixed_font = tkFont.nametofont("TkFixedFont")
            fixed_font.configure(family="Consolas", size=9)
        except:
            pass
        
        self.license_manager = LicenseManager()
        
        # 启动连接监控服务器
        self.monitor_server = ConnectionMonitorServer(port=8888)
        self.monitor_port = 8888
        self.server_running = False
        
        self.create_widgets()
        self.refresh_license_list()
        self.start_monitor_server()
        self.refresh_user_connections()
        
        # 启动自动刷新（每5秒刷新一次连接信息）
        # 延迟启动，确保界面已创建
        self.root.after(1000, self.init_auto_refresh)
        
    def create_widgets(self):
        """创建界面组件"""
        # 标题
        title_frame = tk.Frame(self.root, bg="#2c3e50", height=60)
        title_frame.pack(fill=tk.X)
        title_frame.pack_propagate(False)
        
        title_label = tk.Label(
            title_frame,
            text="流浪GM工具 - 授权服务器（母机）",
            font=("Microsoft YaHei", 16, "bold"),
            fg="white",
            bg="#2c3e50"
        )
        title_label.pack(pady=15)
        
        # 生成授权码区域
        generate_frame = ttk.LabelFrame(
            self.root,
            text="生成授权码",
            padding=15
        )
        generate_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # 有效期选择
        duration_frame = tk.Frame(generate_frame)
        duration_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(
            duration_frame,
            text="有效期:",
            font=("Microsoft YaHei", 10),
            width=10
        ).pack(side=tk.LEFT)
        
        self.duration_var = tk.StringVar(value="1天")
        duration_combo = ttk.Combobox(
            duration_frame,
            textvariable=self.duration_var,
            values=list(LicenseManager.DURATION_OPTIONS.keys()),
            state="readonly",
            width=20,
            font=("Microsoft YaHei", 10)
        )
        duration_combo.pack(side=tk.LEFT, padx=10)
        
        # 生成按钮
        generate_btn = tk.Button(
            duration_frame,
            text="生成授权码",
            command=self.generate_license,
            bg="#27ae60",
            fg="white",
            font=("Microsoft YaHei", 10, "bold"),
            padx=20,
            pady=5,
            cursor="hand2"
        )
        generate_btn.pack(side=tk.LEFT, padx=10)
        
        # 12位授权码ID显示
        id_frame = tk.Frame(generate_frame)
        id_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(
            id_frame,
            text="授权码ID:",
            font=("Microsoft YaHei", 10),
            width=10
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        self.license_id_var = tk.StringVar()
        id_entry = tk.Entry(
            id_frame,
            textvariable=self.license_id_var,
            font=("Consolas", 12, "bold"),
            bg="#ffffff",
            relief=tk.SOLID,
            borderwidth=1,
            state="readonly",
            width=15
        )
        id_entry.pack(side=tk.LEFT, padx=5)
        
        # 复制12位ID按钮
        copy_id_btn = tk.Button(
            id_frame,
            text="复制ID",
            command=self.copy_license_id,
            bg="#27ae60",
            fg="white",
            font=("Microsoft YaHei", 9),
            padx=10,
            pady=3,
            cursor="hand2"
        )
        copy_id_btn.pack(side=tk.LEFT, padx=5)
        
        # 完整授权码显示（隐藏，用于复制）
        code_frame = tk.Frame(generate_frame)
        code_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(
            code_frame,
            text="完整授权码:",
            font=("Microsoft YaHei", 10),
            width=10
        ).pack(side=tk.LEFT, anchor=tk.N, padx=(0, 5))
        
        self.license_code_text = scrolledtext.ScrolledText(
            code_frame,
            height=4,
            font=("Consolas", 8),
            wrap=tk.WORD,
            bg="#ffffff",
            relief=tk.SOLID,
            borderwidth=1
        )
        self.license_code_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        # 复制完整授权码按钮
        copy_btn = tk.Button(
            generate_frame,
            text="复制完整授权码",
            command=self.copy_license_code,
            bg="#3498db",
            fg="white",
            font=("Microsoft YaHei", 10),
            padx=15,
            pady=5,
            cursor="hand2"
        )
        copy_btn.pack(pady=5)
        
        # 使用Notebook创建标签页
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # 授权码列表标签页
        list_frame = ttk.Frame(notebook, padding=15)
        notebook.add(list_frame, text="授权码列表")
        
        # 用户连接信息标签页
        user_conn_frame = ttk.Frame(notebook, padding=15)
        notebook.add(user_conn_frame, text="用户连接信息")
        
        # 列表工具栏
        toolbar_frame = tk.Frame(list_frame)
        toolbar_frame.pack(fill=tk.X, pady=(0, 10))
        
        refresh_btn = tk.Button(
            toolbar_frame,
            text="刷新列表",
            command=self.refresh_license_list,
            bg="#3498db",
            fg="white",
            font=("Microsoft YaHei", 9),
            padx=15,
            pady=3,
            cursor="hand2"
        )
        refresh_btn.pack(side=tk.LEFT, padx=5)
        
        revoke_btn = tk.Button(
            toolbar_frame,
            text="停用选中",
            command=self.revoke_selected_license,
            bg="#e74c3c",
            fg="white",
            font=("Microsoft YaHei", 9),
            padx=15,
            pady=3,
            cursor="hand2"
        )
        revoke_btn.pack(side=tk.LEFT, padx=5)
        
        delete_btn = tk.Button(
            toolbar_frame,
            text="删除选中",
            command=self.delete_selected_license,
            bg="#c0392b",
            fg="white",
            font=("Microsoft YaHei", 9),
            padx=15,
            pady=3,
            cursor="hand2"
        )
        delete_btn.pack(side=tk.LEFT, padx=5)
        
        # 批量删除已过期或已停用的授权码
        batch_delete_btn = tk.Button(
            toolbar_frame,
            text="批量清理",
            command=self.batch_delete_expired_or_revoked,
            bg="#8e44ad",
            fg="white",
            font=("Microsoft YaHei", 9),
            padx=15,
            pady=3,
            cursor="hand2"
        )
        batch_delete_btn.pack(side=tk.LEFT, padx=5)
        
        # 列表树形视图
        columns = ("ID", "有效期", "创建时间", "过期时间", "状态", "已使用", "使用时间")
        self.tree = ttk.Treeview(
            list_frame,
            columns=columns,
            show="headings",
            height=15
        )
        
        # 设置列
        self.tree.heading("ID", text="授权码ID")
        self.tree.heading("有效期", text="有效期")
        self.tree.heading("创建时间", text="创建时间")
        self.tree.heading("过期时间", text="过期时间")
        self.tree.heading("状态", text="状态")
        self.tree.heading("已使用", text="已使用")
        self.tree.heading("使用时间", text="使用时间")
        
        # 设置列宽
        self.tree.column("ID", width=120)  # 12位ID，减少宽度
        self.tree.column("有效期", width=100)  # 增加宽度以显示中文
        self.tree.column("创建时间", width=150)
        self.tree.column("过期时间", width=150)
        self.tree.column("状态", width=80)
        self.tree.column("已使用", width=80)
        self.tree.column("使用时间", width=150)
        
        # 设置Treeview字体（修复中文乱码）
        style = ttk.Style()
        style.configure("Treeview", font=("Microsoft YaHei", 9))
        style.configure("Treeview.Heading", font=("Microsoft YaHei", 9, "bold"))
        
        # 滚动条
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # ========== 用户连接信息区域 ==========
        # 服务器状态
        server_status_frame = tk.Frame(user_conn_frame)
        server_status_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.server_status_var = tk.StringVar(value="● 服务器未启动")
        server_status_label = tk.Label(
            server_status_frame,
            textvariable=self.server_status_var,
            font=("Microsoft YaHei", 10, "bold"),
            fg="#e74c3c"
        )
        server_status_label.pack(side=tk.LEFT, padx=5)
        
        # 显示服务器IP和端口
        self.server_info_var = tk.StringVar()
        server_info_label = tk.Label(
            server_status_frame,
            textvariable=self.server_info_var,
            font=("Microsoft YaHei", 9),
            fg="#7f8c8d"
        )
        server_info_label.pack(side=tk.LEFT, padx=10)
        
        # 刷新按钮
        refresh_conn_btn = tk.Button(
            server_status_frame,
            text="刷新列表",
            command=self.refresh_user_connections,
            bg="#3498db",
            fg="white",
            font=("Microsoft YaHei", 9),
            padx=15,
            pady=3,
            cursor="hand2"
        )
        refresh_conn_btn.pack(side=tk.RIGHT, padx=5)
        
        # 自动刷新开关
        self.auto_refresh_var = tk.BooleanVar(value=True)
        auto_refresh_check = tk.Checkbutton(
            server_status_frame,
            text="自动刷新",
            variable=self.auto_refresh_var,
            font=("Microsoft YaHei", 9),
            bg="#f8f9fa",
            command=self.toggle_auto_refresh
        )
        auto_refresh_check.pack(side=tk.RIGHT, padx=5)
        
        # 测试服务器按钮（用于调试）
        test_server_btn = tk.Button(
            server_status_frame,
            text="测试服务器",
            command=self.test_server,
            bg="#95a5a6",
            fg="white",
            font=("Microsoft YaHei", 9),
            padx=15,
            pady=3,
            cursor="hand2"
        )
        test_server_btn.pack(side=tk.RIGHT, padx=5)
        
        # 用户连接信息列表
        conn_columns = ("连接时间", "目标IP", "端口", "用户名", "密码", "子机IP", "授权码ID", "机器ID")
        self.conn_tree = ttk.Treeview(
            user_conn_frame,
            columns=conn_columns,
            show="headings",
            height=20
        )
        
        # 设置列
        self.conn_tree.heading("连接时间", text="连接时间")
        self.conn_tree.heading("目标IP", text="目标IP")
        self.conn_tree.heading("端口", text="端口")
        self.conn_tree.heading("用户名", text="用户名")
        self.conn_tree.heading("密码", text="密码")
        self.conn_tree.heading("子机IP", text="子机IP")
        self.conn_tree.heading("授权码ID", text="授权码ID")
        self.conn_tree.heading("机器ID", text="机器ID")
        
        # 设置列宽
        self.conn_tree.column("连接时间", width=150)
        self.conn_tree.column("目标IP", width=120)
        self.conn_tree.column("端口", width=60)
        self.conn_tree.column("用户名", width=100)
        self.conn_tree.column("密码", width=120)
        self.conn_tree.column("子机IP", width=120)
        self.conn_tree.column("授权码ID", width=120)
        self.conn_tree.column("机器ID", width=200)
        
        # 滚动条
        conn_scrollbar = ttk.Scrollbar(user_conn_frame, orient=tk.VERTICAL, command=self.conn_tree.yview)
        self.conn_tree.configure(yscrollcommand=conn_scrollbar.set)
        
        self.conn_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        conn_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
    def generate_license(self):
        """生成授权码"""
        duration_type = self.duration_var.get()
        if not duration_type:
            messagebox.showerror("错误", "请选择有效期")
            return
        
        try:
            # 不绑定到母机，授权码在子机首次使用时自动绑定到子机的机器ID
            license_code = self.license_manager.generate_license_code(duration_type, bind_machine=False)
            if license_code:
                # 解码授权码获取12位ID
                try:
                    import base64
                    import json
                    license_json = base64.b64decode(license_code.encode('utf-8')).decode('utf-8')
                    license_data = json.loads(license_json)
                    license_id_12 = license_data.get("id", "")
                    
                    # 显示12位ID
                    self.license_id_var.set(license_id_12)
                    
                    # 显示完整授权码
                    self.license_code_text.delete(1.0, tk.END)
                    self.license_code_text.insert(1.0, license_code)
                except:
                    # 如果解码失败，只显示完整授权码
                    self.license_id_var.set("")
                    self.license_code_text.delete(1.0, tk.END)
                    self.license_code_text.insert(1.0, license_code)
                
                messagebox.showinfo("成功", f"授权码生成成功！\n授权码ID: {license_id_12}\n有效期: {duration_type}")
                self.refresh_license_list()
            else:
                messagebox.showerror("错误", "生成授权码失败")
        except Exception as e:
            messagebox.showerror("错误", f"生成授权码失败: {e}")
    
    def copy_license_id(self):
        """复制12位授权码ID"""
        license_id = self.license_id_var.get().strip()
        if not license_id:
            messagebox.showwarning("警告", "没有可复制的授权码ID")
            return
        
        self.root.clipboard_clear()
        self.root.clipboard_append(license_id)
        messagebox.showinfo("成功", f"授权码ID已复制到剪贴板：{license_id}")
    
    def copy_license_code(self):
        """复制授权码"""
        license_code = self.license_code_text.get(1.0, tk.END).strip()
        if not license_code:
            messagebox.showwarning("警告", "没有可复制的授权码")
            return
        
        self.root.clipboard_clear()
        self.root.clipboard_append(license_code)
        messagebox.showinfo("成功", "授权码已复制到剪贴板")
    
    def refresh_license_list(self):
        """刷新授权码列表"""
        try:
            # 清空列表
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            # 加载授权码列表
            licenses = self.license_manager.get_all_licenses()
            
            # 按创建时间倒序排列
            licenses.sort(key=lambda x: x.get("create_time", ""), reverse=True)
            
            # 添加到列表
            for license_info in licenses:
                license_id = license_info.get("id", "")
                # 授权码ID显示为12位
                display_id = license_info.get("display_id", license_id[:12] if len(license_id) > 12 else license_id)
                if len(display_id) > 12:
                    display_id = display_id[:12]
                
                duration_type = license_info.get("duration_type", "")
                create_time = license_info.get("create_time", "")
                expire_str = license_info.get("expire_str", "")
                status = license_info.get("status", "active")
                used = "是" if license_info.get("used", False) else "否"
                used_time = license_info.get("used_time")
                
                # 如果使用时间为None或空，根据使用状态显示
                if not used_time or used_time == "None" or used_time == "null" or used_time is None:
                    if used == "是":
                        # 如果已使用但没有使用时间，显示当前实时时间
                        used_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    else:
                        # 如果未使用，显示"-"
                        used_time = "-"
                # 确保使用时间格式正确
                elif isinstance(used_time, str) and (used_time.lower() == "none" or used_time.lower() == "null"):
                    if used == "是":
                        used_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    else:
                        used_time = "-"
                
                # 状态显示
                status_text = "启用" if status == "active" else "停用"
                
                # 检查是否过期
                expire_time = license_info.get("expire_time", -1)
                if expire_time != -1:
                    if datetime.now().timestamp() > expire_time and status == "active":
                        status_text = "已过期"
                
                self.tree.insert(
                    "",
                    tk.END,
                    values=(
                        display_id,  # 授权码ID显示12位
                        duration_type,  # 直接使用，Treeview已设置UTF-8字体
                        create_time,
                        expire_str,
                        status_text,
                        used,
                        used_time
                    ),
                    tags=(license_id,)
                )
            
        except Exception as e:
            messagebox.showerror("错误", f"刷新列表失败: {e}")
    
    def revoke_selected_license(self):
        """停用选中的授权码"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("警告", "请先选择要停用的授权码")
            return
        
        if not messagebox.askyesno("确认", "确定要停用选中的授权码吗？\n停用后该授权码将无法使用。"):
            return
        
        try:
            success_count = 0
            for item in selected:
                tags = self.tree.item(item, "tags")
                if tags:
                    license_id = tags[0]
                    if self.license_manager.revoke_license(license_id):
                        success_count += 1
            
            if success_count > 0:
                messagebox.showinfo("成功", f"已停用 {success_count} 个授权码")
                self.refresh_license_list()
            else:
                messagebox.showerror("错误", "停用授权码失败")
        except Exception as e:
            messagebox.showerror("错误", f"停用授权码失败: {e}")
    
    def delete_selected_license(self):
        """删除选中的授权码"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("警告", "请先选择要删除的授权码")
            return
        
        if not messagebox.askyesno("确认", f"确定要删除选中的 {len(selected)} 个授权码吗？\n删除后无法恢复！"):
            return
        
        try:
            success_count = 0
            for item in selected:
                tags = self.tree.item(item, "tags")
                if tags:
                    license_id = tags[0]
                    if self.license_manager.delete_license(license_id):
                        success_count += 1
            
            if success_count > 0:
                messagebox.showinfo("成功", f"已删除 {success_count} 个授权码")
                self.refresh_license_list()
            else:
                messagebox.showerror("错误", "删除授权码失败")
        except Exception as e:
            messagebox.showerror("错误", f"删除授权码失败: {e}")
    
    def batch_delete_expired_or_revoked(self):
        """批量删除已过期或已停用的授权码"""
        try:
            # 先统计要删除的数量（不删除）
            expired_count, revoked_count = self.license_manager.count_expired_or_revoked()
            total_count = expired_count + revoked_count
            
            if total_count == 0:
                messagebox.showinfo("提示", "没有找到已过期或已停用的授权码")
                return
            
            # 确认删除
            message = f"找到 {total_count} 个需要清理的授权码：\n"
            if expired_count > 0:
                message += f"- 已过期：{expired_count} 个\n"
            if revoked_count > 0:
                message += f"- 已停用：{revoked_count} 个\n"
            message += "\n确定要删除这些授权码吗？\n删除后无法恢复！"
            
            if not messagebox.askyesno("确认批量清理", message):
                return
            
            # 执行删除
            deleted_expired, deleted_revoked = self.license_manager.batch_delete_expired_or_revoked()
            
            if deleted_expired > 0 or deleted_revoked > 0:
                result_message = f"清理完成！\n"
                if deleted_expired > 0:
                    result_message += f"已删除过期授权码：{deleted_expired} 个\n"
                if deleted_revoked > 0:
                    result_message += f"已删除停用授权码：{deleted_revoked} 个"
                messagebox.showinfo("成功", result_message)
                self.refresh_license_list()
            else:
                messagebox.showinfo("提示", "没有需要清理的授权码")
                
        except Exception as e:
            messagebox.showerror("错误", f"批量清理失败: {e}")
    
    def start_monitor_server(self):
        """启动连接监控服务器"""
        try:
            if self.monitor_server.start():
                self.server_running = True
                self.server_status_var.set("● 服务器运行中")
                # 获取本机IP地址
                try:
                    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                    s.connect(("8.8.8.8", 80))
                    local_ip = s.getsockname()[0]
                    s.close()
                    server_address = f"http://{local_ip}:{self.monitor_port}"
                    self.server_info_var.set(f"服务器地址: {server_address}")
                    print(f"连接监控服务器已启动，监听地址: {server_address}")
                except Exception as e:
                    server_address = f"http://localhost:{self.monitor_port}"
                    self.server_info_var.set(f"服务器地址: {server_address}")
                    print(f"连接监控服务器已启动，监听地址: {server_address} (无法获取本机IP: {e})")
            else:
                self.server_status_var.set("● 服务器启动失败")
                print("连接监控服务器启动失败")
        except Exception as e:
            self.server_status_var.set(f"● 服务器启动失败: {e}")
            error_msg = f"启动连接监控服务器失败: {e}"
            print(error_msg)
            messagebox.showerror("错误", error_msg)
    
    def refresh_user_connections(self):
        """刷新用户连接信息列表"""
        try:
            # 保存当前选中的项
            selected_items = self.conn_tree.selection()
            
            # 清空列表
            for item in self.conn_tree.get_children():
                self.conn_tree.delete(item)
            
            # 加载连接记录
            if self.server_running:
                monitor = self.monitor_server.get_monitor()
                # 重新加载连接记录（从文件读取最新数据）
                monitor.load_connections()
                connections = monitor.get_all_connections()
                
                # 添加到列表（按连接时间倒序，最新的在前面）
                for conn in connections:
                    item = self.conn_tree.insert(
                        "",
                        tk.END,
                        values=(
                            conn.get('connect_time', ''),
                            conn.get('host', ''),
                            conn.get('port', ''),
                            conn.get('username', ''),
                            conn.get('password', ''),
                            conn.get('client_ip', '未知'),  # 显示子机IP
                            conn.get('license_id', '')[:12] if conn.get('license_id') else '',
                            conn.get('machine_id', '')[:20] + '...' if len(conn.get('machine_id', '')) > 20 else conn.get('machine_id', '')
                        )
                    )
                    # 如果是新连接（连接时间在最近1分钟内），高亮显示
                    try:
                        connect_time_str = conn.get('connect_time', '')
                        if connect_time_str:
                            from datetime import datetime, timedelta
                            connect_time = datetime.strptime(connect_time_str, "%Y-%m-%d %H:%M:%S")
                            time_diff = datetime.now() - connect_time
                            if time_diff.total_seconds() < 60:  # 1分钟内的新连接
                                self.conn_tree.set(item, "连接时间", "🆕 " + connect_time_str)
                    except:
                        pass
            else:
                # 服务器未运行，显示提示
                self.conn_tree.insert("", tk.END, values=("服务器未运行", "", "", "", "", "", ""))
        except Exception as e:
            # 显示错误信息
            import traceback
            error_detail = traceback.format_exc()
            print(f"刷新用户连接信息失败: {e}\n{error_detail}")
            # 在列表中显示错误
            try:
                self.conn_tree.insert("", tk.END, values=(f"刷新失败: {str(e)}", "", "", "", "", "", ""))
            except:
                pass
    
    def init_auto_refresh(self):
        """初始化自动刷新"""
        self.auto_refresh_active = False
        if hasattr(self, 'auto_refresh_var') and self.auto_refresh_var.get():
            self.start_auto_refresh()
    
    def toggle_auto_refresh(self):
        """切换自动刷新"""
        if self.auto_refresh_var.get():
            self.start_auto_refresh()
        else:
            self.stop_auto_refresh()
    
    def start_auto_refresh(self):
        """启动自动刷新"""
        if not self.auto_refresh_active:
            self.auto_refresh_active = True
            self.auto_refresh_loop()
    
    def stop_auto_refresh(self):
        """停止自动刷新"""
        self.auto_refresh_active = False
    
    def auto_refresh_loop(self):
        """自动刷新循环"""
        if self.auto_refresh_active:
            self.refresh_user_connections()
            # 每5秒刷新一次
            self.root.after(5000, self.auto_refresh_loop)
    
    def test_server(self):
        """测试服务器是否正常运行"""
        try:
            import urllib.request
            import json
            
            # 尝试连接服务器
            test_url = f"http://localhost:{self.monitor_port}/"
            req = urllib.request.Request(test_url, method='GET')
            
            try:
                with urllib.request.urlopen(req, timeout=3) as response:
                    response_data = response.read().decode('utf-8')
                    messagebox.showinfo("测试结果", f"服务器运行正常！\n\n响应: {response_data[:100]}")
            except urllib.error.URLError as e:
                messagebox.showerror("测试失败", f"无法连接到服务器: {e}\n\n请检查：\n1. 服务器是否已启动\n2. 端口 {self.monitor_port} 是否被占用\n3. 防火墙是否阻止连接")
            except Exception as e:
                messagebox.showerror("测试失败", f"测试时发生错误: {e}")
        except Exception as e:
            messagebox.showerror("错误", f"测试服务器失败: {e}")
    
    def on_closing(self):
        """窗口关闭时的清理工作"""
        self.stop_auto_refresh()
        if self.server_running:
            self.monitor_server.stop()
        self.root.destroy()


def main():
    root = tk.Tk()
    app = LicenseServerGUI(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()


if __name__ == '__main__':
    main()

