import obsws_python as obs
from stupidArtnet import StupidArtnetServer
from OBSItem import OBSItem
from Ticker import Ticker
from time import sleep


class DMXReceiver():
    
    def __init__(self,universe,address,ticker:Ticker,OBS:OBSItem,Client:obs.ReqClient):
        

        #self.__UniCompr=universe
        #self.__Universe=self.UnivDecompress(universe)
        #self.__Addr=address-1
        self.__OBS=OBS
        self.__Artnet=StupidArtnetServer()
        #self.__Listener=self.__Artnet.register_listener(universe=self.__Universe[0],sub=self.__Universe[1],net=self.__Universe[2], callback_function=self.DMXtoOBS,is_simplified=False)
        self.__Ticker=ticker
        self.__Pause=False
        self.__ListeCount=0
        self.__Check=False
        self.__Client=Client
        self.__collection=None
        self.__profile=None
        self.__scene=None
        self.__sctransition=None
        self.__sctradur=None
        self.__sctransitionduration=50
        self.__AlignType={"TopLeft":5,"TopCenter":4,"TopRight":6,"CenterLeft":1,"Center":0,"CenterRight":2,"BtmLeft":9,"BtmCenter":8,"BtmRight":10}
        #self.__OBS.GetScenefromCollSelected(self.__OBS.CurrentCollection)
        self.__ListenerList={}
        #self.Add_Listener()
        
        
        #self.__Ticker.add_callback(self.callback)
        
        
    #Get Universe/SubNet/Net from Single universe value
    def UnivDecompress(self,valueuniv):
        UnivSubNet=[0,0,0]
        net=int(((valueuniv-1)/2)//128)
        subnet=((valueuniv-1)//16)-(16*net)
        UnivSubNet[0]=((valueuniv-1)-(16*subnet)-(256*net))
        UnivSubNet[1]=subnet
        UnivSubNet[2]=net
        return UnivSubNet

    #Set Universe/SubNet/Net to Single universe value
    def UnivCompress(self,valueunivsubnet):
        UnivSubNet=valueunivsubnet
        net=256*(UnivSubNet[2])
        subnet=16*(UnivSubNet[1])
        value=((UnivSubNet[0]+1)+subnet+net)
        return value
            
    def Add_Listener(self):
        self.__Universe=self.UnivDecompress(self.__OBS.UnivGeneral)
        self.__Listener=self.__Artnet.register_listener(universe=self.__Universe[0],sub=self.__Universe[1],net=self.__Universe[2], callback_function=self.DMXtoOBS,is_simplified=False)
        self.__ListenerList[self.__OBS.UnivGeneral]=self.__Listener
        
        
        for UL in self.__OBS.SourceUniverse:
            if not (UL==self.__OBS.UnivGeneral):
                univsubnet=self.UnivDecompress(UL)
                listener=self.__Artnet.register_listener(universe=univsubnet[0],sub=univsubnet[1],net=univsubnet[2],is_simplified=False)
                self.__ListenerList[UL]=listener

        self.__Ticker.add_callback(self.callback)         
          
    def Remove_Listener(self):
        
        self.__Artnet.delete_listener(self.__Listener)
        for UL in self.__OBS.SourceUniverse:
            if not (UL==self.__OBS.UnivGeneral):
                self.__Artnet.delete_listener(self.__ListenerList[UL])
        self.__ListenerList={}       
        self.__ListeCount=0
        self.__Check=False
        
               
    def Pause(self):
        self.__Pause=True
        self.Remove_Listener()
        
        #éself.__Ticker.remove_callback(self.callback)

    def Start(self):
        #self.__Ticker.add_callback(self.callback)
        self.Add_Listener()
        self.__Pause=False

    def UpdateOBS(self,OBS:OBSItem):
        self.__OBS=OBS       
        
        #self.__Ticker.add_callback(self.callback)           

    def callback(self):
        #self.__Artnet.get_buffer(self.__Listener)
        
        #Check buffer>0 of Universe used before send to source value
        if self.__Check==False:
            for LisLi in self.__ListenerList:
                if len(self.__Artnet.get_buffer(self.__ListenerList[LisLi]))>0:
                    self.__ListeCount+=1
                if self.__ListeCount==len(self.__ListenerList):
                    self.__Check=True
                    self.__Ticker.remove_callback(self.callback)


    def stop(self):
        #self.__Ticker.remove_callback(self.callback)
        #self.__Artnet.delete_listener(self.__Listener)
        pass

    def mapvalue(self,value, fromLow, fromHigh, toLow, toHigh):
        return (value - fromLow) * (toHigh - toLow) / (fromHigh - fromLow) + toLow
    
    #Setting Artnet value to General and Source
    def DMXtoOBS(self,data):   
        if self.__Pause==False and self.__Check:    
            #General Device 
            #print(self.__OBS.UnivGeneral,self.__OBS.AddrGeneral)
            #print(data[self.__OBS.AddrGeneral-1],data[self.__OBS.AddrGeneral],data[self.__OBS.AddrGeneral+1],data[self.__OBS.AddrGeneral+2],data[self.__OBS.AddrGeneral+3])
            if (data[self.__OBS.AddrGeneral-1]<=len(self.__OBS.Profiles)) and (data[self.__OBS.AddrGeneral-1]!=self.__profile) and data[self.__OBS.AddrGeneral-1]>0:
                self.__Client.set_current_profile(self.__OBS.Profiles[data[self.__OBS.AddrGeneral-1]-1])
                self.__profile=data[self.__OBS.AddrGeneral-1]

            if (data[self.__OBS.AddrGeneral]<=len(self.__OBS.Collections)) and (data[self.__OBS.AddrGeneral]!=self.__collection) and data[self.__OBS.AddrGeneral]>0:
                self.__Client.set_current_scene_collection(self.__OBS.Collections[data[self.__OBS.AddrGeneral]-1])
                self.__OBS.CurrentCollection=self.__OBS.Collections[data[self.__OBS.AddrGeneral]-1]
                self.Remove_Listener()
                self.__OBS.GetScenefromCollSelected(self.__OBS.Collections[data[self.__OBS.AddrGeneral]-1])
                self.Add_Listener()
                self.__scene=None
                self.__collection=data[self.__OBS.AddrGeneral] 

            if (data[self.__OBS.AddrGeneral+1]<=len(self.__OBS.ScenesSel)) and (data[self.__OBS.AddrGeneral+1]!=self.__scene):
                if data[self.__OBS.AddrGeneral+1]==0:
                    self.__Client.set_current_program_scene(self.__OBS.ScenesSel[0]["sceneName"])
                    self.__OBS.ActiveScene=self.__OBS.ScenesSel[0]["sceneName"]
                    self.__scene=data[self.__OBS.AddrGeneral+1]    
                    self.__sctransition=None
                    self.__sctradur=None
                else:    
                    self.__Client.set_current_program_scene(self.__OBS.ScenesSel[data[self.__OBS.AddrGeneral+1]-1]["sceneName"])
                    self.__OBS.ActiveScene=self.__OBS.ScenesSel[data[self.__OBS.AddrGeneral+1]-1]["sceneName"]
                    self.__scene=data[self.__OBS.AddrGeneral+1]    
                    self.__sctransition=None
                    self.__sctradur=None

            if (data[self.__OBS.AddrGeneral+2]<=len(self.__OBS.SceneTransitions)) and (data[self.__OBS.AddrGeneral+2]!=self.__sctransition):
                self.__Client.set_current_scene_transition(self.__OBS.SceneTransitions[data[self.__OBS.AddrGeneral+2]-1]["transitionName"])
                self.__sctransition=data[self.__OBS.AddrGeneral+2]    

            if data[self.__OBS.AddrGeneral+3]!=self.__sctradur:
                self.__sctransitionduration=self.mapvalue(data[self.__OBS.AddrGeneral+3],0,255,50,20000)
                self.__Client.set_current_scene_transition_duration(self.__sctransitionduration)
                self.__sctradur=data[self.__OBS.AddrGeneral+3]

            #print(data[self.__Addr+2],len(self.__OBS.ScenesSel),self.__Check)
            #Source device
            #if (data[self.__Addr+2]<=len(self.__OBS.ScenesSel)) and self.__Check:
            if data[self.__OBS.AddrGeneral+1]==0:
                scenesel=1
            else:
                scenesel=data[self.__OBS.AddrGeneral+1]    
            if (scenesel<=len(self.__OBS.ScenesSel)):    
                for source in self.__OBS.ScenesSel[scenesel-1]["Sources"]:
                    if source["ArtnetEnable"]:
                            
                        if source["Univ"]==self.__OBS.UnivGeneral:
                            if data[source["Addr"]-1]!=source["EnaDis"]:
                                if data[source["Addr"]-1]==0:
                                    self.__Client.set_scene_item_enabled(self.__OBS.ActiveScene,source["sceneItemId"],False)
                                    source["EnaDis"]=0
                                if data[source["Addr"]-1]==255:    
                                    self.__Client.set_scene_item_enabled(self.__OBS.ActiveScene,source["sceneItemId"],True)
                                    source["EnaDis"]=255
                            
                            if data[source["Addr"]]!=source["MoveUp"]:
                                if data[source["Addr"]]==255:
                                    self.__Client.set_scene_item_index(self.__OBS.ActiveScene,source["sceneItemId"],source["sceneItemIndex"]+1)
                                    source["MoveUp"]=255
                                if data[source["Addr"]]==0:
                                    source["MoveUp"]=0    
                            
                            if data[source["Addr"]+1]!=source["MoveDown"]:
                                if data[source["Addr"]+1]==255:
                                    value=source["sceneItemIndex"]-1
                                    if value<0:
                                        value=0
                                    self.__Client.set_scene_item_index(self.__OBS.ActiveScene,source["sceneItemId"],value)
                                    source["MoveDown"]=255
                                if data[source["Addr"]+1]==0:
                                    source["MoveDown"]=0    
                            
                            if data[source["Addr"]+2]!=source["Alignment"]:
                                if data[source["Addr"]+2]<=27:
                                    source["sceneItemTransform"]["alignment"]=self.__AlignType["TopLeft"]
                                    self.__Client.set_scene_item_transform(self.__OBS.ActiveScene,source["sceneItemId"],source["sceneItemTransform"])
                                if data[source["Addr"]+2]>27 and data[source["Addr"]+2]<=55:
                                    source["sceneItemTransform"]["alignment"]=self.__AlignType["TopCenter"]
                                    self.__Client.set_scene_item_transform(self.__OBS.ActiveScene,source["sceneItemId"],source["sceneItemTransform"])
                                if data[source["Addr"]+2]>55 and data[source["Addr"]+2]<=83:
                                    source["sceneItemTransform"]["alignment"]=self.__AlignType["TopRight"]
                                    self.__Client.set_scene_item_transform(self.__OBS.ActiveScene,source["sceneItemId"],source["sceneItemTransform"])
                                if data[source["Addr"]+2]>83 and data[source["Addr"]+2]<=111:
                                    source["sceneItemTransform"]["alignment"]=self.__AlignType["CenterLeft"]
                                    self.__Client.set_scene_item_transform(self.__OBS.ActiveScene,source["sceneItemId"],source["sceneItemTransform"])
                                if data[source["Addr"]+2]>111 and data[source["Addr"]+2]<=139:
                                    source["sceneItemTransform"]["alignment"]=self.__AlignType["Center"]
                                    self.__Client.set_scene_item_transform(self.__OBS.ActiveScene,source["sceneItemId"],source["sceneItemTransform"])
                                if data[source["Addr"]+2]>139 and data[source["Addr"]+2]<=167:
                                    source["sceneItemTransform"]["alignment"]=self.__AlignType["CenterRight"]
                                    self.__Client.set_scene_item_transform(self.__OBS.ActiveScene,source["sceneItemId"],source["sceneItemTransform"])
                                if data[source["Addr"]+2]>167 and data[source["Addr"]+2]<=195:
                                    source["sceneItemTransform"]["alignment"]=self.__AlignType["BtmLeft"]
                                    self.__Client.set_scene_item_transform(self.__OBS.ActiveScene,source["sceneItemId"],source["sceneItemTransform"])
                                if data[source["Addr"]+2]>195 and data[source["Addr"]+2]<=223:
                                    source["sceneItemTransform"]["alignment"]=self.__AlignType["BtmCenter"]
                                    self.__Client.set_scene_item_transform(self.__OBS.ActiveScene,source["sceneItemId"],source["sceneItemTransform"])
                                if data[source["Addr"]+2]>223:
                                    source["sceneItemTransform"]["alignment"]=self.__AlignType["BtmRight"]
                                    self.__Client.set_scene_item_transform(self.__OBS.ActiveScene,source["sceneItemId"],source["sceneItemTransform"])                            
                                source["Alignment"]=data[source["Addr"]+2]    
                            
                            if data[source["Addr"]+3]!=source["BoundsAlignment"]:
                                if data[source["Addr"]+3]<=27:
                                    source["sceneItemTransform"]["boundsAlignment"]=self.__AlignType["TopLeft"]
                                    self.__Client.set_scene_item_transform(self.__OBS.ActiveScene,source["sceneItemId"],source["sceneItemTransform"])
                                if data[source["Addr"]+3]>27 and data[source["Addr"]+3]<=55:
                                    source["sceneItemTransform"]["boundsAlignment"]=self.__AlignType["TopCenter"]
                                    self.__Client.set_scene_item_transform(self.__OBS.ActiveScene,source["sceneItemId"],source["sceneItemTransform"])
                                if data[source["Addr"]+3]>55 and data[source["Addr"]+3]<=83:
                                    source["sceneItemTransform"]["boundsAlignment"]=self.__AlignType["TopRight"]
                                    self.__Client.set_scene_item_transform(self.__OBS.ActiveScene,source["sceneItemId"],source["sceneItemTransform"])
                                if data[source["Addr"]+3]>83 and data[source["Addr"]+3]<=111:
                                    source["sceneItemTransform"]["boundsAlignment"]=self.__AlignType["CenterLeft"]
                                    self.__Client.set_scene_item_transform(self.__OBS.ActiveScene,source["sceneItemId"],source["sceneItemTransform"])
                                if data[source["Addr"]+3]>111 and data[source["Addr"]+3]<=139:
                                    source["sceneItemTransform"]["boundsAlignment"]=self.__AlignType["Center"]
                                    self.__Client.set_scene_item_transform(self.__OBS.ActiveScene,source["sceneItemId"],source["sceneItemTransform"])
                                if data[source["Addr"]+3]>139 and data[source["Addr"]+3]<=167:
                                    source["sceneItemTransform"]["boundsAlignment"]=self.__AlignType["CenterRight"]
                                    self.__Client.set_scene_item_transform(self.__OBS.ActiveScene,source["sceneItemId"],source["sceneItemTransform"])
                                if data[source["Addr"]+3]>167 and data[source["Addr"]+3]<=195:
                                    source["sceneItemTransform"]["boundsAlignment"]=self.__AlignType["BtmLeft"]
                                    self.__Client.set_scene_item_transform(self.__OBS.ActiveScene,source["sceneItemId"],source["sceneItemTransform"])
                                if data[source["Addr"]+3]>195 and data[source["Addr"]+3]<=223:
                                    source["sceneItemTransform"]["boundsAlignment"]=self.__AlignType["BtmCenter"]
                                    self.__Client.set_scene_item_transform(self.__OBS.ActiveScene,source["sceneItemId"],source["sceneItemTransform"])
                                if data[source["Addr"]+3]>223:
                                    source["sceneItemTransform"]["boundsAlignment"]=self.__AlignType["BtmRight"]
                                    self.__Client.set_scene_item_transform(self.__OBS.ActiveScene,source["sceneItemId"],source["sceneItemTransform"])                            
                                source["BoundsAlignment"]=data[source["Addr"]+3]    
                            
                            if data[source["Addr"]+4]!=source["BoundsWidth"]:
                                value=self.mapvalue(data[source["Addr"]+4],0,255,1,4096)
                                source["sceneItemTransform"]["boundsWidth"]=value
                                self.__Client.set_scene_item_transform(self.__OBS.ActiveScene,source["sceneItemId"],source["sceneItemTransform"])                            
                                source["BoundsWidth"]=data[source["Addr"]+4] 
                               
                            if data[source["Addr"]+5]!=source["BoundsHeight"]:
                                value=self.mapvalue(data[source["Addr"]+5],0,255,1,4096)
                                source["sceneItemTransform"]["boundsHeight"]=value
                                self.__Client.set_scene_item_transform(self.__OBS.ActiveScene,source["sceneItemId"],source["sceneItemTransform"])                            
                                source["BoundsHeight"]=data[source["Addr"]+5] 
                            
                            if data[source["Addr"]+6]!=source["BoundsType"]:
                                if data[source["Addr"]+6]<=35:
                                    source["sceneItemTransform"]["boundsType"]="OBS_BOUNDS_NONE"
                                    self.__Client.set_scene_item_transform(self.__OBS.ActiveScene,source["sceneItemId"],source["sceneItemTransform"])
                                if data[source["Addr"]+6]>35 and data[source["Addr"]+6]<=71:
                                    source["sceneItemTransform"]["boundsType"]="OBS_BOUNDS_STRETCH"
                                    self.__Client.set_scene_item_transform(self.__OBS.ActiveScene,source["sceneItemId"],source["sceneItemTransform"])
                                if data[source["Addr"]+6]>71 and data[source["Addr"]+6]<=107:
                                    source["sceneItemTransform"]["boundsType"]="OBS_BOUNDS_SCALE_INNER"
                                    self.__Client.set_scene_item_transform(self.__OBS.ActiveScene,source["sceneItemId"],source["sceneItemTransform"])
                                if data[source["Addr"]+6]>107 and data[source["Addr"]+6]<=143:
                                    source["sceneItemTransform"]["boundsType"]="OBS_BOUNDS_SCALE_OUTER"
                                    self.__Client.set_scene_item_transform(self.__OBS.ActiveScene,source["sceneItemId"],source["sceneItemTransform"])
                                if data[source["Addr"]+6]>143 and data[source["Addr"]+6]<=179:
                                    source["sceneItemTransform"]["boundsType"]="OBS_BOUNDS_SCALE_TO_WIDTH"
                                    self.__Client.set_scene_item_transform(self.__OBS.ActiveScene,source["sceneItemId"],source["sceneItemTransform"])
                                if data[source["Addr"]+6]>179 and data[source["Addr"]+6]<=215:
                                    source["sceneItemTransform"]["boundsType"]="OBS_BOUNDS_SCALE_TO_HEIGHT"
                                    self.__Client.set_scene_item_transform(self.__OBS.ActiveScene,source["sceneItemId"],source["sceneItemTransform"])
                                if data[source["Addr"]+6]>215:
                                    source["sceneItemTransform"]["boundsType"]="OBS_BOUNDS_MAX_ONLY"
                                    self.__Client.set_scene_item_transform(self.__OBS.ActiveScene,source["sceneItemId"],source["sceneItemTransform"])
                                source["BoundsType"]=data[source["Addr"]+6]    
                            
                            if data[source["Addr"]+7]!=source["CropBottom"]:
                                value=self.mapvalue(data[source["Addr"]+7],0,255,0,source["sceneItemTransform"]["sourceHeight"])
                                source["sceneItemTransform"]["cropBottom"]=value
                                self.__Client.set_scene_item_transform(self.__OBS.ActiveScene,source["sceneItemId"],source["sceneItemTransform"])                            
                                source["CropBottom"]=data[source["Addr"]+7] 
                            
                            if data[source["Addr"]+8]!=source["CropLeft"]:
                                value=self.mapvalue(data[source["Addr"]+8],0,255,0,source["sceneItemTransform"]["sourceWidth"])
                                source["sceneItemTransform"]["cropLeft"]=value
                                self.__Client.set_scene_item_transform(self.__OBS.ActiveScene,source["sceneItemId"],source["sceneItemTransform"])                            
                                source["CropLeft"]=data[source["Addr"]+8] 
                            
                            if data[source["Addr"]+9]!=source["CropRight"]:
                                value=self.mapvalue(data[source["Addr"]+9],0,255,0,source["sceneItemTransform"]["sourceWidth"])
                                source["sceneItemTransform"]["cropRight"]=value
                                self.__Client.set_scene_item_transform(self.__OBS.ActiveScene,source["sceneItemId"],source["sceneItemTransform"])                            
                                source["CropRight"]=data[source["Addr"]+9] 
                            
                            if data[source["Addr"]+10]!=source["CropTop"]:
                                value=self.mapvalue(data[source["Addr"]+10],0,255,0,source["sceneItemTransform"]["sourceHeight"])
                                source["sceneItemTransform"]["cropTop"]=value
                                self.__Client.set_scene_item_transform(self.__OBS.ActiveScene,source["sceneItemId"],source["sceneItemTransform"])                            
                                source["CropTop"]=data[source["Addr"]+10] 
                            
                            if data[source["Addr"]+11]!=source["ScaleX"]:
                                value=self.mapvalue(data[source["Addr"]+11],0,255,0,2)
                                source["sceneItemTransform"]["scaleX"]=value
                                self.__Client.set_scene_item_transform(self.__OBS.ActiveScene,source["sceneItemId"],source["sceneItemTransform"])                            
                                source["ScaleX"]=data[source["Addr"]+11] 
                            
                            if data[source["Addr"]+12]!=source["ScaleY"]:
                                value=self.mapvalue(data[source["Addr"]+12],0,255,0,2)
                                source["sceneItemTransform"]["scaleY"]=value
                                self.__Client.set_scene_item_transform(self.__OBS.ActiveScene,source["sceneItemId"],source["sceneItemTransform"])                            
                                source["ScaleY"]=data[source["Addr"]+12] 
                            
                            if data[source["Addr"]+13]!=source["PositionX"]:
                                value=self.mapvalue(data[source["Addr"]+13],0,255,-4096,4096)
                                source["sceneItemTransform"]["positionX"]=value
                                self.__Client.set_scene_item_transform(self.__OBS.ActiveScene,source["sceneItemId"],source["sceneItemTransform"])                            
                                source["PositionX"]=data[source["Addr"]+13] 
                            
                            if data[source["Addr"]+14]!=source["PositionY"]:
                                value=self.mapvalue(data[source["Addr"]+14],0,255,-4096,4096)
                                source["sceneItemTransform"]["positionY"]=value
                                self.__Client.set_scene_item_transform(self.__OBS.ActiveScene,source["sceneItemId"],source["sceneItemTransform"])                            
                                source["PositionY"]=data[source["Addr"]+14] 
                            
                            if data[source["Addr"]+15]!=source["Rotation"]:
                                value=self.mapvalue(data[source["Addr"]+15],0,255,0,360)
                                source["sceneItemTransform"]["rotation"]=value
                                self.__Client.set_scene_item_transform(self.__OBS.ActiveScene,source["sceneItemId"],source["sceneItemTransform"])                            
                                source["Rotation"]=data[source["Addr"]+15] 
                            
                            if data[source["Addr"]+16]!=source["BlendMode"]:
                                if data[source["Addr"]+16]<=35:
                                    source["sceneItemBlendMode"]="OBS_BLEND_NORMAL"
                                    self.__Client.set_scene_item_blend_mode(self.__OBS.ActiveScene,source["sceneItemId"],source["sceneItemBlendMode"])
                                if data[source["Addr"]+16]>35 and data[source["Addr"]+16]<=71:
                                    source["sceneItemBlendMode"]="OBS_BLEND_ADDITIVE"
                                    self.__Client.set_scene_item_blend_mode(self.__OBS.ActiveScene,source["sceneItemId"],source["sceneItemBlendMode"])
                                if data[source["Addr"]+16]>71 and data[source["Addr"]+16]<=107:
                                    source["sceneItemBlendMode"]="OBS_BLEND_SUBTRACT"
                                    self.__Client.set_scene_item_blend_mode(self.__OBS.ActiveScene,source["sceneItemId"],source["sceneItemBlendMode"])
                                if data[source["Addr"]+16]>107 and data[source["Addr"]+16]<=143:
                                    source["sceneItemBlendMode"]="OBS_BLEND_SCREEN"
                                    self.__Client.set_scene_item_blend_mode(self.__OBS.ActiveScene,source["sceneItemId"],source["sceneItemBlendMode"])
                                if data[source["Addr"]+16]>143 and data[source["Addr"]+16]<=179:
                                    source["sceneItemBlendMode"]="OBS_BLEND_MULTIPLY"
                                    self.__Client.set_scene_item_blend_mode(self.__OBS.ActiveScene,source["sceneItemId"],source["sceneItemBlendMode"])
                                if data[source["Addr"]+16]>179 and data[source["Addr"]+16]<=215:
                                    source["sceneItemBlendMode"]="OBS_BLEND_LIGHTEN"
                                    self.__Client.set_scene_item_blend_mode(self.__OBS.ActiveScene,source["sceneItemId"],source["sceneItemBlendMode"])
                                if data[source["Addr"]+16]>215:
                                    source["sceneItemBlendMode"]="OBS_BLEND_DARKEN"
                                    self.__Client.set_scene_item_blend_mode(self.__OBS.ActiveScene,source["sceneItemId"],source["sceneItemBlendMode"])
                                source["BlendMode"]=data[source["Addr"]+16]    
                            
                        else:
                            buffer=self.__Artnet.get_buffer(self.__ListenerList[source["Univ"]])
                            if len(buffer)>0:
                                if buffer[source["Addr"]-1]!=source["EnaDis"]:
                                    if buffer[source["Addr"]-1]==0:
                                        self.__Client.set_scene_item_enabled(self.__OBS.ActiveScene,source["sceneItemId"],False)
                                        source["EnaDis"]=0
                                    if buffer[source["Addr"]-1]==255:    
                                        self.__Client.set_scene_item_enabled(self.__OBS.ActiveScene,source["sceneItemId"],True)
                                        source["EnaDis"]=255
                                
                                if buffer[source["Addr"]]!=source["MoveUp"]:
                                    if buffer[source["Addr"]]==255:
                                        self.__Client.set_scene_item_index(self.__OBS.ActiveScene,source["sceneItemId"],source["sceneItemIndex"]+1)
                                        source["MoveUp"]=255
                                    if buffer[source["Addr"]]==0:
                                        source["MoveUp"]=0    
                                
                                if buffer[source["Addr"]+1]!=source["MoveDown"]:
                                    if buffer[source["Addr"]+1]==255:
                                        value=source["sceneItemIndex"]-1
                                        if value<0:
                                            value=0
                                        self.__Client.set_scene_item_index(self.__OBS.ActiveScene,source["sceneItemId"],value)
                                        source["MoveDown"]=255
                                    if buffer[source["Addr"]+1]==0:
                                        source["MoveDown"]=0    
                                
                                if buffer[source["Addr"]+2]!=source["Alignment"]:
                                    if buffer[source["Addr"]+2]<=27:
                                        source["sceneItemTransform"]["alignment"]=self.__AlignType["TopLeft"]
                                        self.__Client.set_scene_item_transform(self.__OBS.ActiveScene,source["sceneItemId"],source["sceneItemTransform"])
                                    if buffer[source["Addr"]+2]>27 and buffer[source["Addr"]+2]<=55:
                                        source["sceneItemTransform"]["alignment"]=self.__AlignType["TopCenter"]
                                        self.__Client.set_scene_item_transform(self.__OBS.ActiveScene,source["sceneItemId"],source["sceneItemTransform"])
                                    if buffer[source["Addr"]+2]>55 and buffer[source["Addr"]+2]<=83:
                                        source["sceneItemTransform"]["alignment"]=self.__AlignType["TopRight"]
                                        self.__Client.set_scene_item_transform(self.__OBS.ActiveScene,source["sceneItemId"],source["sceneItemTransform"])
                                    if buffer[source["Addr"]+2]>83 and buffer[source["Addr"]+2]<=111:
                                        source["sceneItemTransform"]["alignment"]=self.__AlignType["CenterLeft"]
                                        self.__Client.set_scene_item_transform(self.__OBS.ActiveScene,source["sceneItemId"],source["sceneItemTransform"])
                                    if buffer[source["Addr"]+2]>111 and buffer[source["Addr"]+2]<=139:
                                        source["sceneItemTransform"]["alignment"]=self.__AlignType["Center"]
                                        self.__Client.set_scene_item_transform(self.__OBS.ActiveScene,source["sceneItemId"],source["sceneItemTransform"])
                                    if buffer[source["Addr"]+2]>139 and buffer[source["Addr"]+2]<=167:
                                        source["sceneItemTransform"]["alignment"]=self.__AlignType["CenterRight"]
                                        self.__Client.set_scene_item_transform(self.__OBS.ActiveScene,source["sceneItemId"],source["sceneItemTransform"])
                                    if buffer[source["Addr"]+2]>167 and buffer[source["Addr"]+2]<=195:
                                        source["sceneItemTransform"]["alignment"]=self.__AlignType["BtmLeft"]
                                        self.__Client.set_scene_item_transform(self.__OBS.ActiveScene,source["sceneItemId"],source["sceneItemTransform"])
                                    if buffer[source["Addr"]+2]>195 and buffer[source["Addr"]+2]<=223:
                                        source["sceneItemTransform"]["alignment"]=self.__AlignType["BtmCenter"]
                                        self.__Client.set_scene_item_transform(self.__OBS.ActiveScene,source["sceneItemId"],source["sceneItemTransform"])
                                    if buffer[source["Addr"]+2]>223:
                                        source["sceneItemTransform"]["alignment"]=self.__AlignType["BtmRight"]
                                        self.__Client.set_scene_item_transform(self.__OBS.ActiveScene,source["sceneItemId"],source["sceneItemTransform"])                            
                                    source["Alignment"]=buffer[source["Addr"]+2]    
                                
                                if buffer[source["Addr"]+3]!=source["BoundsAlignment"]:
                                    if buffer[source["Addr"]+3]<=27:
                                        source["sceneItemTransform"]["boundsAlignment"]=self.__AlignType["TopLeft"]
                                        self.__Client.set_scene_item_transform(self.__OBS.ActiveScene,source["sceneItemId"],source["sceneItemTransform"])
                                    if buffer[source["Addr"]+3]>27 and buffer[source["Addr"]+3]<=55:
                                        source["sceneItemTransform"]["boundsAlignment"]=self.__AlignType["TopCenter"]
                                        self.__Client.set_scene_item_transform(self.__OBS.ActiveScene,source["sceneItemId"],source["sceneItemTransform"])
                                    if buffer[source["Addr"]+3]>55 and buffer[source["Addr"]+3]<=83:
                                        source["sceneItemTransform"]["boundsAlignment"]=self.__AlignType["TopRight"]
                                        self.__Client.set_scene_item_transform(self.__OBS.ActiveScene,source["sceneItemId"],source["sceneItemTransform"])
                                    if buffer[source["Addr"]+3]>83 and buffer[source["Addr"]+3]<=111:
                                        source["sceneItemTransform"]["boundsAlignment"]=self.__AlignType["CenterLeft"]
                                        self.__Client.set_scene_item_transform(self.__OBS.ActiveScene,source["sceneItemId"],source["sceneItemTransform"])
                                    if buffer[source["Addr"]+3]>111 and buffer[source["Addr"]+3]<=139:
                                        source["sceneItemTransform"]["boundsAlignment"]=self.__AlignType["Center"]
                                        self.__Client.set_scene_item_transform(self.__OBS.ActiveScene,source["sceneItemId"],source["sceneItemTransform"])
                                    if buffer[source["Addr"]+3]>139 and buffer[source["Addr"]+3]<=167:
                                        source["sceneItemTransform"]["boundsAlignment"]=self.__AlignType["CenterRight"]
                                        self.__Client.set_scene_item_transform(self.__OBS.ActiveScene,source["sceneItemId"],source["sceneItemTransform"])
                                    if buffer[source["Addr"]+3]>167 and buffer[source["Addr"]+3]<=195:
                                        source["sceneItemTransform"]["boundsAlignment"]=self.__AlignType["BtmLeft"]
                                        self.__Client.set_scene_item_transform(self.__OBS.ActiveScene,source["sceneItemId"],source["sceneItemTransform"])
                                    if buffer[source["Addr"]+3]>195 and buffer[source["Addr"]+3]<=223:
                                        source["sceneItemTransform"]["boundsAlignment"]=self.__AlignType["BtmCenter"]
                                        self.__Client.set_scene_item_transform(self.__OBS.ActiveScene,source["sceneItemId"],source["sceneItemTransform"])
                                    if buffer[source["Addr"]+3]>223:
                                        source["sceneItemTransform"]["boundsAlignment"]=self.__AlignType["BtmRight"]
                                        self.__Client.set_scene_item_transform(self.__OBS.ActiveScene,source["sceneItemId"],source["sceneItemTransform"])                            
                                    source["BoundsAlignment"]=buffer[source["Addr"]+3]    
                                
                                if buffer[source["Addr"]+4]!=source["BoundsWidth"]:
                                    value=self.mapvalue(buffer[source["Addr"]+4],0,255,1,4096)
                                    source["sceneItemTransform"]["boundsWidth"]=value
                                    self.__Client.set_scene_item_transform(self.__OBS.ActiveScene,source["sceneItemId"],source["sceneItemTransform"])                            
                                    source["BoundsWidth"]=buffer[source["Addr"]+4] 
                                    
                                if buffer[source["Addr"]+5]!=source["BoundsHeight"]:
                                    value=self.mapvalue(buffer[source["Addr"]+5],0,255,1,4096)
                                    source["sceneItemTransform"]["boundsHeight"]=value
                                    self.__Client.set_scene_item_transform(self.__OBS.ActiveScene,source["sceneItemId"],source["sceneItemTransform"])                            
                                    source["BoundsHeight"]=buffer[source["Addr"]+5] 
                                
                                if buffer[source["Addr"]+6]!=source["BoundsType"]:
                                    if buffer[source["Addr"]+6]<=35:
                                        source["sceneItemTransform"]["boundsType"]="OBS_BOUNDS_NONE"
                                        self.__Client.set_scene_item_transform(self.__OBS.ActiveScene,source["sceneItemId"],source["sceneItemTransform"])
                                    if buffer[source["Addr"]+6]>35 and buffer[source["Addr"]+6]<=71:
                                        source["sceneItemTransform"]["boundsType"]="OBS_BOUNDS_STRETCH"
                                        self.__Client.set_scene_item_transform(self.__OBS.ActiveScene,source["sceneItemId"],source["sceneItemTransform"])
                                    if buffer[source["Addr"]+6]>71 and buffer[source["Addr"]+6]<=107:
                                        source["sceneItemTransform"]["boundsType"]="OBS_BOUNDS_SCALE_INNER"
                                        self.__Client.set_scene_item_transform(self.__OBS.ActiveScene,source["sceneItemId"],source["sceneItemTransform"])
                                    if buffer[source["Addr"]+6]>107 and buffer[source["Addr"]+6]<=143:
                                        source["sceneItemTransform"]["boundsType"]="OBS_BOUNDS_SCALE_OUTER"
                                        self.__Client.set_scene_item_transform(self.__OBS.ActiveScene,source["sceneItemId"],source["sceneItemTransform"])
                                    if buffer[source["Addr"]+6]>143 and buffer[source["Addr"]+6]<=179:
                                        source["sceneItemTransform"]["boundsType"]="OBS_BOUNDS_SCALE_TO_WIDTH"
                                        self.__Client.set_scene_item_transform(self.__OBS.ActiveScene,source["sceneItemId"],source["sceneItemTransform"])
                                    if buffer[source["Addr"]+6]>179 and buffer[source["Addr"]+6]<=215:
                                        source["sceneItemTransform"]["boundsType"]="OBS_BOUNDS_SCALE_TO_HEIGHT"
                                        self.__Client.set_scene_item_transform(self.__OBS.ActiveScene,source["sceneItemId"],source["sceneItemTransform"])
                                    if buffer[source["Addr"]+6]>215:
                                        source["sceneItemTransform"]["boundsType"]="OBS_BOUNDS_MAX_ONLY"
                                        self.__Client.set_scene_item_transform(self.__OBS.ActiveScene,source["sceneItemId"],source["sceneItemTransform"])
                                    source["BoundsType"]=buffer[source["Addr"]+6]    
                               
                                if buffer[source["Addr"]+7]!=source["CropBottom"]:
                                    value=self.mapvalue(buffer[source["Addr"]+7],0,255,0,source["sceneItemTransform"]["sourceHeight"])
                                    source["sceneItemTransform"]["cropBottom"]=value
                                    self.__Client.set_scene_item_transform(self.__OBS.ActiveScene,source["sceneItemId"],source["sceneItemTransform"])                            
                                    source["CropBottom"]=buffer[source["Addr"]+7] 
                                
                                if buffer[source["Addr"]+8]!=source["CropLeft"]:
                                    value=self.mapvalue(buffer[source["Addr"]+8],0,255,0,source["sceneItemTransform"]["sourceWidth"])
                                    source["sceneItemTransform"]["cropLeft"]=value
                                    self.__Client.set_scene_item_transform(self.__OBS.ActiveScene,source["sceneItemId"],source["sceneItemTransform"])                            
                                    source["CropLeft"]=buffer[source["Addr"]+8] 
                                
                                if buffer[source["Addr"]+9]!=source["CropRight"]:
                                    value=self.mapvalue(buffer[source["Addr"]+9],0,255,0,source["sceneItemTransform"]["sourceWidth"])
                                    source["sceneItemTransform"]["cropRight"]=value
                                    self.__Client.set_scene_item_transform(self.__OBS.ActiveScene,source["sceneItemId"],source["sceneItemTransform"])                            
                                    source["CropRight"]=buffer[source["Addr"]+9] 
                                
                                if buffer[source["Addr"]+10]!=source["CropTop"]:
                                    value=self.mapvalue(buffer[source["Addr"]+10],0,255,0,source["sceneItemTransform"]["sourceHeight"])
                                    source["sceneItemTransform"]["cropTop"]=value
                                    self.__Client.set_scene_item_transform(self.__OBS.ActiveScene,source["sceneItemId"],source["sceneItemTransform"])                            
                                    source["CropTop"]=buffer[source["Addr"]+10] 
                                
                                if buffer[source["Addr"]+11]!=source["ScaleX"]:
                                    value=self.mapvalue(buffer[source["Addr"]+11],0,255,0,2)
                                    source["sceneItemTransform"]["scaleX"]=value
                                    self.__Client.set_scene_item_transform(self.__OBS.ActiveScene,source["sceneItemId"],source["sceneItemTransform"])                            
                                    source["ScaleX"]=buffer[source["Addr"]+11] 
                                
                                if buffer[source["Addr"]+12]!=source["ScaleY"]:
                                    value=self.mapvalue(buffer[source["Addr"]+12],0,255,0,2)
                                    source["sceneItemTransform"]["scaleY"]=value
                                    self.__Client.set_scene_item_transform(self.__OBS.ActiveScene,source["sceneItemId"],source["sceneItemTransform"])                            
                                    source["ScaleY"]=buffer[source["Addr"]+12] 
                                
                                if buffer[source["Addr"]+13]!=source["PositionX"]:
                                    value=self.mapvalue(buffer[source["Addr"]+13],0,255,-4096,4096)
                                    source["sceneItemTransform"]["positionX"]=value
                                    self.__Client.set_scene_item_transform(self.__OBS.ActiveScene,source["sceneItemId"],source["sceneItemTransform"])                            
                                    source["PositionX"]=buffer[source["Addr"]+13] 
                                
                                if buffer[source["Addr"]+14]!=source["PositionY"]:
                                    value=self.mapvalue(buffer[source["Addr"]+14],0,255,-4096,4096)
                                    source["sceneItemTransform"]["positionY"]=value
                                    self.__Client.set_scene_item_transform(self.__OBS.ActiveScene,source["sceneItemId"],source["sceneItemTransform"])                            
                                    source["PositionY"]=buffer[source["Addr"]+14] 
                                
                                if buffer[source["Addr"]+15]!=source["Rotation"]:
                                    value=self.mapvalue(buffer[source["Addr"]+15],0,255,0,360)
                                    source["sceneItemTransform"]["rotation"]=value
                                    self.__Client.set_scene_item_transform(self.__OBS.ActiveScene,source["sceneItemId"],source["sceneItemTransform"])                            
                                    source["Rotation"]=buffer[source["Addr"]+15] 
                                
                                if buffer[source["Addr"]+16]!=source["BlendMode"]:
                                    if buffer[source["Addr"]+16]<=35:
                                        source["sceneItemBlendMode"]="OBS_BLEND_NORMAL"
                                        self.__Client.set_scene_item_blend_mode(self.__OBS.ActiveScene,source["sceneItemId"],source["sceneItemBlendMode"])
                                    if buffer[source["Addr"]+16]>35 and buffer[source["Addr"]+16]<=71:
                                        source["sceneItemBlendMode"]="OBS_BLEND_ADDITIVE"
                                        self.__Client.set_scene_item_blend_mode(self.__OBS.ActiveScene,source["sceneItemId"],source["sceneItemBlendMode"])
                                    if buffer[source["Addr"]+16]>71 and buffer[source["Addr"]+16]<=107:
                                        source["sceneItemBlendMode"]="OBS_BLEND_SUBTRACT"
                                        self.__Client.set_scene_item_blend_mode(self.__OBS.ActiveScene,source["sceneItemId"],source["sceneItemBlendMode"])
                                    if buffer[source["Addr"]+16]>107 and buffer[source["Addr"]+16]<=143:
                                        source["sceneItemBlendMode"]="OBS_BLEND_SCREEN"
                                        self.__Client.set_scene_item_blend_mode(self.__OBS.ActiveScene,source["sceneItemId"],source["sceneItemBlendMode"])
                                    if buffer[source["Addr"]+16]>143 and buffer[source["Addr"]+16]<=179:
                                        source["sceneItemBlendMode"]="OBS_BLEND_MULTIPLY"
                                        self.__Client.set_scene_item_blend_mode(self.__OBS.ActiveScene,source["sceneItemId"],source["sceneItemBlendMode"])
                                    if buffer[source["Addr"]+16]>179 and buffer[source["Addr"]+16]<=215:
                                        source["sceneItemBlendMode"]="OBS_BLEND_LIGHTEN"
                                        self.__Client.set_scene_item_blend_mode(self.__OBS.ActiveScene,source["sceneItemId"],source["sceneItemBlendMode"])
                                    if buffer[source["Addr"]+16]>215:
                                        source["sceneItemBlendMode"]="OBS_BLEND_DARKEN"
                                        self.__Client.set_scene_item_blend_mode(self.__OBS.ActiveScene,source["sceneItemId"],source["sceneItemBlendMode"])
                                    source["BlendMode"]=buffer[source["Addr"]+16]    
                                

                    if source["isGroup"]:
                        for sourcegroup in source["Sources"]:
                            if sourcegroup["ArtnetEnable"]:
                                if sourcegroup["Univ"]==self.__OBS.UnivGeneral:
                                    if data[sourcegroup["Addr"]-1]!=sourcegroup["EnaDis"]:
                                        if data[sourcegroup["Addr"]-1]==0:
                                            self.__Client.set_scene_item_enabled(source["sourceName"],sourcegroup["sceneItemId"],False)
                                            sourcegroup["EnaDis"]=0
                                        if data[sourcegroup["Addr"]-1]==255:    
                                            self.__Client.set_scene_item_enabled(source["sourceName"],sourcegroup["sceneItemId"],True)
                                            sourcegroup["EnaDis"]=255
                                    
                                    if data[sourcegroup["Addr"]]!=sourcegroup["MoveUp"]:
                                        if data[sourcegroup["Addr"]]==255:
                                            self.__Client.set_scene_item_index(source["sourceName"],sourcegroup["sceneItemId"],sourcegroup["sceneItemIndex"]+1)
                                            sourcegroup["MoveUp"]=255
                                        if data[sourcegroup["Addr"]]==0:
                                            sourcegroup["MoveUp"]=0    
                                    
                                    if data[sourcegroup["Addr"]+1]!=sourcegroup["MoveDown"]:
                                        if data[sourcegroup["Addr"]+1]==255:
                                            value=sourcegroup["sceneItemIndex"]-1
                                            if value<0:
                                                value=0
                                            self.__Client.set_scene_item_index(source["sourceName"],sourcegroup["sceneItemId"],value)
                                            sourcegroup["MoveDown"]=255
                                        if data[sourcegroup["Addr"]+1]==0:
                                            sourcegroup["MoveDown"]=0    
                                    
                                    if data[sourcegroup["Addr"]+2]!=sourcegroup["Alignment"]:
                                        if data[sourcegroup["Addr"]+2]<=27:
                                            sourcegroup["sceneItemTransform"]["alignment"]=self.__AlignType["TopLeft"]
                                            self.__Client.set_scene_item_transform(source["sourceName"],sourcegroup["sceneItemId"],sourcegroup["sceneItemTransform"])
                                        if data[sourcegroup["Addr"]+2]>27 and data[sourcegroup["Addr"]+2]<=55:
                                            sourcegroup["sceneItemTransform"]["alignment"]=self.__AlignType["TopCenter"]
                                            self.__Client.set_scene_item_transform(source["sourceName"],sourcegroup["sceneItemId"],sourcegroup["sceneItemTransform"])
                                        if data[sourcegroup["Addr"]+2]>55 and data[sourcegroup["Addr"]+2]<=83:
                                            sourcegroup["sceneItemTransform"]["alignment"]=self.__AlignType["TopRight"]
                                            self.__Client.set_scene_item_transform(source["sourceName"],sourcegroup["sceneItemId"],sourcegroup["sceneItemTransform"])
                                        if data[sourcegroup["Addr"]+2]>83 and data[sourcegroup["Addr"]+2]<=111:
                                            sourcegroup["sceneItemTransform"]["alignment"]=self.__AlignType["CenterLeft"]
                                            self.__Client.set_scene_item_transform(source["sourceName"],sourcegroup["sceneItemId"],sourcegroup["sceneItemTransform"])
                                        if data[sourcegroup["Addr"]+2]>111 and data[sourcegroup["Addr"]+2]<=139:
                                            sourcegroup["sceneItemTransform"]["alignment"]=self.__AlignType["Center"]
                                            self.__Client.set_scene_item_transform(source["sourceName"],sourcegroup["sceneItemId"],sourcegroup["sceneItemTransform"])
                                        if data[sourcegroup["Addr"]+2]>139 and data[sourcegroup["Addr"]+2]<=167:
                                            sourcegroup["sceneItemTransform"]["alignment"]=self.__AlignType["CenterRight"]
                                            self.__Client.set_scene_item_transform(source["sourceName"],sourcegroup["sceneItemId"],sourcegroup["sceneItemTransform"])
                                        if data[sourcegroup["Addr"]+2]>167 and data[sourcegroup["Addr"]+2]<=195:
                                            sourcegroup["sceneItemTransform"]["alignment"]=self.__AlignType["BtmLeft"]
                                            self.__Client.set_scene_item_transform(source["sourceName"],sourcegroup["sceneItemId"],sourcegroup["sceneItemTransform"])
                                        if data[sourcegroup["Addr"]+2]>195 and data[sourcegroup["Addr"]+2]<=223:
                                            sourcegroup["sceneItemTransform"]["alignment"]=self.__AlignType["BtmCenter"]
                                            self.__Client.set_scene_item_transform(source["sourceName"],sourcegroup["sceneItemId"],sourcegroup["sceneItemTransform"])
                                        if data[sourcegroup["Addr"]+2]>223:
                                            sourcegroup["sceneItemTransform"]["alignment"]=self.__AlignType["BtmRight"]
                                            self.__Client.set_scene_item_transform(source["sourceName"],sourcegroup["sceneItemId"],sourcegroup["sceneItemTransform"])                            
                                        sourcegroup["Alignment"]=data[sourcegroup["Addr"]+2]    
                                   
                                    if data[sourcegroup["Addr"]+3]!=sourcegroup["BoundsAlignment"]:
                                        if data[sourcegroup["Addr"]+3]<=27:
                                            sourcegroup["sceneItemTransform"]["boundsAlignment"]=self.__AlignType["TopLeft"]
                                            self.__Client.set_scene_item_transform(source["sourceName"],sourcegroup["sceneItemId"],sourcegroup["sceneItemTransform"])
                                        if data[sourcegroup["Addr"]+3]>27 and data[sourcegroup["Addr"]+3]<=55:
                                            sourcegroup["sceneItemTransform"]["boundsAlignment"]=self.__AlignType["TopCenter"]
                                            self.__Client.set_scene_item_transform(source["sourceName"],sourcegroup["sceneItemId"],sourcegroup["sceneItemTransform"])
                                        if data[sourcegroup["Addr"]+3]>55 and data[sourcegroup["Addr"]+3]<=83:
                                            sourcegroup["sceneItemTransform"]["boundsAlignment"]=self.__AlignType["TopRight"]
                                            self.__Client.set_scene_item_transform(source["sourceName"],sourcegroup["sceneItemId"],sourcegroup["sceneItemTransform"])
                                        if data[sourcegroup["Addr"]+3]>83 and data[sourcegroup["Addr"]+3]<=111:
                                            sourcegroup["sceneItemTransform"]["boundsAlignment"]=self.__AlignType["CenterLeft"]
                                            self.__Client.set_scene_item_transform(source["sourceName"],sourcegroup["sceneItemId"],sourcegroup["sceneItemTransform"])
                                        if data[sourcegroup["Addr"]+3]>111 and data[sourcegroup["Addr"]+3]<=139:
                                            sourcegroup["sceneItemTransform"]["boundsAlignment"]=self.__AlignType["Center"]
                                            self.__Client.set_scene_item_transform(source["sourceName"],sourcegroup["sceneItemId"],sourcegroup["sceneItemTransform"])
                                        if data[sourcegroup["Addr"]+3]>139 and data[sourcegroup["Addr"]+3]<=167:
                                            sourcegroup["sceneItemTransform"]["boundsAlignment"]=self.__AlignType["CenterRight"]
                                            self.__Client.set_scene_item_transform(source["sourceName"],sourcegroup["sceneItemId"],sourcegroup["sceneItemTransform"])
                                        if data[sourcegroup["Addr"]+3]>167 and data[sourcegroup["Addr"]+3]<=195:
                                            sourcegroup["sceneItemTransform"]["boundsAlignment"]=self.__AlignType["BtmLeft"]
                                            self.__Client.set_scene_item_transform(source["sourceName"],sourcegroup["sceneItemId"],sourcegroup["sceneItemTransform"])
                                        if data[sourcegroup["Addr"]+3]>195 and data[sourcegroup["Addr"]+3]<=223:
                                            sourcegroup["sceneItemTransform"]["boundsAlignment"]=self.__AlignType["BtmCenter"]
                                            self.__Client.set_scene_item_transform(source["sourceName"],sourcegroup["sceneItemId"],sourcegroup["sceneItemTransform"])
                                        if data[sourcegroup["Addr"]+3]>223:
                                            sourcegroup["sceneItemTransform"]["boundsAlignment"]=self.__AlignType["BtmRight"]
                                            self.__Client.set_scene_item_transform(source["sourceName"],sourcegroup["sceneItemId"],sourcegroup["sceneItemTransform"])                            
                                        sourcegroup["BoundsAlignment"]=data[sourcegroup["Addr"]+3]    
                                    
                                    if data[sourcegroup["Addr"]+4]!=sourcegroup["BoundsWidth"]:
                                        value=self.mapvalue(data[sourcegroup["Addr"]+4],0,255,1,4096)
                                        sourcegroup["sceneItemTransform"]["boundsWidth"]=value
                                        self.__Client.set_scene_item_transform(source["sourceName"],sourcegroup["sceneItemId"],sourcegroup["sceneItemTransform"])                            
                                        sourcegroup["BoundsWidth"]=data[sourcegroup["Addr"]+4] 
                                       
                                    if data[sourcegroup["Addr"]+5]!=sourcegroup["BoundsHeight"]:
                                        value=self.mapvalue(data[sourcegroup["Addr"]+5],0,255,1,4096)
                                        sourcegroup["sceneItemTransform"]["boundsHeight"]=value
                                        self.__Client.set_scene_item_transform(source["sourceName"],sourcegroup["sceneItemId"],sourcegroup["sceneItemTransform"])                            
                                        sourcegroup["BoundsHeight"]=data[sourcegroup["Addr"]+5] 
                                    
                                    if data[sourcegroup["Addr"]+6]!=sourcegroup["BoundsType"]:
                                        if data[sourcegroup["Addr"]+6]<=35:
                                            sourcegroup["sceneItemTransform"]["boundsType"]="OBS_BOUNDS_NONE"
                                            self.__Client.set_scene_item_transform(source["sourceName"],sourcegroup["sceneItemId"],sourcegroup["sceneItemTransform"])
                                        if data[sourcegroup["Addr"]+6]>35 and data[sourcegroup["Addr"]+6]<=71:
                                            sourcegroup["sceneItemTransform"]["boundsType"]="OBS_BOUNDS_STRETCH"
                                            self.__Client.set_scene_item_transform(source["sourceName"],sourcegroup["sceneItemId"],sourcegroup["sceneItemTransform"])
                                        if data[sourcegroup["Addr"]+6]>71 and data[sourcegroup["Addr"]+6]<=107:
                                            sourcegroup["sceneItemTransform"]["boundsType"]="OBS_BOUNDS_SCALE_INNER"
                                            self.__Client.set_scene_item_transform(source["sourceName"],sourcegroup["sceneItemId"],sourcegroup["sceneItemTransform"])
                                        if data[sourcegroup["Addr"]+6]>107 and data[sourcegroup["Addr"]+6]<=143:
                                            sourcegroup["sceneItemTransform"]["boundsType"]="OBS_BOUNDS_SCALE_OUTER"
                                            self.__Client.set_scene_item_transform(source["sourceName"],sourcegroup["sceneItemId"],sourcegroup["sceneItemTransform"])
                                        if data[sourcegroup["Addr"]+6]>143 and data[sourcegroup["Addr"]+6]<=179:
                                            sourcegroup["sceneItemTransform"]["boundsType"]="OBS_BOUNDS_SCALE_TO_WIDTH"
                                            self.__Client.set_scene_item_transform(source["sourceName"],sourcegroup["sceneItemId"],sourcegroup["sceneItemTransform"])
                                        if data[sourcegroup["Addr"]+6]>179 and data[sourcegroup["Addr"]+6]<=215:
                                            sourcegroup["sceneItemTransform"]["boundsType"]="OBS_BOUNDS_SCALE_TO_HEIGHT"
                                            self.__Client.set_scene_item_transform(source["sourceName"],sourcegroup["sceneItemId"],sourcegroup["sceneItemTransform"])
                                        if data[sourcegroup["Addr"]+6]>215:
                                            sourcegroup["sceneItemTransform"]["boundsType"]="OBS_BOUNDS_MAX_ONLY"
                                            self.__Client.set_scene_item_transform(source["sourceName"],sourcegroup["sceneItemId"],sourcegroup["sceneItemTransform"])
                                        sourcegroup["BoundsType"]=data[sourcegroup["Addr"]+6]    
                                   
                                    if data[sourcegroup["Addr"]+7]!=sourcegroup["CropBottom"]:
                                        value=self.mapvalue(data[sourcegroup["Addr"]+7],0,255,0,sourcegroup["sceneItemTransform"]["sourceHeight"])
                                        sourcegroup["sceneItemTransform"]["cropBottom"]=value
                                        self.__Client.set_scene_item_transform(source["sourceName"],sourcegroup["sceneItemId"],sourcegroup["sceneItemTransform"])                            
                                        sourcegroup["CropBottom"]=data[sourcegroup["Addr"]+7] 
                                    
                                    if data[sourcegroup["Addr"]+8]!=sourcegroup["CropLeft"]:
                                        value=self.mapvalue(data[sourcegroup["Addr"]+8],0,255,0,sourcegroup["sceneItemTransform"]["sourceWidth"])
                                        sourcegroup["sceneItemTransform"]["cropLeft"]=value
                                        self.__Client.set_scene_item_transform(source["sourceName"],sourcegroup["sceneItemId"],sourcegroup["sceneItemTransform"])                            
                                        sourcegroup["CropLeft"]=data[sourcegroup["Addr"]+8] 
                                    
                                    if data[sourcegroup["Addr"]+9]!=sourcegroup["CropRight"]:
                                        value=self.mapvalue(data[sourcegroup["Addr"]+9],0,255,0,sourcegroup["sceneItemTransform"]["sourceWidth"])
                                        sourcegroup["sceneItemTransform"]["cropRight"]=value
                                        self.__Client.set_scene_item_transform(source["sourceName"],sourcegroup["sceneItemId"],sourcegroup["sceneItemTransform"])                            
                                        sourcegroup["CropRight"]=data[sourcegroup["Addr"]+9] 
                                    
                                    if data[sourcegroup["Addr"]+10]!=sourcegroup["CropTop"]:
                                        value=self.mapvalue(data[sourcegroup["Addr"]+10],0,255,0,sourcegroup["sceneItemTransform"]["sourceHeight"])
                                        sourcegroup["sceneItemTransform"]["cropTop"]=value
                                        self.__Client.set_scene_item_transform(source["sourceName"],sourcegroup["sceneItemId"],sourcegroup["sceneItemTransform"])                            
                                        sourcegroup["CropTop"]=data[sourcegroup["Addr"]+10] 
                                    
                                    if data[sourcegroup["Addr"]+11]!=sourcegroup["ScaleX"]:
                                        value=self.mapvalue(data[sourcegroup["Addr"]+11],0,255,0,2)
                                        sourcegroup["sceneItemTransform"]["scaleX"]=value
                                        self.__Client.set_scene_item_transform(source["sourceName"],sourcegroup["sceneItemId"],sourcegroup["sceneItemTransform"])                            
                                        sourcegroup["ScaleX"]=data[sourcegroup["Addr"]+11] 
                                    
                                    if data[sourcegroup["Addr"]+12]!=sourcegroup["ScaleY"]:
                                        value=self.mapvalue(data[sourcegroup["Addr"]+12],0,255,0,2)
                                        sourcegroup["sceneItemTransform"]["scaleY"]=value
                                        self.__Client.set_scene_item_transform(source["sourceName"],sourcegroup["sceneItemId"],sourcegroup["sceneItemTransform"])                            
                                        sourcegroup["ScaleY"]=data[sourcegroup["Addr"]+12] 
                                    
                                    if data[sourcegroup["Addr"]+13]!=sourcegroup["PositionX"]:
                                        value=self.mapvalue(data[sourcegroup["Addr"]+13],0,255,-4096,4096)
                                        sourcegroup["sceneItemTransform"]["positionX"]=value
                                        self.__Client.set_scene_item_transform(source["sourceName"],sourcegroup["sceneItemId"],sourcegroup["sceneItemTransform"])                            
                                        sourcegroup["PositionX"]=data[sourcegroup["Addr"]+13] 
                                    
                                    if data[sourcegroup["Addr"]+14]!=sourcegroup["PositionY"]:
                                        value=self.mapvalue(data[sourcegroup["Addr"]+14],0,255,-4096,4096)
                                        sourcegroup["sceneItemTransform"]["positionY"]=value
                                        self.__Client.set_scene_item_transform(source["sourceName"],sourcegroup["sceneItemId"],sourcegroup["sceneItemTransform"])                            
                                        sourcegroup["PositionY"]=data[sourcegroup["Addr"]+14] 
                                    
                                    if data[sourcegroup["Addr"]+15]!=sourcegroup["Rotation"]:
                                        value=self.mapvalue(data[sourcegroup["Addr"]+15],0,255,0,360)
                                        sourcegroup["sceneItemTransform"]["rotation"]=value
                                        self.__Client.set_scene_item_transform(source["sourceName"],sourcegroup["sceneItemId"],sourcegroup["sceneItemTransform"])                            
                                        sourcegroup["Rotation"]=data[sourcegroup["Addr"]+15] 
                                    
                                    if data[sourcegroup["Addr"]+16]!=sourcegroup["BlendMode"]:
                                        if data[sourcegroup["Addr"]+16]<=35:
                                            sourcegroup["sceneItemBlendMode"]="OBS_BLEND_NORMAL"
                                            self.__Client.set_scene_item_blend_mode(source["sourceName"],sourcegroup["sceneItemId"],sourcegroup["sceneItemBlendMode"])
                                        if data[sourcegroup["Addr"]+16]>35 and data[sourcegroup["Addr"]+16]<=71:
                                            sourcegroup["sceneItemBlendMode"]="OBS_BLEND_ADDITIVE"
                                            self.__Client.set_scene_item_blend_mode(source["sourceName"],sourcegroup["sceneItemId"],sourcegroup["sceneItemBlendMode"])
                                        if data[sourcegroup["Addr"]+16]>71 and data[sourcegroup["Addr"]+16]<=107:
                                            sourcegroup["sceneItemBlendMode"]="OBS_BLEND_SUBTRACT"
                                            self.__Client.set_scene_item_blend_mode(source["sourceName"],sourcegroup["sceneItemId"],sourcegroup["sceneItemBlendMode"])
                                        if data[sourcegroup["Addr"]+16]>107 and data[sourcegroup["Addr"]+16]<=143:
                                            sourcegroup["sceneItemBlendMode"]="OBS_BLEND_SCREEN"
                                            self.__Client.set_scene_item_blend_mode(source["sourceName"],sourcegroup["sceneItemId"],sourcegroup["sceneItemBlendMode"])
                                        if data[sourcegroup["Addr"]+16]>143 and data[sourcegroup["Addr"]+16]<=179:
                                            sourcegroup["sceneItemBlendMode"]="OBS_BLEND_MULTIPLY"
                                            self.__Client.set_scene_item_blend_mode(source["sourceName"],sourcegroup["sceneItemId"],sourcegroup["sceneItemBlendMode"])
                                        if data[sourcegroup["Addr"]+16]>179 and data[sourcegroup["Addr"]+16]<=215:
                                            sourcegroup["sceneItemBlendMode"]="OBS_BLEND_LIGHTEN"
                                            self.__Client.set_scene_item_blend_mode(source["sourceName"],sourcegroup["sceneItemId"],sourcegroup["sceneItemBlendMode"])
                                        if data[sourcegroup["Addr"]+16]>215:
                                            sourcegroup["sceneItemBlendMode"]="OBS_BLEND_DARKEN"
                                            self.__Client.set_scene_item_blend_mode(source["sourceName"],sourcegroup["sceneItemId"],sourcegroup["sceneItemBlendMode"])
                                        sourcegroup["BlendMode"]=data[sourcegroup["Addr"]+16]    
                                    
                                else:
                                    
                                    buffer=self.__Artnet.get_buffer(self.__ListenerList[sourcegroup["Univ"]])

                                    if len(buffer)>0:
                                        if buffer[sourcegroup["Addr"]-1]!=sourcegroup["EnaDis"]:
                                            if buffer[sourcegroup["Addr"]-1]==0:
                                                self.__Client.set_scene_item_enabled(source["sourceName"],sourcegroup["sceneItemId"],False)
                                                sourcegroup["EnaDis"]=0
                                            if buffer[sourcegroup["Addr"]-1]==255:    
                                                self.__Client.set_scene_item_enabled(source["sourceName"],sourcegroup["sceneItemId"],True)
                                                sourcegroup["EnaDis"]=255
                                        
                                        if buffer[sourcegroup["Addr"]]!=sourcegroup["MoveUp"]:
                                            if buffer[sourcegroup["Addr"]]==255:
                                                self.__Client.set_scene_item_index(source["sourceName"],sourcegroup["sceneItemId"],sourcegroup["sceneItemIndex"]+1)
                                                sourcegroup["MoveUp"]=255
                                            if buffer[sourcegroup["Addr"]]==0:
                                                sourcegroup["MoveUp"]=0    
                                        
                                        if buffer[sourcegroup["Addr"]+1]!=sourcegroup["MoveDown"]:
                                            if buffer[sourcegroup["Addr"]+1]==255:
                                                value=sourcegroup["sceneItemIndex"]-1
                                                if value<0:
                                                    value=0
                                                self.__Client.set_scene_item_index(source["sourceName"],sourcegroup["sceneItemId"],value)
                                                sourcegroup["MoveDown"]=255
                                            if buffer[sourcegroup["Addr"]+1]==0:
                                                sourcegroup["MoveDown"]=0    
                                        
                                        if buffer[sourcegroup["Addr"]+2]!=sourcegroup["Alignment"]:
                                            if buffer[sourcegroup["Addr"]+2]<=27:
                                                sourcegroup["sceneItemTransform"]["alignment"]=self.__AlignType["TopLeft"]
                                                self.__Client.set_scene_item_transform(source["sourceName"],sourcegroup["sceneItemId"],sourcegroup["sceneItemTransform"])
                                            if buffer[sourcegroup["Addr"]+2]>27 and buffer[sourcegroup["Addr"]+2]<=55:
                                                sourcegroup["sceneItemTransform"]["alignment"]=self.__AlignType["TopCenter"]
                                                self.__Client.set_scene_item_transform(source["sourceName"],sourcegroup["sceneItemId"],sourcegroup["sceneItemTransform"])
                                            if buffer[sourcegroup["Addr"]+2]>55 and buffer[sourcegroup["Addr"]+2]<=83:
                                                sourcegroup["sceneItemTransform"]["alignment"]=self.__AlignType["TopRight"]
                                                self.__Client.set_scene_item_transform(source["sourceName"],sourcegroup["sceneItemId"],sourcegroup["sceneItemTransform"])
                                            if buffer[sourcegroup["Addr"]+2]>83 and buffer[sourcegroup["Addr"]+2]<=111:
                                                sourcegroup["sceneItemTransform"]["alignment"]=self.__AlignType["CenterLeft"]
                                                self.__Client.set_scene_item_transform(source["sourceName"],sourcegroup["sceneItemId"],sourcegroup["sceneItemTransform"])
                                            if buffer[sourcegroup["Addr"]+2]>111 and buffer[sourcegroup["Addr"]+2]<=139:
                                                sourcegroup["sceneItemTransform"]["alignment"]=self.__AlignType["Center"]
                                                self.__Client.set_scene_item_transform(source["sourceName"],sourcegroup["sceneItemId"],sourcegroup["sceneItemTransform"])
                                            if buffer[sourcegroup["Addr"]+2]>139 and buffer[sourcegroup["Addr"]+2]<=167:
                                                sourcegroup["sceneItemTransform"]["alignment"]=self.__AlignType["CenterRight"]
                                                self.__Client.set_scene_item_transform(source["sourceName"],sourcegroup["sceneItemId"],sourcegroup["sceneItemTransform"])
                                            if buffer[sourcegroup["Addr"]+2]>167 and buffer[sourcegroup["Addr"]+2]<=195:
                                                sourcegroup["sceneItemTransform"]["alignment"]=self.__AlignType["BtmLeft"]
                                                self.__Client.set_scene_item_transform(source["sourceName"],sourcegroup["sceneItemId"],sourcegroup["sceneItemTransform"])
                                            if buffer[sourcegroup["Addr"]+2]>195 and buffer[sourcegroup["Addr"]+2]<=223:
                                                sourcegroup["sceneItemTransform"]["alignment"]=self.__AlignType["BtmCenter"]
                                                self.__Client.set_scene_item_transform(source["sourceName"],sourcegroup["sceneItemId"],sourcegroup["sceneItemTransform"])
                                            if buffer[sourcegroup["Addr"]+2]>223:
                                                sourcegroup["sceneItemTransform"]["alignment"]=self.__AlignType["BtmRight"]
                                                self.__Client.set_scene_item_transform(source["sourceName"],sourcegroup["sceneItemId"],sourcegroup["sceneItemTransform"])                            
                                            sourcegroup["Alignment"]=buffer[sourcegroup["Addr"]+2]    
                                        
                                        if buffer[sourcegroup["Addr"]+3]!=sourcegroup["BoundsAlignment"]:
                                            if buffer[sourcegroup["Addr"]+3]<=27:
                                                sourcegroup["sceneItemTransform"]["boundsAlignment"]=self.__AlignType["TopLeft"]
                                                self.__Client.set_scene_item_transform(source["sourceName"],sourcegroup["sceneItemId"],sourcegroup["sceneItemTransform"])
                                            if buffer[sourcegroup["Addr"]+3]>27 and buffer[sourcegroup["Addr"]+3]<=55:
                                                sourcegroup["sceneItemTransform"]["boundsAlignment"]=self.__AlignType["TopCenter"]
                                                self.__Client.set_scene_item_transform(source["sourceName"],sourcegroup["sceneItemId"],sourcegroup["sceneItemTransform"])
                                            if buffer[sourcegroup["Addr"]+3]>55 and buffer[sourcegroup["Addr"]+3]<=83:
                                                sourcegroup["sceneItemTransform"]["boundsAlignment"]=self.__AlignType["TopRight"]
                                                self.__Client.set_scene_item_transform(source["sourceName"],sourcegroup["sceneItemId"],sourcegroup["sceneItemTransform"])
                                            if buffer[sourcegroup["Addr"]+3]>83 and buffer[sourcegroup["Addr"]+3]<=111:
                                                sourcegroup["sceneItemTransform"]["boundsAlignment"]=self.__AlignType["CenterLeft"]
                                                self.__Client.set_scene_item_transform(source["sourceName"],sourcegroup["sceneItemId"],sourcegroup["sceneItemTransform"])
                                            if buffer[sourcegroup["Addr"]+3]>111 and buffer[sourcegroup["Addr"]+3]<=139:
                                                sourcegroup["sceneItemTransform"]["boundsAlignment"]=self.__AlignType["Center"]
                                                self.__Client.set_scene_item_transform(source["sourceName"],sourcegroup["sceneItemId"],sourcegroup["sceneItemTransform"])
                                            if buffer[sourcegroup["Addr"]+3]>139 and buffer[sourcegroup["Addr"]+3]<=167:
                                                sourcegroup["sceneItemTransform"]["boundsAlignment"]=self.__AlignType["CenterRight"]
                                                self.__Client.set_scene_item_transform(source["sourceName"],sourcegroup["sceneItemId"],sourcegroup["sceneItemTransform"])
                                            if buffer[sourcegroup["Addr"]+3]>167 and buffer[sourcegroup["Addr"]+3]<=195:
                                                sourcegroup["sceneItemTransform"]["boundsAlignment"]=self.__AlignType["BtmLeft"]
                                                self.__Client.set_scene_item_transform(source["sourceName"],sourcegroup["sceneItemId"],sourcegroup["sceneItemTransform"])
                                            if buffer[sourcegroup["Addr"]+3]>195 and buffer[sourcegroup["Addr"]+3]<=223:
                                                sourcegroup["sceneItemTransform"]["boundsAlignment"]=self.__AlignType["BtmCenter"]
                                                self.__Client.set_scene_item_transform(source["sourceName"],sourcegroup["sceneItemId"],sourcegroup["sceneItemTransform"])
                                            if buffer[sourcegroup["Addr"]+3]>223:
                                                sourcegroup["sceneItemTransform"]["boundsAlignment"]=self.__AlignType["BtmRight"]
                                                self.__Client.set_scene_item_transform(source["sourceName"],sourcegroup["sceneItemId"],sourcegroup["sceneItemTransform"])                            
                                            sourcegroup["BoundsAlignment"]=buffer[sourcegroup["Addr"]+3]    

                                        if buffer[sourcegroup["Addr"]+4]!=sourcegroup["BoundsWidth"]:
                                            value=self.mapvalue(buffer[sourcegroup["Addr"]+4],0,255,1,4096)
                                            sourcegroup["sceneItemTransform"]["boundsWidth"]=value
                                            self.__Client.set_scene_item_transform(source["sourceName"],sourcegroup["sceneItemId"],sourcegroup["sceneItemTransform"])                            
                                            sourcegroup["BoundsWidth"]=buffer[sourcegroup["Addr"]+4] 
                                           
                                        if buffer[sourcegroup["Addr"]+5]!=sourcegroup["BoundsHeight"]:
                                            value=self.mapvalue(buffer[sourcegroup["Addr"]+5],0,255,1,4096)
                                            sourcegroup["sceneItemTransform"]["boundsHeight"]=value
                                            self.__Client.set_scene_item_transform(source["sourceName"],sourcegroup["sceneItemId"],sourcegroup["sceneItemTransform"])                            
                                            sourcegroup["BoundsHeight"]=buffer[sourcegroup["Addr"]+5] 
                                        
                                        if buffer[sourcegroup["Addr"]+6]!=sourcegroup["BoundsType"]:
                                            if buffer[sourcegroup["Addr"]+6]<=35:
                                                sourcegroup["sceneItemTransform"]["boundsType"]="OBS_BOUNDS_NONE"
                                                self.__Client.set_scene_item_transform(source["sourceName"],sourcegroup["sceneItemId"],sourcegroup["sceneItemTransform"])
                                            if buffer[sourcegroup["Addr"]+6]>35 and buffer[sourcegroup["Addr"]+6]<=71:
                                                sourcegroup["sceneItemTransform"]["boundsType"]="OBS_BOUNDS_STRETCH"
                                                self.__Client.set_scene_item_transform(source["sourceName"],sourcegroup["sceneItemId"],sourcegroup["sceneItemTransform"])
                                            if buffer[sourcegroup["Addr"]+6]>71 and buffer[sourcegroup["Addr"]+6]<=107:
                                                sourcegroup["sceneItemTransform"]["boundsType"]="OBS_BOUNDS_SCALE_INNER"
                                                self.__Client.set_scene_item_transform(source["sourceName"],sourcegroup["sceneItemId"],sourcegroup["sceneItemTransform"])
                                            if buffer[sourcegroup["Addr"]+6]>107 and buffer[sourcegroup["Addr"]+6]<=143:
                                                sourcegroup["sceneItemTransform"]["boundsType"]="OBS_BOUNDS_SCALE_OUTER"
                                                self.__Client.set_scene_item_transform(source["sourceName"],sourcegroup["sceneItemId"],sourcegroup["sceneItemTransform"])
                                            if buffer[sourcegroup["Addr"]+6]>143 and buffer[sourcegroup["Addr"]+6]<=179:
                                                sourcegroup["sceneItemTransform"]["boundsType"]="OBS_BOUNDS_SCALE_TO_WIDTH"
                                                self.__Client.set_scene_item_transform(source["sourceName"],sourcegroup["sceneItemId"],sourcegroup["sceneItemTransform"])
                                            if buffer[sourcegroup["Addr"]+6]>179 and buffer[sourcegroup["Addr"]+6]<=215:
                                                sourcegroup["sceneItemTransform"]["boundsType"]="OBS_BOUNDS_SCALE_TO_HEIGHT"
                                                self.__Client.set_scene_item_transform(source["sourceName"],sourcegroup["sceneItemId"],sourcegroup["sceneItemTransform"])
                                            if buffer[sourcegroup["Addr"]+6]>215:
                                                sourcegroup["sceneItemTransform"]["boundsType"]="OBS_BOUNDS_MAX_ONLY"
                                                self.__Client.set_scene_item_transform(source["sourceName"],sourcegroup["sceneItemId"],sourcegroup["sceneItemTransform"])
                                            sourcegroup["BoundsType"]=buffer[sourcegroup["Addr"]+6]    
                                        
                                        if buffer[sourcegroup["Addr"]+7]!=sourcegroup["CropBottom"]:
                                            value=self.mapvalue(buffer[sourcegroup["Addr"]+7],0,255,0,sourcegroup["sceneItemTransform"]["sourceHeight"])
                                            sourcegroup["sceneItemTransform"]["cropBottom"]=value
                                            self.__Client.set_scene_item_transform(source["sourceName"],sourcegroup["sceneItemId"],sourcegroup["sceneItemTransform"])                            
                                            sourcegroup["CropBottom"]=buffer[sourcegroup["Addr"]+7] 
                                        
                                        if buffer[sourcegroup["Addr"]+8]!=sourcegroup["CropLeft"]:
                                            value=self.mapvalue(buffer[sourcegroup["Addr"]+8],0,255,0,sourcegroup["sceneItemTransform"]["sourceWidth"])
                                            sourcegroup["sceneItemTransform"]["cropLeft"]=value
                                            self.__Client.set_scene_item_transform(source["sourceName"],sourcegroup["sceneItemId"],sourcegroup["sceneItemTransform"])                            
                                            sourcegroup["CropLeft"]=buffer[sourcegroup["Addr"]+8] 
                                        
                                        if buffer[sourcegroup["Addr"]+9]!=sourcegroup["CropRight"]:
                                            value=self.mapvalue(buffer[sourcegroup["Addr"]+9],0,255,0,sourcegroup["sceneItemTransform"]["sourceWidth"])
                                            sourcegroup["sceneItemTransform"]["cropRight"]=value
                                            self.__Client.set_scene_item_transform(source["sourceName"],sourcegroup["sceneItemId"],sourcegroup["sceneItemTransform"])                            
                                            sourcegroup["CropRight"]=buffer[sourcegroup["Addr"]+9] 
                                        
                                        if buffer[sourcegroup["Addr"]+10]!=sourcegroup["CropTop"]:
                                            value=self.mapvalue(buffer[sourcegroup["Addr"]+10],0,255,0,sourcegroup["sceneItemTransform"]["sourceHeight"])
                                            sourcegroup["sceneItemTransform"]["cropTop"]=value
                                            self.__Client.set_scene_item_transform(source["sourceName"],sourcegroup["sceneItemId"],sourcegroup["sceneItemTransform"])                            
                                            sourcegroup["CropTop"]=buffer[sourcegroup["Addr"]+10] 
                                        
                                        if buffer[sourcegroup["Addr"]+11]!=sourcegroup["ScaleX"]:
                                            value=self.mapvalue(buffer[sourcegroup["Addr"]+11],0,255,0,2)
                                            sourcegroup["sceneItemTransform"]["scaleX"]=value
                                            self.__Client.set_scene_item_transform(source["sourceName"],sourcegroup["sceneItemId"],sourcegroup["sceneItemTransform"])                            
                                            sourcegroup["ScaleX"]=buffer[sourcegroup["Addr"]+11] 
                                        
                                        if buffer[sourcegroup["Addr"]+12]!=sourcegroup["ScaleY"]:
                                            value=self.mapvalue(buffer[sourcegroup["Addr"]+12],0,255,0,2)
                                            sourcegroup["sceneItemTransform"]["scaleY"]=value
                                            self.__Client.set_scene_item_transform(source["sourceName"],sourcegroup["sceneItemId"],sourcegroup["sceneItemTransform"])                            
                                            sourcegroup["ScaleY"]=buffer[sourcegroup["Addr"]+12] 
                                        
                                        if buffer[sourcegroup["Addr"]+13]!=sourcegroup["PositionX"]:
                                            value=self.mapvalue(buffer[sourcegroup["Addr"]+13],0,255,-4096,4096)
                                            sourcegroup["sceneItemTransform"]["positionX"]=value
                                            self.__Client.set_scene_item_transform(source["sourceName"],sourcegroup["sceneItemId"],sourcegroup["sceneItemTransform"])                            
                                            sourcegroup["PositionX"]=buffer[sourcegroup["Addr"]+13] 
                                        
                                        if buffer[sourcegroup["Addr"]+14]!=sourcegroup["PositionY"]:
                                            value=self.mapvalue(buffer[sourcegroup["Addr"]+14],0,255,-4096,4096)
                                            sourcegroup["sceneItemTransform"]["positionY"]=value
                                            self.__Client.set_scene_item_transform(source["sourceName"],sourcegroup["sceneItemId"],sourcegroup["sceneItemTransform"])                            
                                            sourcegroup["PositionY"]=buffer[sourcegroup["Addr"]+14] 
                                        
                                        if buffer[sourcegroup["Addr"]+15]!=sourcegroup["Rotation"]:
                                            value=self.mapvalue(buffer[sourcegroup["Addr"]+15],0,255,0,360)
                                            sourcegroup["sceneItemTransform"]["rotation"]=value
                                            self.__Client.set_scene_item_transform(source["sourceName"],sourcegroup["sceneItemId"],sourcegroup["sceneItemTransform"])                            
                                            sourcegroup["Rotation"]=buffer[sourcegroup["Addr"]+15] 
                                        
                                        if buffer[sourcegroup["Addr"]+16]!=sourcegroup["BlendMode"]:
                                            if buffer[sourcegroup["Addr"]+16]<=35:
                                                sourcegroup["sceneItemBlendMode"]="OBS_BLEND_NORMAL"
                                                self.__Client.set_scene_item_blend_mode(source["sourceName"],sourcegroup["sceneItemId"],sourcegroup["sceneItemBlendMode"])
                                            if buffer[sourcegroup["Addr"]+16]>35 and buffer[sourcegroup["Addr"]+16]<=71:
                                                sourcegroup["sceneItemBlendMode"]="OBS_BLEND_ADDITIVE"
                                                self.__Client.set_scene_item_blend_mode(source["sourceName"],sourcegroup["sceneItemId"],sourcegroup["sceneItemBlendMode"])
                                            if buffer[sourcegroup["Addr"]+16]>71 and buffer[sourcegroup["Addr"]+16]<=107:
                                                sourcegroup["sceneItemBlendMode"]="OBS_BLEND_SUBTRACT"
                                                self.__Client.set_scene_item_blend_mode(source["sourceName"],sourcegroup["sceneItemId"],sourcegroup["sceneItemBlendMode"])
                                            if buffer[sourcegroup["Addr"]+16]>107 and buffer[sourcegroup["Addr"]+16]<=143:
                                                sourcegroup["sceneItemBlendMode"]="OBS_BLEND_SCREEN"
                                                self.__Client.set_scene_item_blend_mode(source["sourceName"],sourcegroup["sceneItemId"],sourcegroup["sceneItemBlendMode"])
                                            if buffer[sourcegroup["Addr"]+16]>143 and buffer[sourcegroup["Addr"]+16]<=179:
                                                sourcegroup["sceneItemBlendMode"]="OBS_BLEND_MULTIPLY"
                                                self.__Client.set_scene_item_blend_mode(source["sourceName"],sourcegroup["sceneItemId"],sourcegroup["sceneItemBlendMode"])
                                            if buffer[sourcegroup["Addr"]+16]>179 and buffer[sourcegroup["Addr"]+16]<=215:
                                                sourcegroup["sceneItemBlendMode"]="OBS_BLEND_LIGHTEN"
                                                self.__Client.set_scene_item_blend_mode(source["sourceName"],sourcegroup["sceneItemId"],sourcegroup["sceneItemBlendMode"])
                                            if buffer[sourcegroup["Addr"]+16]>215:
                                                sourcegroup["sceneItemBlendMode"]="OBS_BLEND_DARKEN"
                                                self.__Client.set_scene_item_blend_mode(source["sourceName"],sourcegroup["sceneItemId"],sourcegroup["sceneItemBlendMode"])
                                            sourcegroup["BlendMode"]=buffer[sourcegroup["Addr"]+16]       