@echo off
start /d "D:\application\obs-studio\bin\64bit" obs64.exe -m --websocket_port 4444 --websocket_password "123456"
start /d "D:\application\obs-studio\bin\64bit" obs64.exe -m --websocket_port 5555 --websocket_password "123456"
start /d "D:\application\obs-studio\bin\64bit" obs64.exe -m --websocket_port 6666 --websocket_password "123456"
