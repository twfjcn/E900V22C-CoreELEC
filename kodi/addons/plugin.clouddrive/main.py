import xbmc
import xbmcgui
import os
import socket
import xbmcvfs  # 确保导入了此模块
from http_server import run_http_server, stop_http_server
import threading
           
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

# 从配置文件中读取CD2+AList版本号
def read_cd2_from_config():
    # 使用xbmcvfs.translatePath获取Kodi的特定目录路径
    #config_path = '/storage/.kodi/userdata/userconfig/npc.conf'  
    config_path = xbmcvfs.translatePath('special://userdata/Version')

    try:
        with open(config_path, 'r') as f:
            for line in f.readlines():
                if line.startswith('cd2='):
                    return line.split('=')[1].strip()
    except Exception as e:
        # 处理文件打开错误等异常
        print(f"Error reading config file: {e}")

    return None

# 从配置文件中读取AList版本号
def read_alist_from_config():
    # 使用xbmcvfs.translatePath获取Kodi的特定目录路径
    #config_path = '/storage/.kodi/userdata/userconfig/npc.conf'  
    config_path = xbmcvfs.translatePath('special://userdata/Version')

    try:
        with open(config_path, 'r') as f:
            for line in f.readlines():
                if line.startswith('alist='):
                    return line.split('=')[1].strip()
    except Exception as e:
        # 处理文件打开错误等异常
        print(f"Error reading config file: {e}")

    return None

def read_path_from_config():
    # 使用xbmcvfs.translatePath获取Kodi的特定目录路径
    #config_path = '/storage/.kodi/userdata/userconfig/npc.conf'  
    config_path = xbmcvfs.translatePath('special://userdata/cdisklist.txt')
    try:
        with open(config_path, 'r') as f:    
            for line in f.readlines():
                #if line.startswith('115'):
                    return line.split()
    except Exception as e:
        # 处理文件打开错误等异常
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
        local_ip = get_local_ip()
        website_url = f"http://{local_ip}:80"
        qr_code_url = f"https://qun.qq.com/qrcode/index?data={website_url}"
        cd2 = read_cd2_from_config()
        alist = read_alist_from_config()
        catalogue = read_path_from_config()
        # 显示自定义对话框
        xml_file_name = "dialog_layout.xml"
        xml_file_path = "/usr/share/kodi/addons/plugin.clouddrive/"
        skin_name = "Default"
    
        dialog = CustomQRDialog(xml_file_name, xml_file_path, skin_name, qr_code_url=qr_code_url, cd2=cd2, alist=alist, catalogue=catalogue)
        
        dialog.doModal()
        del dialog
        
    # 当对话框关闭时，停止HTTP服务器
    stop_http_server()
    # 确保线程已完全关闭
    server_thread.join()

if __name__ == "__main__":
    main()

