import obsws_python as obs
import json
import time
class OBS_controller:
    
    def printJsonObject(self,object):
        print(json.dumps(object,indent=3))
        
        
    def printJsonObjectList(self,object_list):
        for object in object_list:
            self.printJsonObject(object)
            
    def __init__(self, host='localhost', port=4444, password='123456') -> None:
        self.host = host
        self.port = port
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



    def get_stream_service_settings(self):
        """
        Gets the current stream service settings (stream destination)

        Returns:
            object:
            - attr:
                + stream_service_type (String): Stream service type, like rtmp_custom or rtmp_common
                + stream_service_settings(Object): Stream service settings
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
            streamkey (_type_): _description_
            server (_type_): _description_
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
            playlist.append(item)
            
        settings = {
            "playback_behavior": "stop_restart",
            "playlist": playlist,
            "shuffle": False
        }
        
        self.set_input_settings(name=source_name, settings=settings, overlay= False )
        
                    
        

def main():
    # my_obs = OBS_controller()
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
    
if __name__ == "__main__":
    main()
        