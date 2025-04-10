import xbmcaddon
import xbmcgui
import xbmc
import os
import subprocess
import shutil

addon = xbmcaddon.Addon()
addonname = addon.getAddonInfo('name')


def check_internet():
    response = os.system("ping -c 1 www.baidu.com")
    return response == 0


def systen_update():
    UPD = '/tmp/upd'
    if os.path.exists(UPD):
        xbmc.executebuiltin('Notification(系统更新, 后台正在运行更新)')
        exit()
    else:
        xbmc.executebuiltin('Notification(检查更新, 请稍等...)')

    UPDATEPRO = '/tmp/up'
    nandscript = '/usr/bin/updatecheck'
    pwd = 'up'
    pwdd = 'update'
    cmd = nandscript + ' ' + pwd
    cmdd = nandscript + ' ' + pwdd
    subprocess.getstatusoutput(cmd)
    if os.path.exists(UPDATEPRO):
        f = open(UPDATEPRO, 'r')
        line1 = f.read()
        line2 = "版本号："
        line3 = ("有可用更新，是否现在更新？\n" + line2 + line1)
        xbmc.executebuiltin('Notification(有可用更新！, 是否下载升级包？)')
        os.remove(UPDATEPRO)
        if xbmcgui.Dialog().yesno(addonname, line3):
            xbmc.executebuiltin('Notification(正在下载升级包!,请稍等...)')
            if os.path.exists(nandscript):
                os.mknod(UPD)
                # 启动更新进程并记录进程 ID
                process = subprocess.Popen(cmdd, shell=True)
                pid = process.pid
                UPDATE = '/tmp/fini'
                if os.path.exists(UPDATE):
                    xbmc.executebuiltin('Notification(升级包下载完成, 系统即将重启！...)')
                    # os.remove(UPDATE)
                    xbmc.sleep(3000)
                    os.system('reboot')
                else:
                    xbmc.executebuiltin('Notification(系统更新, 无可用更新)')
                    os.remove(UPD)
        else:
            # 终止 /storage/.config/cu 运行
            try:
                os.kill(pid, 9)
            except NameError:
                pass
            except OSError:
                pass
            # 删除 /storage/.update/ 下的文件
            update_dir = '/storage/.update/'
            if os.path.exists(update_dir):
                for item in os.listdir(update_dir):
                    item_path = os.path.join(update_dir, item)
                    if os.path.isfile(item_path):
                        os.remove(item_path)
                    elif os.path.isdir(item_path):
                        shutil.rmtree(item_path)
            # 删除 /tmp/ 下的 fini 标记文件
            fini_file = '/tmp/fini'
            if os.path.exists(fini_file):
                os.remove(fini_file)
    else:
        xbmc.executebuiltin('Notification(系统更新, 无可用更新)')


def main():
    if not check_internet():
        xbmc.executebuiltin('Notification(系统更新, 你的设备未联网！)')
    else:
        systen_update()


if __name__ == "__main__":
    main()
    