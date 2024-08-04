import obsws_python as obs
import json
import time

from obsws_python.error import OBSSDKRequestError
class OBS_controller:
    
    def printJsonObject(self,object):
        print(json.dumps(object,indent=3))
        
        
    def printJsonObjectList(self,object_list):
        for object in object_list:
            self.printJsonObject(object)
            
    def __init__(self, host='172.28.182.84', port=4455, password='123456') -> None:
        # flag = False
        # # Đọc file config.txt
        # with open('config.txt', 'r') as file:
        #     # Đọc từng dòng trong file
        #     for line in file:
        #         # Tách chuỗi thành hai phần, phần bên trái là key, phần bên phải là value
        #         key, value = line.strip().split('-')
        #         # Nếu key là 'VIDEO PATH', lưu giá trị vào biến videopath và thoát vòng lặp
        #         if key.strip() == 'PORT':
        #             self.port = value
        #             flag = True
        #             break
        # if not flag:
        #     self.port = port
        self.port = port
        self.host = host
        self.password = password
        self.request_client = obs.ReqClient(host = self.host,port = self.port,password = self.password)

        
    def get_input_list(self,kind=None):
        """
        Get inputs of obs
        Args:
            kind (String, optional): Restrict the array to only inputs of the specified kind. Defaults to None.

        Returns:
        Object : response contain field "inputs" (Array<Object>)
        """
        response = self.request_client.get_input_list(kind)
        self.printJsonObjectList(response.inputs)
        return response
        
    def get_input_settings(self,name):
        """ 
        To create the entire settings object,
        overlay inputSettings over the defaultInputSettings provided by GetInputDefaultSettings

        Args:
            name (String): Name of the input to get the settings of

        Returns:
            Object contain:
                +input_settings(Object): Object of settings for the input
                +input_kind(String):The kind of the input
        """
        payload = {"inputName": name}
        response =  self.request_client.send("GetInputSettings", payload)
        self.printJsonObject(response.input_settings)
        return response

        
    def set_input_settings(self,name, settings, overlay):
        """
        Sets the settings of an input.

        Args:
            name (String, optional): Name of the input to set the settings of
            settings (Object):
                -attr: can use get_input_settings to see an example
                    + playback_behavior(String): ex: "stop_restart"
                    + playlist(Array<object>):
                        -item:
                            hidden(bool): video is hidden or not
                            selected(bool):video is sellected 
                            value(string): path to video or source
                    + shuffle(bool): playlist is played random or not
            overlay (bool, optional):   True == apply the settings on top of existing ones, 
                                        False == reset the input to its defaults, then apply settings.

        Returns: None
        """
        print("33333333")
        print(settings)
        return self.request_client.set_input_settings(name, settings, overlay)   
    
    def get_scene_item_list(self,name):
        """ 
        get scene item list of an scene

        Args:
            name (String): Name of the scene

        Returns:
            Object contain:
                scene_items (Array<Objest>) : Array of scene items in the scene
        """
        payload = {"sceneName": name}
        response =  self.request_client.send("GetSceneItemList", payload)
        self.printJsonObject(response.scene_items)
        return response

    def create_scene(self, _name):
        self.request_client.create_scene(name=_name)

    def get_stream_service_settings(self):
        """
        Gets the current stream service settings (stream destination)

        Returns:
            object:
            - attr:
                + stream_service_type (String): Stream service type, like rtmp_custom or rtmp_common
                + stream_service_settings(Object): Stream service settings
                    -attr:
                        + bwtest (Bool): bandwidth test option
                        + key (String): stream key of rtmp protocol
                        + protocol (String):  protocol is using
                        + server (String): server is used
                        + use_auth (Bool): use authentication or not
        """
        response =  self.request_client.get_stream_service_settings() 
        self.printJsonObject(response.stream_service_settings)
        print(response.stream_service_type)
        return response
    
    def set_stream_service_settings(self,stream_service_type,stream_service_settings):
        """
        Sets the current stream service settings (stream destination)
        Note: Simple RTMP settings can be set with type rtmp_custom and the settings fields server and key.
        

        Args:
            stream_service_type (String): type of stream service to apply. Example: rtmp_common or rtmp_custom
            stream_service_settings (Object): Settings to apply to the service, can use get_stream_service_settings to see an example
        """
        self.request_client.set_stream_service_settings(ss_type = stream_service_type, ss_settings = stream_service_settings)
                
    def start_stream(self):
        """
        start livestream on OBS
        """
        self.request_client.start_stream()
        
    def stop_stream(self):
        """
        Stop Livestream on OBS
        """
        self.request_client.stop_stream()
        
    def toggle_stream(self):
        """
        toggle Livestream on OBS
        """
        self.request_client.toggle_stream()
        
    def get_stream_status(self):
        """
        Gets the status of the stream output.
        Returns:
            Object: 
            -attr:
                + output_active (Bool): Whether the output is active
                + output_bytes (Boolean): Whether the output is active
                + output_timecode (String): Current formatted timecode string for the output
                + utput_duration (Number): Current duration in milliseconds for the output
                + output_congestion (Number): Congestion of the output
                + output_reconnecting (Number): Number of bytes sent by the output
                + output_skipped_frames (Number): Number of frames skipped by the output's process
                + output_total_frames (Number): Total number of frames delivered by the output's process
        """
        request = self.request_client.get_stream_status()
        print("Stream Status")
        print(f"\t output active: {request.output_active}")
        print(f"\t output bytes: {request.output_bytes}")
        print(f"\t output congestion: {request.output_congestion}")
        print(f"\t output duration: {request.output_duration}")
        print(f"\t output reconnecting: {request.output_reconnecting}")
        print(f"\t output skipped frames: {request.output_skipped_frames}")
        print(f"\t output timecode:{request.output_timecode}")
        print(f"\t output total frames:{request.output_total_frames}")
        return request
    
    def check_stream_is_active(self):
        response = self.get_stream_status()
        return response.output_active
    
    def is_exited_in_playlist(self,source_name,video_path):
        """
        check video is in playlist or not

        Args:
            source_name (String): name of source
            video_path (String): video path want to check is exited or not

        Returns:
            Bool: true if exist otherwise false if not
        """
        #load input_settings of source_name
        response = self.get_input_settings(source_name)
        input_settings = response.input_settings
        for item in input_settings.get('playlist'):
            if item.get("value") == video_path:
                return True
        return False
    
    def add_video_to_playlist(self, source_name, video_path, hidden = False, selected = False):
        """
        Add an video to playlist of the source 

        Args:
            source_name (String): Name of source
            path_video (String): path to the video in server run obs
        Return:
            Bool: true if success, false if not
        """
        
        #load input_settings of source_name
        response = self.get_input_settings(source_name)
        input_settings = response.input_settings
        # self.printJsonObject(input_settings.get('playlist'))
        # creating an item to add into list if this item is not exist in playlist
        if self.is_exited_in_playlist(source_name,video_path):
            return False
        item = {
                "hidden": hidden,
                "selected": selected,
                "value": video_path
        }
        input_settings.get('playlist').append(item)
        # self.printJsonObject(input_settings.get('playlist'))
        # update playlist
        self.request_client.set_input_settings(name = source_name, settings = input_settings,overlay = True)
        return True
    
    
    def remove_a_video_in_playlist(self, source_name, video_path):
        """
        Remove an video in playlist

        Args:
            source_name (String): name of source which you want to remove an video in playlist
            video_path (String): path of video you want to remove

        Returns:
            Bool: true if remove success, false if not
        """
        # load input_settings of source_name
        response = self.get_input_settings(source_name)
        input_settings_playlist = response.input_settings.get('playlist')
        # return false because playlist is empty: 
        if len(input_settings_playlist) == 0:
            return False
        
        # remove item playlist
        new_playlist = [item for item in  input_settings_playlist if item.get('value') != video_path]
        # update playlist
        if len(new_playlist) == len(input_settings_playlist):
            return False
        
        new_input_settings = {
            "playlist" : new_playlist
        }
        self.request_client.set_input_settings(name = source_name, settings =  new_input_settings ,overlay = True)
        return True
    
    def set_stream_service_key_server(self,streamkey,server):
        """
        Set stream key an server to obs websocket

        Args:
            streamkey (String): streamkey of rtmp protocol
            server (String): server name domain or ip
        """
        stream_service_type = "rtmp_custom"
        stream_service_settings = {
            "bwtest": False,
            "key": streamkey,
            "protocol": "RTMP",
            "server": server,
            "use_auth": False
        }
        self.set_stream_service_settings(stream_service_type,stream_service_settings)
    
    
    def set_input_playlist (self, video_path_list, source_name="mySource"):
        """
        Set video list to playlist 
        

        Args:
            video_path_list (_type_): _description_
        """
        playlist = []
        for idx,video in enumerate(video_path_list):
            item = {
                "hidden": False,
                "selected": True if idx == 0 else False,
                "value": video
            }
            print("11111")
            playlist.append(item)
            print("222222")
            
        settings = {
            "playback_behavior": "stop_restart",
            "playlist": playlist,
            "shuffle": False
        }
        
        self.set_input_settings(name=source_name, settings=settings, overlay= False )
        
                    
    def set_current_program_scene(self,scene_name):
            self.request_client.set_current_program_scene(scene_name)
        

def main():
    # stream_key = "live_1044211682_Ol34MomAqRm3Ef7s0jwrKq0KNGj3Ku"
    # server = "rtmp://live.twitch.tv/app"
    # my_obs.get_input_list()
    # my_obs.get_input_settings("mySource")
    # my_obs.get_scene_item_list('scene1')
    
    # my_obs.set_stream_service_key_server(streamkey=stream_key,server=server)
    # my_obs.start_stream()
    # my_obs.get_stream_service_settings()
    # my_obs.get_input_settings(name="mySource")
    # my_obs.add_video_to_playlist("mySource","C:/Users/NHAN/OneDrive/Desktop/workspace/CMS/mp4_videos/ship.mp4")
    # my_obs.remove_a_video_in_playlist("mySource","C:/Users/NHAN/OneDrive/Desktop/workspace/CMS/mp4_videos/ship.mp4")
    # while True:
    #     try: 
    #         time.sleep(1)
    #     except KeyboardInterrupt:
    #         my_obs.stop_stream()
    #         break
    pass
    
     
def test_for_failed_streamkey():
    my_obs1 = OBS_controller(port=5454,password="123456")
    my_obs1.create_scene("VTV3")

    try:
        my_obs1.create_scene("VTV3")
    except OBSSDKRequestError as e:
        if "A source already exists by that scene name" in str(e):
            print("VTV3 already created")
        else:
            print(f"An error occurred: {e}")
    


if __name__ == "__main__":
    try:
        test_for_failed_streamkey()
    except Exception as e:
        print(f"An unexpected error occurred in the main block: {e}")

    while(1):
        print("hahahha")
        time.sleep(1)
