import xbmcaddon
import xbmcgui
import xbmc
import os
import subprocess


def show_confirmation_dialog():
    addon = xbmcaddon.Addon()
    addon_name = addon.getAddonInfo('name')
    dialog = xbmcgui.Dialog()
    confirmed = dialog.yesno(addon_name, '确定要把系统还原到原厂设置吗？')
    return confirmed


def delete_clouddrive_file():
    file_path = os.path.join('/storage/.kodi/clouddrive2/', 'clouddrive')
    if os.path.exists(file_path):
        try:
            os.remove(file_path)
            xbmc.log(f"成功删除 {file_path}")
        except Exception as e:
            xbmc.log(f"删除 {file_path} 时出错: {e}", level=xbmc.LOGERROR)


def reboot_system():
    try:
        subprocess.run(['reboot'], check=True)
    except subprocess.CalledProcessError as e:
        xbmc.log(f"重启系统时出错: {e}", level=xbmc.LOGERROR)


def main():
    if show_confirmation_dialog():
        delete_clouddrive_file()
        reboot_system()


if __name__ == "__main__":
    main()
