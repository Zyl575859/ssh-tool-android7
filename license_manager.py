#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
授权管理系统
支持生成授权码、验证授权码、管理授权码（启用/停用）
"""

import json
import os
import sys
import hashlib
import base64
from datetime import datetime, timedelta
from typing import Dict, Optional, List, Tuple
import uuid
import platform
import subprocess
import socket

# Windows特定导入
if platform.system() == 'Windows':
    try:
        import winreg
    except ImportError:
        winreg = None


# 授权码加密密钥
_LICENSE_KEY = "liulang_gm_tool_license_key_2024_v1.0.1"


def get_app_dir():
    """获取应用程序目录（兼容打包后的exe和开发环境）"""
    if getattr(sys, 'frozen', False):
        return os.path.dirname(os.path.abspath(sys.executable))
    else:
        return os.path.dirname(os.path.abspath(__file__))


# 缓存机器ID，避免重复计算（提高性能，减少阻塞）
_MACHINE_ID_CACHE = None

def get_machine_id() -> str:
    """
    获取机器唯一标识（用于绑定授权码）
    使用MAC地址、主机名、Windows机器GUID等组合生成
    不使用WMIC（Windows 11已弃用），改用更可靠的方法
    使用缓存机制，避免重复计算
    """
    global _MACHINE_ID_CACHE
    
    # 如果已经缓存，直接返回
    if _MACHINE_ID_CACHE is not None:
        return _MACHINE_ID_CACHE
    
    try:
        machine_info = []
        
        # Windows系统
        if platform.system() == 'Windows':
            try:
                # 方法1: 获取MAC地址（第一个可用网卡）- 最可靠
                mac = uuid.getnode()
                # uuid.getnode() 返回48位整数，如果无法获取真实MAC会返回随机值
                # 检查是否为有效MAC地址（不是随机生成的）
                if mac and mac != 0:
                    # 检查MAC地址是否看起来是真实的（不是全0或全F）
                    mac_hex = format(mac, '012x')
                    if mac_hex != '000000000000' and not all(c == 'f' for c in mac_hex.lower()):
                        machine_info.append(str(mac))
            except:
                pass
            
            try:
                # 获取主机名（作为辅助标识）
                hostname = socket.gethostname()
                if hostname:
                    machine_info.append(hostname)
            except:
                pass
            
            # 优先尝试从注册表获取机器GUID（更快，不依赖PowerShell）
            if winreg:
                try:
                    key = winreg.OpenKey(
                        winreg.HKEY_LOCAL_MACHINE,
                        r"SOFTWARE\Microsoft\Cryptography"
                    )
                    machine_guid = winreg.QueryValueEx(key, "MachineGuid")[0]
                    winreg.CloseKey(key)
                    if machine_guid and len(machine_guid) > 10:
                        machine_info.append(machine_guid)
                except:
                    # 如果注册表方法失败，尝试PowerShell（但设置更短的超时）
                    try:
                        ps_command = 'Get-ItemPropertyValue -Path "HKLM:\\SOFTWARE\\Microsoft\\Cryptography" -Name "MachineGuid" -ErrorAction SilentlyContinue'
                        result = subprocess.run(
                            ['powershell', '-Command', ps_command],
                            capture_output=True,
                            text=True,
                            timeout=1,  # 进一步减少超时时间到1秒
                            shell=True,
                            creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
                        )
                        if result.returncode == 0 and result.stdout:
                            machine_guid = result.stdout.strip()
                            if machine_guid and len(machine_guid) > 10:
                                machine_info.append(machine_guid)
                    except:
                        # PowerShell失败，静默忽略
                        pass
            
            try:
                # 获取用户名（作为辅助标识）
                username = os.getenv('USERNAME') or os.getenv('USER')
                if username:
                    machine_info.append(username)
            except:
                pass
            
            # 如果以上方法都失败，使用注册表中的其他信息
            if not machine_info and winreg:
                try:
                    # 尝试从注册表获取计算机名
                    key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 
                                        r"SYSTEM\CurrentControlSet\Control\ComputerName\ComputerName")
                    computer_name = winreg.QueryValueEx(key, "ComputerName")[0]
                    winreg.CloseKey(key)
                    if computer_name:
                        machine_info.append(computer_name)
                except:
                    pass
        
        # Linux/Mac系统
        else:
            try:
                # 获取机器ID
                if os.path.exists('/etc/machine-id'):
                    with open('/etc/machine-id', 'r') as f:
                        machine_info.append(f.read().strip())
            except:
                pass
            
            try:
                # 获取主机名
                hostname = platform.node()
                if hostname:
                    machine_info.append(hostname)
            except:
                pass
        
        # 如果无法获取硬件信息，使用主机名+用户名作为备用
        if not machine_info:
            machine_info.append(platform.node())
            machine_info.append(os.getenv('USERNAME', os.getenv('USER', 'unknown')))
        
        # 组合信息并生成哈希
        machine_string = '|'.join(machine_info)
        machine_id = hashlib.md5(machine_string.encode('utf-8')).hexdigest()
        
        # 缓存结果
        _MACHINE_ID_CACHE = machine_id
        
        return machine_id

    except Exception as e:
        # 如果所有方法都失败，使用主机名生成一个备用ID
        fallback = platform.node() + str(os.getpid())
        machine_id = hashlib.md5(fallback.encode('utf-8')).hexdigest()
        # 缓存结果
        _MACHINE_ID_CACHE = machine_id
        return machine_id


class LicenseManager:
    """授权管理器"""
    
    # 有效期选项（秒）
    DURATION_OPTIONS = {
        "1分钟": 60,
        "1小时": 3600,
        "1天": 86400,
        "7天": 604800,
        "30天": 2592000,
        "永久": -1  # -1 表示永久有效
    }
    
    def __init__(self):
        self.app_dir = get_app_dir()
        self.licenses_file = os.path.join(self.app_dir, 'licenses.json')
        self.license_file = os.path.join(self.app_dir, 'license.key')  # 子机保存的授权码文件
        
    def generate_license_code(self, duration_type: str = "1天", bind_machine: bool = False) -> Optional[str]:
        """
        生成授权码
        
        Args:
            duration_type: 有效期类型（1分钟/1小时/1天/7天/30天/永久）
            bind_machine: 是否绑定机器（True=首次使用时绑定，False=不绑定，可在任何设备使用）
                        注意：即使bind_machine=True，也不会在生成时绑定，而是在子机首次验证时绑定
            
        Returns:
            授权码字符串，如果失败返回None
        """
        try:
            # 获取有效期（秒）
            duration = self.DURATION_OPTIONS.get(duration_type, 86400)
            
            # 生成唯一ID（只取前12位用于显示）
            license_id = str(uuid.uuid4()).replace('-', '')[:12]
            
            # 不绑定机器ID（在子机首次验证时自动绑定）
            # 即使bind_machine=True，也不在生成时绑定，而是在验证时绑定
            machine_id = None
            
            # 计算到期时间
            if duration == -1:
                expire_time = -1  # 永久
                expire_str = "永久"
            else:
                expire_time = (datetime.now() + timedelta(seconds=duration)).timestamp()
                expire_str = datetime.fromtimestamp(expire_time).strftime("%Y-%m-%d %H:%M:%S")
            
            # 创建授权信息
            license_data = {
                "id": license_id,
                "machine_id": machine_id,  # 绑定的机器ID
                "bind_machine": bind_machine,  # 是否绑定机器
                "duration_type": duration_type,
                "duration": duration,
                "create_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "expire_time": expire_time,
                "expire_str": expire_str,
                "status": "active",  # active: 启用, revoked: 停用
                "used": False,
                "used_time": None
            }
            
            # 生成签名
            signature = self._generate_signature(license_data)
            license_data["signature"] = signature
            
            # 将授权信息编码为Base64
            license_json = json.dumps(license_data, ensure_ascii=False)
            license_code = base64.b64encode(license_json.encode('utf-8')).decode('utf-8')
            
            # 保存到授权列表（保存完整UUID用于内部管理）
            license_data["id"] = str(uuid.uuid4())  # 内部使用完整UUID
            self._save_license_to_list(license_data)
            
            return license_code
            
        except Exception as e:
            print(f"生成授权码失败: {e}")
            return None
    
    def _generate_signature(self, license_data: Dict) -> str:
        """生成授权码签名（防止篡改）"""
        try:
            # 创建签名字符串（排除signature字段）
            sign_data = license_data.copy()
            if "signature" in sign_data:
                del sign_data["signature"]
            
            sign_str = json.dumps(sign_data, ensure_ascii=False, sort_keys=True)
            sign_str = sign_str + _LICENSE_KEY
            
            # 计算SHA256哈希
            signature = hashlib.sha256(sign_str.encode('utf-8')).hexdigest()
            return signature
            
        except Exception as e:
            print(f"生成签名失败: {e}")
            return ""
    
    def _save_license_to_list(self, license_data: Dict):
        """保存授权码到列表文件"""
        try:
            licenses = []
            if os.path.exists(self.licenses_file):
                with open(self.licenses_file, 'r', encoding='utf-8') as f:
                    licenses = json.load(f)
            
            # 检查是否已存在相同的ID
            license_id = license_data.get("id")
            licenses = [l for l in licenses if l.get("id") != license_id]
            
            # 添加新授权码
            licenses.append(license_data)
            
            # 保存到文件
            with open(self.licenses_file, 'w', encoding='utf-8') as f:
                json.dump(licenses, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            print(f"保存授权码列表失败: {e}")
    
    def verify_license(self, license_code: str, check_list: bool = True) -> Tuple[bool, str]:
        """
        验证授权码
        
        Args:
            license_code: 授权码
            check_list: 是否检查授权码列表（子机可以设置为False以支持离线验证）
        
        Returns:
            (是否有效, 错误信息)
        """
        try:
            # 解码授权码
            try:
                license_json = base64.b64decode(license_code.encode('utf-8')).decode('utf-8')
                license_data = json.loads(license_json)
            except Exception as e:
                return False, "授权码格式错误"
            
            # 验证签名
            signature = license_data.get("signature", "")
            expected_signature = self._generate_signature(license_data)
            if signature != expected_signature:
                return False, "授权码签名验证失败（可能被篡改）"
            
            # 如果检查列表（母机或在线验证）
            # 注意：只有在列表文件存在时才检查，如果不存在则允许离线验证
            if check_list and os.path.exists(self.licenses_file):
                license_id = license_data.get("id")
                license_info = self._get_license_from_list(license_id)
                
                # 如果找到授权码信息，检查状态和使用情况
                if license_info:
                    # 检查授权码状态（从列表中读取最新状态）
                    if license_info.get("status") == "revoked":
                        # 授权码已被停用，更新授权码文件中的状态
                        license_data["status"] = "revoked"
                        revoked_license_code = base64.b64encode(
                            json.dumps(license_data, ensure_ascii=False).encode('utf-8')
                        ).decode('utf-8')
                        self._save_license_to_file(revoked_license_code)
                        return False, "授权码已被停用"
                    
                    # 标记为已使用
                    if not license_info.get("used"):
                        license_info["used"] = True
                        license_info["used_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        self._update_license_in_list(license_info)
                # 如果列表文件存在但找不到授权码，可能是旧授权码或跨机器使用
                # 这种情况下仍然允许验证（通过签名和过期时间验证）
            
            # 检查是否过期（使用授权码中的过期时间）
            expire_time = license_data.get("expire_time")
            if expire_time != -1:  # 不是永久
                current_time = datetime.now().timestamp()
                if current_time > expire_time:
                    expire_str = license_data.get("expire_str", "未知")
                    return False, f"授权码已过期（过期时间: {expire_str}）"
            
            # 检查机器绑定（如果授权码绑定了机器）
            bind_machine = license_data.get("bind_machine", False)
            current_machine_id = get_machine_id()
            license_machine_id = license_data.get("machine_id")
            
            # 处理机器绑定逻辑
            # 如果bind_machine=True，在首次使用时绑定，换设备时自动重新绑定
            # 如果bind_machine=False，不绑定机器，可以在任何设备使用
            if bind_machine:
                # 如果授权码要求绑定机器
                if not license_machine_id:
                    # 首次使用，绑定到当前机器
                    license_data["machine_id"] = current_machine_id
                    # 重新生成签名（因为machine_id改变了）
                    license_data["signature"] = self._generate_signature(license_data)
                    # 重新编码授权码
                    license_code = base64.b64encode(
                        json.dumps(license_data, ensure_ascii=False).encode('utf-8')
                    ).decode('utf-8')
                elif license_machine_id != current_machine_id:
                    # 授权码已绑定到其他机器，允许换设备使用（自动重新绑定到新设备）
                    # 更新机器ID为新设备
                    license_data["machine_id"] = current_machine_id
                    # 重新生成签名（因为machine_id改变了）
                    license_data["signature"] = self._generate_signature(license_data)
                    # 重新编码授权码
                    license_code = base64.b64encode(
                        json.dumps(license_data, ensure_ascii=False).encode('utf-8')
                    ).decode('utf-8')
            # 如果bind_machine=False，不检查机器ID，可以在任何设备使用
            
            # 检查授权码是否被停用
            # 方法1: 检查列表文件（如果存在，优先使用）
            license_id_12 = license_data.get("id")
            license_machine_id = license_data.get("machine_id")
            create_time = license_data.get("create_time")
            
            if os.path.exists(self.licenses_file):
                licenses = self.get_all_licenses()
                license_info = None
                
                # 优先通过12位ID查找
                for lic in licenses:
                    if (lic.get("display_id") == license_id_12 or 
                        lic.get("id") == license_id_12 or
                        lic.get("id", "")[:12] == license_id_12[:12]):
                        license_info = lic
                        break
                
                # 如果通过ID找不到，尝试通过机器ID和创建时间查找
                if not license_info and license_machine_id and create_time:
                    for lic in licenses:
                        if lic.get("machine_id") == license_machine_id and lic.get("create_time") == create_time:
                            license_info = lic
                            break
                
                # 如果找到授权码信息，检查状态
                if license_info:
                    if license_info.get("status") == "revoked":
                        # 授权码已被停用，同时更新授权码文件中的状态标记
                        license_data["status"] = "revoked"
                        revoked_license_code = base64.b64encode(
                            json.dumps(license_data, ensure_ascii=False).encode('utf-8')
                        ).decode('utf-8')
                        self._save_license_to_file(revoked_license_code)
                        return False, "授权码已被停用"
                # 如果列表文件存在但找不到授权码，可能是旧授权码或跨机器使用
                # 这种情况下仍然允许验证（通过签名和过期时间验证）
            
            # 方法2: 检查授权码本身的状态（支持离线停用检测）
            # 如果授权码中已经标记为停用，直接拒绝
            if license_data.get("status") == "revoked":
                return False, "授权码已被停用"
            
            # 保存到子机授权文件
            # 如果在验证过程中授权码被更新（重新绑定机器ID），使用更新后的授权码
            # 检查license_code是否已被更新（如果更新了，说明machine_id被绑定或重新绑定）
            # 如果bind_machine=True且license_data中有machine_id，说明已经更新过
            if bind_machine and license_data.get("machine_id") == current_machine_id:
                # 授权码已更新（绑定或重新绑定机器ID），使用更新后的授权码
                final_license_code = base64.b64encode(
                    json.dumps(license_data, ensure_ascii=False).encode('utf-8')
                ).decode('utf-8')
            else:
                # 使用原始授权码或已更新的授权码
                # 如果license_code在验证过程中被更新了，直接使用它
                final_license_code = license_code
            
            self._save_license_to_file(final_license_code)
            
            return True, "授权验证成功"
            
        except Exception as e:
            return False, f"验证授权码失败: {str(e)}"
    
    def _get_license_from_list(self, license_id: str) -> Optional[Dict]:
        """从列表中获取授权码信息"""
        try:
            if not os.path.exists(self.licenses_file):
                return None
            
            with open(self.licenses_file, 'r', encoding='utf-8') as f:
                licenses = json.load(f)
            
            for license_info in licenses:
                if license_info.get("id") == license_id:
                    return license_info
            
            return None
            
        except Exception as e:
            print(f"获取授权码信息失败: {e}")
            return None
    
    def _update_license_in_list(self, license_data: Dict):
        """更新授权码列表中的授权码信息"""
        try:
            if not os.path.exists(self.licenses_file):
                return
            
            with open(self.licenses_file, 'r', encoding='utf-8') as f:
                licenses = json.load(f)
            
            license_id = license_data.get("id")
            for i, license_info in enumerate(licenses):
                if license_info.get("id") == license_id:
                    licenses[i] = license_data
                    break
            
            with open(self.licenses_file, 'w', encoding='utf-8') as f:
                json.dump(licenses, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            print(f"更新授权码信息失败: {e}")
    
    def _save_license_to_file(self, license_code: str):
        """保存授权码到子机文件"""
        try:
            with open(self.license_file, 'w', encoding='utf-8') as f:
                f.write(license_code)
        except Exception as e:
            print(f"保存授权码文件失败: {e}")
    
    def load_license_from_file(self) -> Optional[str]:
        """从文件加载授权码"""
        try:
            if os.path.exists(self.license_file):
                with open(self.license_file, 'r', encoding='utf-8') as f:
                    return f.read().strip()
            return None
        except Exception as e:
            print(f"加载授权码文件失败: {e}")
            return None
    
    def check_license_valid(self, check_list: bool = False) -> Tuple[bool, str]:
        """检查当前授权码是否有效"""
        license_code = self.load_license_from_file()
        if not license_code:
            return False, "未找到授权码，请输入授权码"
        
        # 子机检查时，先尝试离线验证（不检查列表）
        # 这样可以支持离线使用
        return self.verify_license(license_code, check_list=check_list)
    
    def revoke_license(self, license_id: str) -> bool:
        """停用授权码"""
        try:
            if not os.path.exists(self.licenses_file):
                return False
            
            with open(self.licenses_file, 'r', encoding='utf-8') as f:
                licenses = json.load(f)
            
            found = False
            for license_info in licenses:
                # 支持通过完整UUID或12位ID查找
                if (license_info.get("id") == license_id or 
                    license_info.get("display_id") == license_id or
                    license_info.get("id", "")[:12] == license_id[:12]):
                    license_info["status"] = "revoked"
                    license_info["revoke_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    found = True
                    break
            
            if found:
                with open(self.licenses_file, 'w', encoding='utf-8') as f:
                    json.dump(licenses, f, indent=2, ensure_ascii=False)
                return True
            
            return False
            
        except Exception as e:
            print(f"停用授权码失败: {e}")
            return False
    
    def delete_license(self, license_id: str) -> bool:
        """删除授权码"""
        try:
            if not os.path.exists(self.licenses_file):
                return False
            
            with open(self.licenses_file, 'r', encoding='utf-8') as f:
                licenses = json.load(f)
            
            original_count = len(licenses)
            # 过滤掉要删除的授权码
            licenses = [
                lic for lic in licenses
                if not (
                    lic.get("id") == license_id or 
                    lic.get("display_id") == license_id or
                    lic.get("id", "")[:12] == license_id[:12]
                )
            ]
            
            if len(licenses) < original_count:
                with open(self.licenses_file, 'w', encoding='utf-8') as f:
                    json.dump(licenses, f, indent=2, ensure_ascii=False)
                return True
            
            return False
            
        except Exception as e:
            print(f"删除授权码失败: {e}")
            return False
    
    def count_expired_or_revoked(self) -> Tuple[int, int]:
        """
        统计已过期或已停用的授权码数量（不删除）
        
        Returns:
            (过期授权码数量, 停用授权码数量)
        """
        try:
            if not os.path.exists(self.licenses_file):
                return 0, 0
            
            with open(self.licenses_file, 'r', encoding='utf-8') as f:
                licenses = json.load(f)
            
            current_time = datetime.now().timestamp()
            
            expired_count = 0
            revoked_count = 0
            
            for lic in licenses:
                status = lic.get("status", "active")
                expire_time = lic.get("expire_time", -1)
                
                # 检查是否已停用
                if status == "revoked":
                    revoked_count += 1
                    continue
                
                # 检查是否已过期
                if expire_time != -1 and current_time > expire_time:
                    expired_count += 1
                    continue
            
            return expired_count, revoked_count
            
        except Exception as e:
            print(f"统计授权码失败: {e}")
            return 0, 0
    
    def batch_delete_expired_or_revoked(self) -> Tuple[int, int]:
        """
        批量删除已过期或已停用的授权码
        
        Returns:
            (删除的过期授权码数量, 删除的停用授权码数量)
        """
        try:
            if not os.path.exists(self.licenses_file):
                return 0, 0
            
            with open(self.licenses_file, 'r', encoding='utf-8') as f:
                licenses = json.load(f)
            
            original_count = len(licenses)
            current_time = datetime.now().timestamp()
            
            expired_count = 0
            revoked_count = 0
            
            # 过滤掉已过期或已停用的授权码
            valid_licenses = []
            for lic in licenses:
                status = lic.get("status", "active")
                expire_time = lic.get("expire_time", -1)
                
                # 检查是否已停用
                if status == "revoked":
                    revoked_count += 1
                    continue
                
                # 检查是否已过期
                if expire_time != -1 and current_time > expire_time:
                    expired_count += 1
                    continue
                
                # 保留有效的授权码
                valid_licenses.append(lic)
            
            # 如果有删除的授权码，保存更新后的列表
            if len(valid_licenses) < original_count:
                with open(self.licenses_file, 'w', encoding='utf-8') as f:
                    json.dump(valid_licenses, f, indent=2, ensure_ascii=False)
            
            return expired_count, revoked_count
            
        except Exception as e:
            print(f"批量删除失败: {e}")
            return 0, 0
    
    def get_all_licenses(self) -> List[Dict]:
        """获取所有授权码列表"""
        try:
            if os.path.exists(self.licenses_file):
                with open(self.licenses_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return []
        except Exception as e:
            print(f"获取授权码列表失败: {e}")
            return []
    
    def get_license_info(self, license_code: str) -> Optional[Dict]:
        """获取授权码信息（不解码）"""
        try:
            license_json = base64.b64decode(license_code.encode('utf-8')).decode('utf-8')
            license_data = json.loads(license_json)
            return license_data
        except:
            return None


if __name__ == '__main__':
    # 测试代码
    manager = LicenseManager()
    
    # 生成测试授权码
    code = manager.generate_license_code("1分钟")
    print(f"生成的授权码: {code}")
    
    # 验证授权码
    valid, msg = manager.verify_license(code)
    print(f"验证结果: {valid}, 消息: {msg}")

