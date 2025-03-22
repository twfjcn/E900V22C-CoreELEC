#!/bin/sh
cd /storage/.kodi/clouddrive2
./clouddrive &

cd /storage/.kodi/alist
./alist server &

cd /usr/config
./book.sh &
