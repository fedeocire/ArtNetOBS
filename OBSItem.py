import obsws_python as obs
import copy

class OBSItem():

    def __init__(self):
        self.__ClientOBS=None
        self.VersionOBS="-"
        self.VersionOBSWS="-"
        self.VideoSetting={'base_height':0, 'base_width':0, 'fps_denominator':0, 'fps_numerator':0, 'output_height':0, 'output_width':0}
        self.Collections=[]
        self.Profiles=[]
        self.Scenes=[]
        self.ScenesSel=[]
        self.ActiveScene=None
        self.Sources=[]
        self.SceneTransitions=[]
        self.CurrentCollection=None
        self.SourceUniverse=[]
        self.UnivGeneral=None
        self.AddrGeneral=None
    
    def SetReqClient(self,ClientOBS:obs.ReqClient):    
        self.__ClientOBS=ClientOBS

    def GetAllItem(self):
        self.GetVersion()
        self.GetVideoSetting()
        self.GetCollections()
        for collection in self.Collections:
            self.GetScenefromCollection(collection)
        self.GetProfiles()
        
        #self.GetScenes()
        #self.GetSources()
        self.GetScenesTransitions()
        #LoadSetting()
        #self.GetScenefromCollSelected(self.CurrentCollection)
        
    def non_match_elements(self,list_a, list_b):
        non_match = None
        for i in list_a:
            if i not in list_b:
                non_match=i
        return non_match    
               
        

    def GetVersion(self):    
        #Version OBS Studio and OBS WebSocket
        version=self.__ClientOBS.get_version()
        self.VersionOBS=version.obs_version
        self.VersionOBSWS=version.obs_web_socket_version

    def GetVideoSetting(self):
        #Video Setting
        vsOBS=self.__ClientOBS.get_video_settings()
        self.VideoSetting["base_height"]=vsOBS.base_height        
        self.VideoSetting["base_width"]=vsOBS.base_width
        self.VideoSetting["fps_denominator"]=vsOBS.fps_denominator
        self.VideoSetting["fps_numerator"]=vsOBS.fps_numerator
        self.VideoSetting["output_height"]=vsOBS.output_height
        self.VideoSetting["output_width"]=vsOBS.output_width

    def GetCollections(self):    
        #Collections
        clOBS=self.__ClientOBS.get_scene_collection_list()
        self.Collections=clOBS.scene_collections
        self.CurrentCollection=clOBS.current_scene_collection_name

    def UpdateCollections(self,NewColl):
        Namecoll=self.non_match_elements(NewColl,self.Collections)
        self.Collections=NewColl
        self.CurrentCollection=Namecoll
        self.GetScenes()
        
        return Namecoll

    def RemoveCollection(self,DelColl):
        Namecoll=self.non_match_elements(self.Collections,DelColl)
        
        for scene in self.Scenes:
            if scene["Collection"]==Namecoll:
                self.Scenes.remove(scene)

        self.Collections=DelColl
        # self.CurrentCollection=Namecoll
        # self.GetScenes()
        
        return Namecoll    

    def GetProfiles(self):    
        #Profiles
        PrOBS=self.__ClientOBS.get_profile_list()
        self.Profiles=PrOBS.profiles
        

    def GetScenes(self):     
        #Scenes
        scOBS=self.__ClientOBS.get_scene_list()
        
        
        for scene in scOBS.scenes:
            soOBS=self.__ClientOBS.get_scene_item_list(scene["sceneName"])  
            self.Sources=soOBS.scene_items
            for source in self.Sources:
                if source["isGroup"]:
                    source["Sources"]=[]
                    SoGrpOBS=self.__ClientOBS.get_group_scene_item_list(source["sourceName"])
                    for SoGroup in SoGrpOBS.scene_items:
                        SoGroup["EnaDis"]=None
                        SoGroup["MoveUp"]=None
                        SoGroup["MoveDown"]=None
                        SoGroup["Alignment"]=None
                        SoGroup["BoundsAlignment"]=None
                        SoGroup["BoundsWidth"]=None
                        SoGroup["BoundsHeight"]=None
                        SoGroup["BoundsType"]=None
                        SoGroup["CropBottom"]=None
                        SoGroup["CropLeft"]=None
                        SoGroup["CropRight"]=None
                        SoGroup["CropTop"]=None
                        SoGroup["ScaleX"]=None
                        SoGroup["ScaleY"]=None
                        SoGroup["PositionX"]=None
                        SoGroup["PositionY"]=None
                        SoGroup["Rotation"]=None
                        SoGroup["BlendMode"]=None
                        SoGroup["ArtnetEnable"]=False
                        SoGroup["Univ"]=None
                        SoGroup["Addr"]=None
                        if SoGroup["sceneItemTransform"]["boundsWidth"]<1:
                            SoGroup["sceneItemTransform"]["boundsWidth"]=1
                        if SoGroup["sceneItemTransform"]["boundsHeight"]<1:
                            SoGroup["sceneItemTransform"]["boundsHeight"]=1 
                        source["Sources"].append(copy.deepcopy(SoGroup))
                                       
                source["EnaDis"]=None
                source["MoveUp"]=None
                source["MoveDown"]=None
                source["Alignment"]=None
                source["BoundsAlignment"]=None
                source["BoundsWidth"]=None
                source["BoundsHeight"]=None
                source["BoundsType"]=None
                source["CropBottom"]=None
                source["CropLeft"]=None
                source["CropRight"]=None
                source["CropTop"]=None
                source["ScaleX"]=None
                source["ScaleY"]=None
                source["PositionX"]=None
                source["PositionY"]=None
                source["Rotation"]=None
                source["BlendMode"]=None
                source["ArtnetEnable"]=False
                source["Univ"]=None
                source["Addr"]=None
                if source["sceneItemTransform"]["boundsWidth"]<1:
                    source["sceneItemTransform"]["boundsWidth"]=1
                if source["sceneItemTransform"]["boundsHeight"]<1:
                    source["sceneItemTransform"]["boundsHeight"]=1    
            scene["Sources"]=self.Sources
            scene["Collection"]=self.CurrentCollection
                
        self.Scenes+=scOBS.scenes        
        self.ActiveScene=scOBS.current_program_scene_name 
    
    def UpdateScenes(self,name):
        scOBS=self.__ClientOBS.get_scene_list()
        
        for scene in scOBS.scenes:
            scene["Collection"]=self.CurrentCollection  
            if scene["sceneName"]==name:
                scene["Sources"]=[]
                newscene={'sceneIndex': scene["sceneIndex"], 'sceneName': name, 'Sources': [], 'Collection': self.CurrentCollection}
            else:
                for sceneOBS in self.Scenes:
                    if sceneOBS["Collection"]==scene["Collection"]:
                        if sceneOBS["sceneName"]==scene["sceneName"]:
                            if sceneOBS["sceneIndex"]==0:
                                index=self.Scenes.index(sceneOBS)
                            sceneOBS["sceneIndex"]+=1
        self.Scenes.insert(index,newscene)      
        self.ActiveScene=name         
               
    def RemoveScene(self,DelScene):
        for scene in self.Scenes:
            if scene["Collection"]==self.CurrentCollection:
                if scene["sceneName"]==DelScene:
                    self.Scenes.remove(scene)

        scOBS=self.__ClientOBS.get_scene_list()
        for sceneOBS in scOBS.scenes:
            for scene in self.Scenes:
                if scene["Collection"]==self.CurrentCollection:
                    if sceneOBS["sceneName"]==scene["sceneName"]:
                        scene["sceneIndex"]=sceneOBS["sceneIndex"]
        
    def UpdateNameScene(self,OldName,NewName):
        for scene in self.Scenes:
            if scene["Collection"]==self.CurrentCollection:
                if scene["sceneName"]==OldName:
                    scene["sceneName"]=NewName
        self.ActiveScene=NewName            

    def CheckisGroup(self,OldName):
        for scene in self.Scenes:
            if scene["Collection"]==self.CurrentCollection:
                if scene["sceneName"]==self.ActiveScene:
                    for source in scene["Sources"]:
                        if source["sourceName"]==OldName:
                            if source["isGroup"]:
                                return True  

    def CheckisItemGroup(self,scene_items):
        equal=0
        for scene in self.Scenes:
            if scene["Collection"]==self.CurrentCollection:
                if scene["sceneName"]==self.ActiveScene:
                    for item in scene_items:
                        for source in scene["Sources"]:
                            if (item["sceneItemId"]==source["sceneItemId"]) and (item["sceneItemIndex"]==source["sceneItemIndex"]):
                                equal+=1
                    if len(scene["Sources"])==equal:
                        return True
                       
                                                    


    def GetScenesTransitions(self):
        sctOBS=self.__ClientOBS.get_scene_transition_list()
        self.SceneTransitions=sctOBS.transitions

    def GetSourceFilterList(self,source):
        sofOBS=self.__ClientOBS.get_source_filter_list(source)
        print(sofOBS.filters)

    def GetSources(self):
        #Sources
        soOBS=self.__ClientOBS.get_scene_item_list(self.ActiveScene)  
        self.Sources=soOBS.scene_items
        for source in self.Sources:
            source["EnaDis"]=None
            source["MoveUp"]=None
            source["MoveDown"]=None

    def UpdateScenesItem(self,scene_item_id,scene_item_index,scene_name,source_name):
        soOBS=self.__ClientOBS.get_scene_item_list(scene_name)
        self.Sources=soOBS.scene_items
        for source in self.Sources:
              
            if source["sourceName"]==source_name:
                if source["isGroup"]:
                    source["Sources"]=[]    
                source["EnaDis"]=None
                source["MoveUp"]=None
                source["MoveDown"]=None
                source["Alignment"]=None
                source["BoundsAlignment"]=None
                source["BoundsWidth"]=None
                source["BoundsHeight"]=None
                source["BoundsType"]=None
                source["CropBottom"]=None
                source["CropLeft"]=None
                source["CropRight"]=None
                source["CropTop"]=None
                source["ScaleX"]=None
                source["ScaleY"]=None
                source["PositionX"]=None
                source["PositionY"]=None
                source["Rotation"]=None
                source["BlendMode"]=None
                source["ArtnetEnable"]=False
                source["Univ"]=None
                source["Addr"]=None
                if source["sceneItemTransform"]["boundsWidth"]<1:
                    source["sceneItemTransform"]["boundsWidth"]=1
                if source["sceneItemTransform"]["boundsHeight"]<1:
                    source["sceneItemTransform"]["boundsHeight"]=1
                for sceneOBS in self.Scenes:
                    if sceneOBS["Collection"]==self.CurrentCollection:
                        if sceneOBS["sceneName"]==scene_name:
                            sceneOBS["Sources"].append(copy.deepcopy(source))
                            break

    def RemoveScenesItem(self,scene_item_id,scene_name,source_name):                  
        for scene in self.Scenes:
            if scene["Collection"]==self.CurrentCollection:
                if scene["sceneName"]==scene_name:
                    for sources in scene["Sources"]:
                        if sources["sourceName"]==source_name and sources["sceneItemId"]==scene_item_id:
                            if sources["isGroup"]:
                                for sourcesgroup in sources["Sources"]:
                                    sources["Sources"].remove(sourcesgroup)
                            scene["Sources"].remove(sources)

        soOBS=self.__ClientOBS.get_scene_item_list(scene_name)
        
        for sceneitemOBS in soOBS.scene_items:
            for scene in self.Scenes:
                if scene["Collection"]==self.CurrentCollection:
                    if scene["sceneName"]==scene_name:
                        for sources in scene["Sources"]:
                            if sceneitemOBS["sourceName"]==sources["sourceName"]:
                                sources["sceneItemIndex"]=sceneitemOBS["sceneItemIndex"]

    def RemoveGroupScenesItem(self,scene_item_id,scene_name,source_name):                  
        for scene in self.Scenes:
            if scene["Collection"]==self.CurrentCollection:
                if scene["sceneName"]==self.ActiveScene:
                    for sources in scene["Sources"]:
                        if sources["sourceName"]==scene_name:
                            for sourcesgroup in sources["Sources"]:
                                if sourcesgroup["sourceName"]==source_name and sourcesgroup["sceneItemId"]==scene_item_id:
                                    sources["Sources"].remove(sourcesgroup)

        soOBS=self.__ClientOBS.get_group_scene_item_list(scene_name)
        
        for sceneitemOBS in soOBS.scene_items:
            for scene in self.Scenes:
                if scene["Collection"]==self.CurrentCollection:
                    if scene["sceneName"]==self.ActiveScene:
                        for sources in scene["Sources"]:
                            if sources["sourceName"]==scene_name:
                                for sourcesgroup in sources["Sources"]:
                                    if sceneitemOBS["sourceName"]==sourcesgroup["sourceName"]:
                                        sourcesgroup["sceneItemIndex"]=sceneitemOBS["sceneItemIndex"]                            

    def ReorderScenesItem(self,scene_items,scene_name):
        for scene in self.Scenes:
            if scene["Collection"]==self.CurrentCollection:
                if scene["sceneName"]==scene_name:
                    if len(scene_items)<len(scene["Sources"]): #Check Source Moved in a group 
                        grpOBS=self.__ClientOBS.get_group_list()
                        for group in grpOBS.groups:
                            SoGrpOBS=self.__ClientOBS.get_group_scene_item_list(group)
                            for sources in scene["Sources"]:
                                if sources["sourceName"]==group:
                                    if len(sources["Sources"])<len(SoGrpOBS.scene_items):
                                        for SoGroup in SoGrpOBS.scene_items:
                                            for SourceMoved in scene["Sources"]:
                                                if SourceMoved["sourceName"]==SoGroup["sourceName"]:
                                                    SourceMoved["sceneItemIndex"]=SoGroup["sceneItemIndex"]
                                                    sources["Sources"].append(copy.deepcopy(SourceMoved))
                                                    scene["Sources"].remove(SourceMoved)
                                                  
                    if len(scene_items)>len(scene["Sources"]): #Check Source Moved out of group 
                        grpOBS=self.__ClientOBS.get_group_list()
                        for group in grpOBS.groups:
                            for sources in scene["Sources"]:
                                if sources["sourceName"]==group:
                                    for SoScene in scene_items:
                                        for SourceMoved in sources["Sources"]:
                                            if SourceMoved["sceneItemId"]==SoScene["sceneItemId"]:
                                                scene["Sources"].append(copy.deepcopy(SourceMoved))
                                                sources["Sources"].remove(SourceMoved)
                                                         
                    for sources in scene["Sources"]:
                        for sourceOBS in scene_items:
                            if sourceOBS["sceneItemId"]==sources["sceneItemId"]:
                                sources["sceneItemIndex"]=sourceOBS["sceneItemIndex"]
                    
                    sourcesapp = [None] * len(scene["Sources"])       
                    for sources in scene["Sources"]:
                        sourcesapp[sources["sceneItemIndex"]]=copy.deepcopy(sources)           
                    scene["Sources"]=sourcesapp

    def ReorderScenesItemGroup(self,scene_name):                
        for scene in self.Scenes:
            if scene["Collection"]==self.CurrentCollection:
                if scene["sceneName"]==scene_name:
                    for sources in scene["Sources"]:
                        if sources["isGroup"]:
                            sources["Sources"]=[]
                            SoGrpOBS=self.__ClientOBS.get_group_scene_item_list(sources["sourceName"])
                            for SoGroup in SoGrpOBS.scene_items:    
                                if SoGroup["isGroup"]:
                                    SoGroup["Sources"]=[]    
                                SoGroup["EnaDis"]=None
                                SoGroup["MoveUp"]=None
                                SoGroup["MoveDown"]=None
                                SoGroup["Alignment"]=None
                                SoGroup["BoundsAlignment"]=None
                                SoGroup["BoundsWidth"]=None
                                SoGroup["BoundsHeight"]=None
                                SoGroup["BoundsType"]=None
                                SoGroup["CropBottom"]=None
                                SoGroup["CropLeft"]=None
                                SoGroup["CropRight"]=None
                                SoGroup["CropTop"]=None
                                SoGroup["ScaleX"]=None
                                SoGroup["ScaleY"]=None
                                SoGroup["PositionX"]=None
                                SoGroup["PositionY"]=None
                                SoGroup["Rotation"]=None
                                SoGroup["BlendMode"]=None
                                SoGroup["ArtnetEnable"]=False
                                SoGroup["Univ"]=None
                                SoGroup["Addr"]=None
                                if SoGroup["sceneItemTransform"]["boundsWidth"]<1:
                                    SoGroup["sceneItemTransform"]["boundsWidth"]=1
                                if SoGroup["sceneItemTransform"]["boundsHeight"]<1:
                                    SoGroup["sceneItemTransform"]["boundsHeight"]=1
                                sources["Sources"].append(copy.deepcopy(SoGroup))    

    def UpdateNameScenesItem(self,input_name,old_input_name):
        for scene in self.Scenes:
            if scene["Collection"]==self.CurrentCollection:
                if scene["sceneName"]==self.ActiveScene:
                    for source in scene["Sources"]:
                        if source["sourceName"]==old_input_name:
                            source["sourceName"]=input_name

    def GetScenefromCollection(self,Collection):
        self.__ClientOBS.set_current_scene_collection(Collection) 
        self.CurrentCollection=Collection   
        self.GetScenes()
        
    def GetScenefromCollSelected(self,Collection): 
        self.ScenesSel=[]  
        self.SourceUniverse=[]
        #self.SourceUniverse.append(self.UnivGeneral)
        for scene in self.Scenes:
            if scene["Collection"]==Collection:
                self.ScenesSel.append(scene)
                for source in scene["Sources"]:
                    if not (source["Univ"] in self.SourceUniverse) and source["ArtnetEnable"]==True:
                        self.SourceUniverse.append(source["Univ"])
                    if source["isGroup"]:
                        for sourcegroup in source["Sources"]:
                            if not (sourcegroup["Univ"] in self.SourceUniverse) and sourcegroup["ArtnetEnable"]==True:
                                self.SourceUniverse.append(sourcegroup["Univ"])
                
                  

    def SetSourcesTrasform(self,Source):
        soTOBS=self.__ClientOBS.get_scene_item_transform(self.ActiveScene,Source["sceneItemId"])     
        print(soTOBS.scene_item_transform)
        #18        