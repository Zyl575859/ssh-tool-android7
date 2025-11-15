import os
import runpy
import sys
import traceback

try:
    import tkinter as _tk
    from tkinter import messagebox as _messagebox
except Exception:
    _tk = None
    _messagebox = None


def main() -> None:
    if os.name == "nt":
        os.system("chcp 65001 >nul")
        os.system("title SSH连接工具 - 图形界面")
        os.system("color 0A")

    print()
    print("正在启动SSH连接工具（图形界面）...")
    print()

    base_dir = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    if base_dir not in sys.path:
        sys.path.insert(0, base_dir)

    script_path = os.path.join(base_dir, "ssh_tool_gui.py")

    try:
        runpy.run_path(script_path, run_name="__main__")
    except Exception as exc:
        print()
        print("启动失败，可能的原因：")
        print("1. 程序缺少运行依赖")
        print("2. 未正确解压全部文件")
        print()
        print("错误详情:")
        traceback.print_exc()

        error_msg = f"启动失败: {exc}\n\n详情已输出到控制台。"

        if _tk and _messagebox:
            try:
                root = _tk.Tk()
                root.withdraw()
                _messagebox.showerror("启动失败", error_msg)
            except Exception:
                pass
            finally:
                try:
                    root.destroy()
                except Exception:
                    pass
        else:
            try:
                import ctypes

                ctypes.windll.user32.MessageBoxW(
                    None,
                    error_msg,
                    "启动失败",
                    0x00000010,  # MB_ICONERROR
                )
            except Exception:
                pass


if __name__ == "__main__":
    main()

