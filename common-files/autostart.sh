#!/bin/sh
systemctl start bluetooth
#sleep表示等待时间 时间长短根据电视开机时间调整 默认3秒足够用了
sleep 3
cp /storage/config.toml /storage/Waytech/CloudDrive2/config.toml
cd /storage/.kodi/clouddrive2
./clouddrive &

cd /storage/.kodi/alist/
./alist server &

