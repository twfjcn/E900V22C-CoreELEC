import xbmc
import xbmcgui
import os
import socket
import xbmcvfs  # 确保导入了此模块

# 检查网络连接
def check_internet():
    response = os.system("ping -c 1 www.baidu.com")
    return response == 0

# 获取机器的内网IP地址
def get_local_ip():
    try:
        # 这将创建一个UDP连接（并不真正进行数据传输）以访问公共IP，这样就可以返回正确的本地IP地址
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))  # 使用Google的公共DNS服务器IP来获取本地的出口IP
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception as e:
        xbmc.log(f"Error getting local IP address: {e}", xbmc.LOGERROR)
        return "127.0.0.1"

# 从配置文件中读取vkey
def read_vkey_from_config():
    # 使用xbmcvfs.translatePath获取Kodi的特定目录路径
    config_path = xbmcvfs.translatePath('special://userdata/userconfig/npc.conf')

    try:
        with open(config_path, 'r') as f:
            for line in f.readlines():
                if line.startswith('vkey='):
                    return line.split('=')[1].strip()
    except Exception as e:
        # 处理文件打开错误等异常
        print(f"Error reading config file: {e}")

    return None

class CustomQRDialog(xbmcgui.WindowXMLDialog):
    def __init__(self, xmlFilename, scriptPath, defaultSkin, defaultRes, *args, **kwargs):
        super(CustomQRDialog, self).__init__(xmlFilename, scriptPath, defaultSkin, defaultRes)
        self.qr_code_url = kwargs.get("qr_code_url")
        self.vkey = kwargs.get("vkey")
        self.local_ip = get_local_ip()

    def onInit(self):
        self.getControl(100).setImage(self.qr_code_url)
        self.getControl(101).setLabel("请打开手机浏览器扫描二维码挂载云盘")
        self.getControl(102).setLabel(f"IP地址: {self.local_ip}")
        self.getControl(103).setLabel("注意：请确保手机与播放器连接了同一个网络")
        self.getControl(104).setLabel("Alist挂载地址")
        self.getControl(105).setLabel(f"请用电脑浏览器输入: {self.local_ip}:5244")

def main():
    if not check_internet():
        local_ip = get_local_ip()
        dialog = xbmcgui.Dialog()
        dialog.ok("网络问题", f"您的设备未联网，设备IP：{local_ip}")
    else:
        local_ip = get_local_ip()
        qr_code_url = f"https://qun.qq.com/qrcode/index?data=http://{local_ip}"
        vkey = read_vkey_from_config()
        
        # 显示自定义对话框
        scriptPath = xbmcvfs.translatePath("special://home/addons/plugin.clouddrive/")
        xmlFilename = "dialog_layout.xml"
        defaultSkin = "Default"
        defaultRes = "1080i"
        dialog = CustomQRDialog(xmlFilename, scriptPath, defaultSkin, defaultRes, qr_code_url=qr_code_url, vkey=vkey)
        dialog.doModal()
        del dialog
        
if __name__ == "__main__":
    main()