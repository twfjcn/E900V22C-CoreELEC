import xbmc
import xbmcgui
import os
import socket
import xbmcvfs
import urllib.request
from http.server import run_http_server, stop_http_server
import threading


# 检查网络连接
def check_internet():
    response = os.system("ping -c 1 www.baidu.com")
    return response == 0


# 获取机器的内网IP地址
def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception as e:
        xbmc.log(f"Error getting local IP address: {e}", xbmc.LOGERROR)
        return "127.0.0.1"


# 从配置文件中读取CD2+AList版本号
def read_cd2_from_config():
    config_path = xbmcvfs.translatePath('special://userdata/Version')
    try:
        with open(config_path, 'r') as f:
            for line in f.readlines():
                if line.startswith('cd2='):
                    return line.split('=')[1].strip()
    except Exception as e:
        print(f"Error reading config file: {e}")
    return None


# 从配置文件中读取AList版本号
def read_alist_from_config():
    config_path = xbmcvfs.translatePath('special://userdata/Version')
    try:
        with open(config_path, 'r') as f:
            for line in f.readlines():
                if line.startswith('alist='):
                    return line.split('=')[1].strip()
    except Exception as e:
        print(f"Error reading config file: {e}")
    return None


def read_path_from_config():
    config_path = xbmcvfs.translatePath('special://userdata/cdisklist.txt')
    try:
        with open(config_path, 'r') as f:
            for line in f.readlines():
                # if line.startswith('115'):
                return line.split()
    except Exception as e:
        print(f"Error reading config file: {e}")
    return None


class CustomQRDialog(xbmcgui.WindowXMLDialog):
    def __init__(self, *args, **kwargs):
        super().__init__(*args)
        self.qr_code_url = kwargs["qr_code_url"]
        self.cd2 = kwargs.get("cd2")
        self.alist = kwargs.get("alist")
        self.catalogue = kwargs.get("catalogue")
        self.local_ip = get_local_ip()

    def onInit(self):
        # 设置二维码图片
        self.getControl(100).setImage(self.qr_code_url)
        # 设置提示信息
        self.getControl(101).setLabel("扫描二维码登陆CD2（挂载云盘）")
        # 设置IP地址
        self.getControl(102).setLabel(f"IP地址: {self.local_ip}")
        # 设置vkey值信息
        # self.getControl(103).setLabel(f"UUID1: {self.vkey}")
        self.getControl(103).setLabel(f"或者浏览器输入IP地址（登录设备需在同一网段）")

        self.getControl(104).setLabel(f"CD2版本号：{self.cd2}\n")
        self.getControl(105).setLabel(f"AList版本号：{self.alist}")
        self.getControl(106).setLabel(f"AList地址：{self.local_ip}:5244\n    用户名：admin 密码：1234")
        self.getControl(108).setLabel(f"已挂载的云盘：{self.catalogue}")


# 按顺序尝试获取二维码的函数
def get_qr_code_url():
    local_ip = get_local_ip()
    website_url = f"http://{local_ip}:80"

    # 接口一
    qr_code_url = f"https://qun.qq.com/qrcode/index?data={website_url}"
    try:
        with urllib.request.urlopen(qr_code_url) as response:
            if response.getcode() == 200:
                return qr_code_url
    except:
        pass

    # 接口二
    qr_code_url = f"https://api.pwmqr.com/qrcode/create/?url={website_url}"
    try:
        with urllib.request.urlopen(qr_code_url) as response:
            if response.getcode() == 200:
                return qr_code_url
    except:
        pass

    # 接口三
    qr_code_url = f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data={website_url}"
    try:
        with urllib.request.urlopen(qr_code_url) as response:
            if response.getcode() == 200:
                return qr_code_url
    except:
        pass

    return None


# 主逻辑
def main():
    # 使用一个线程启动HTTP服务器
    server_thread = threading.Thread(target=run_http_server)
    server_thread.start()

    if not check_internet():
        local_ip = get_local_ip()
        dialog = xbmcgui.Dialog()
        dialog.ok("网络问题", f"您的设备未联网，设备IP：{local_ip}")
    else:
        qr_code_url = get_qr_code_url()
        if qr_code_url is None:
            dialog = xbmcgui.Dialog()
            dialog.ok("二维码获取失败", "无法获取二维码，请检查网络和接口设置。")
            return

        local_ip = get_local_ip()
        cd2 = read_cd2_from_config()
        alist = read_alist_from_config()
        catalogue = read_path_from_config()

        # 显示自定义对话框
        xml_file_name = "dialog_layout.xml"
        xml_file_path = "/usr/share/kodi/addons/plugin.clouddrive/"
        skin_name = "Default"

        dialog = CustomQRDialog(xml_file_name, xml_file_path, skin_name, qr_code_url=qr_code_url, cd2=cd2, alist=alist,
                                catalogue=catalogue)

        dialog.doModal()
        del dialog

    # 当对话框关闭时，停止HTTP服务器
    stop_http_server()
    # 确保线程已完全关闭
    server_thread.join()


if __name__ == "__main__":
    main()

