import subprocess
import sys
import threading
# import undetected_chromedriver as uc 
# import time
from get_cookies_avoid_bot_detection import get_cookie
from OBS_Controller_oop import OBS_controller
import time

process = None
browser_path = "C:\Program Files\Google\Chrome\Application\chrome.exe"
url =  "https://vtvgo.vn/xem-truc-tuyen-kenh-vtv1-1.html"
port = "9091"
sceen_name = "LIVE"
source_name = "myscreen"
obs_monitor = OBS_controller("localhost",4455,"123456")

def host_stream(url,port):
    global process, obs_monitor, sceen_name, source_name
    if process is not None:
        process.terminate()
        time.sleep(3)
    aws_waf_token_cookie = get_cookie(url,"aws-waf-token")
    print(aws_waf_token_cookie)
    cmd = [
        "streamlink",
        "--webbrowser-executable", browser_path,
        # "--http-cookie", f"aws-waf-token={aws_waf_token_cookie}",
        "--player-external-http-continuous", 0,
        "--player-external-http",
        "--player-external-http-port", port,
        url, 
        "best"
    ]
    # Start the streamlink process
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    print("run stream link proccess")
    while True:
        output = process.stdout.readline()
        if output:
            print(output.strip())
            if "[cli][info]  http://127.0.0.1:" in output:
                print("Server started. Proceeding with additional commands...")
                break
            
            
    # need improve code

    
    # Monitor the output
    # while True:
    #     output = process.stdout.readline()
    #     # if output == '' and process.poll() is not None:
    #     #     break
    #     if output:
    #         print(output.strip())
    #     time.sleep(1)
    
def monitor_streamlink( interval):
    global subprocess, url, port_ws, obs_monitor, source_name,sceen_name
    obs_monitor.toggle_scene_item_enabled(sceen_name,source_name)
    count_end = 0
    state_want_to_restart = ["OBS_MEDIA_STATE_ENDED", "OBS_MEDIA_STATE_ERROR", "OBS_MEDIA_STATE_OPENING"]
    while True:
        try:
            media_status = obs_monitor.get_media_input_status(source_name)
            print(media_status)
            if media_status in state_want_to_restart:
                count_end += 1
                if count_end >= 5:
                    print("input get problem") 
                    if subprocess is not None:
                        host_stream(url,port)
            else:
                count_end = 0

            time.sleep(interval)
        except Exception as e:
            # obs_monitor.close()
            print(f"[ERROR:] {e}")
    
# t1 = threading.Thread(target=host_stream, args=(url,port,),daemon=True)
t2 = threading.Thread(target=monitor_streamlink, args=(10,),daemon=True)



if __name__ == "__main__":
    
    # host_stream(url, port)
    # t1.start()
    host_stream(url,port)
    # time.sleep(10)
    print("start monitor source")
    t2.start()
    while True:
        try:
            output = process.stdout.readline()
            error_streamlink = process.stderr.readline()
            if output:
                print(output.strip())
            if error_streamlink:
                print(error_streamlink.strip())
            time.sleep(1)
        except Exception:
            break