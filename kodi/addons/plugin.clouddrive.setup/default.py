import xbmc
import xbmcgui
import xbmcaddon
import sys
import os   
from resources.lib.menu import router

# 导入自定义模块
from resources.lib.api_client import CloudDrive

addon = xbmcaddon.Addon()
addon_name = addon.getAddonInfo('name')


# 检查网络连接
def check_internet():
    response = os.system("ping -c 1 baidu.com")
    return response == 0

def main():
    if not CloudDrive.api_internet():
        dialog = xbmcgui.Dialog()
        dialog.ok("服务器访问失败", "请稍后再试!")
        exit()
      
    router(sys.argv[2][1:])

if __name__ == '__main__':
    main()    