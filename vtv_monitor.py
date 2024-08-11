import streamlink
import subprocess
import sys
import threading
# import undetected_chromedriver as uc 
# import time
from OBS_Controller_oop import OBS_controller
import time
import undetected_chromedriver as uc 


class VTV_Monitor():
    def __init__(self, obs_controller: OBS_controller, url: str, port: str, scene:str, source:str, browser_path="C:/Program Files/Google/Chrome/Application/chrome.exe",quality="best"):
        self.obs_controller = obs_controller
        self.url = url
        self.port = port
        self.scene = scene
        self.source = source
        self.browser_path = browser_path
        self.quality = quality
        self.streamlink_subprocess: subprocess = None
        
        self.rehost_event = threading.Event()
        self.refresh_event = threading.Event()
        
        
    
    def get_cookie(self,url, name):
        # headless flag must be fail
        self.driver = uc.Chrome(headless=False,use_subprocess=True) 
        self.driver.get(url)
        time.sleep(1)
        my_cookie = self.driver.get_cookie(name)
        print (my_cookie)
        self.driver.close()
        # very importance if remove will raise an error
        time.sleep(1)
        return my_cookie.get("value") 
    
    def host_stream(self):
        aws_waf_token_cookie = self.get_cookie(self.url,"aws-waf-token")
        print(aws_waf_token_cookie)
        cmd = [
            "streamlink",
            "--webbrowser-executable",  self.browser_path,
            # "--http-cookie", f"aws-waf-token={aws_waf_token_cookie}",
            "--player-external-http-continuous", "0",
            "--player-external-http",
            "--player-external-http-port", self.port,
            self.url, "best"
        ]
        self.streamlink_process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        host_process_not_finish = True
        while True:
            output = self.streamlink_process.stdout.readline()
            if output:
                print(output.strip())
                if "[cli][info]  http://127.0.0.1:" in output:
                    print("Server started. Proceeding with additional commands...")
                    self.refresh_event.set()
                    break
                    
        self.streamlink_process.wait()
        self.rehost_event.set()
        
    def refresh_source(self):
        while True:
            try:
                self.refresh_event.wait()
                self.refresh_event.clear()
                if self.obs_controller.get_scene_item_enabled(self.scene,self.source):
                    self.obs_controller.toggle_scene_item_enabled(self.scene,self.source)
                else:
                    self.obs_controller.set_scene_item_enabled()
                    
            except Exception as e:
                print(f"[ERROR]: {e}")
                 
                
            except KeyboardInterrupt:
                print("end thread refresh")
                break
                
    def re_host_stream(self):
         while True:
            try:
                self.rehost_event.wait()
                self.rehost_event.clear()
                time.sleep(15)
                self.host_stream()
                
            except Exception as e:
                print(f"[ERROR]: {e}")
                if self.driver:
                    self.driver.close()
                time.sleep(10)
                self.host_stream()
                
            except KeyboardInterrupt:
                print("end thread refresh")
                break
            
    def run(self):
        rehost_stream_thread = threading.Thread( target=self.re_host_stream,daemon= True)
        refresh_thread = threading.Thread( target= self.refresh_source,daemon = True)
        rehost_stream_thread.start()
        refresh_thread.start()
        self.host_stream()
        while True:
            try:
                print(self.obs_controller.get_media_input_status(self.source))
                time.sleep(10)
            except KeyboardInterrupt:
                break
        
if __name__ == "__main__":
    myvtv = VTV_Monitor(
        OBS_controller("localhost", 4455, "123456"),
        url = "https://vtvgo.vn/xem-truc-tuyen-kenh-vtv1-1.html",
        port= "9091",
        scene="LIVE",
        source="myscreen"
    )
    myvtv.run()