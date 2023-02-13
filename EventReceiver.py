import obsws_python as obs
from OBSItem import OBSItem
import dearpygui.dearpygui as dpg
from DMXReceiver import DMXReceiver
from Ticker import Ticker

class EventReceiver():
    
    def __init__(self,EventClientOBS:obs.EventClient,OBSIt:OBSItem,Status,OBSVe,OBSWs,Receiver:DMXReceiver,ticker:Ticker,ToggleAutoConnect,UpdateTable,InitializeTable):
        global __EvClOBS,__OBSIt,__Status,__OBSVe,__OBSWs,__Rcv,__TAutoConnect,__UpdateTable,__NoUpdateScene,__Ticker,__InitializeTable

        __Ticker=ticker
        __NoUpdateScene=0
        __EvClOBS=EventClientOBS
        __OBSIt=OBSIt
        __Status=Status
        __OBSVe=OBSVe
        __OBSWs=OBSWs
        __Rcv=Receiver
        __TAutoConnect=ToggleAutoConnect
        __UpdateTable=UpdateTable
        __InitializeTable=InitializeTable
        __EvClOBS.callback.register(self.on_scene_collection_list_changed)
        __EvClOBS.callback.register(self.on_scene_created)
        __EvClOBS.callback.register(self.on_scene_removed)
        __EvClOBS.callback.register(self.on_exit_started)
        __EvClOBS.callback.register(self.on_current_scene_collection_changing)
        __EvClOBS.callback.register(self.on_current_scene_collection_changed)
        __EvClOBS.callback.register(self.on_scene_name_changed)
        __EvClOBS.callback.register(self.on_scene_item_created)
        __EvClOBS.callback.register(self.on_scene_item_removed)
        __EvClOBS.callback.register(self.on_scene_item_list_reindexed) 
        __EvClOBS.callback.register(self.on_input_name_changed)

    def on_current_scene_collection_changing(event,data):
        global __NoUpdateScene
        __NoUpdateScene=1

    def on_current_scene_collection_changed(event,data):
        global __OBSIt,__NoUpdateScene

        __OBSIt.CurrentCollection=data.scene_collection_name
        __NoUpdateScene=0
          
    def on_scene_collection_list_changed(event,data):
        global __OBSIt,__UpdateTable

        
        if len(__OBSIt.Collections)<len(data.scene_collections):
            #Add New Collection
            value=__OBSIt.UpdateCollections(data.scene_collections)
            __UpdateTable("Col","a",value)
        else:    
            #Remove Collection
            value=__OBSIt.RemoveCollection(data.scene_collections)
            __UpdateTable("Col","d",value)

    def on_scene_item_created(event,data):
        global __OBSIt,__UpdateTable,__NoUpdateScene
        if __NoUpdateScene==0:
            __OBSIt.UpdateScenesItem(data.scene_item_id,data.scene_item_index,data.scene_name,data.source_name)
            __UpdateTable("Source","a",[data.scene_name,data.source_name,data.scene_item_index,data.scene_item_id])

    def on_scene_item_removed(event,data):
        global __OBSIt,__UpdateTable,__NoUpdateScene
        if __NoUpdateScene==0:
            if __OBSIt.CheckisGroup(data.scene_name):
                __OBSIt.RemoveGroupScenesItem(data.scene_item_id,data.scene_name,data.source_name)
                #First True/False is for Group,Second True/False is for source group
                __UpdateTable("Source","d",[data.scene_name,data.source_name,data.scene_item_id,True,True])
                return
            if __OBSIt.CheckisGroup(data.source_name):
                __OBSIt.RemoveScenesItem(data.scene_item_id,data.scene_name,data.source_name)
                __UpdateTable("Source","d",[data.scene_name,data.source_name,data.scene_item_id,True,False])
            else:   
                __OBSIt.RemoveScenesItem(data.scene_item_id,data.scene_name,data.source_name)
                __UpdateTable("Source","d",[data.scene_name,data.source_name,data.scene_item_id,False,False])

    def on_scene_item_list_reindexed(event,data):
        global __OBSIt,__UpdateTable,__NoUpdateScene
        if __NoUpdateScene==0:
            if __OBSIt.CheckisItemGroup(data.scene_items):
                __OBSIt.ReorderScenesItemGroup(data.scene_name)
            else:    
                __OBSIt.ReorderScenesItem(data.scene_items,data.scene_name)
            __UpdateTable("Source","r",[data.scene_items,data.scene_name])

    def on_input_name_changed(event,data):
        global __OBSIt,__UpdateTable,__NoUpdateScene
        if __NoUpdateScene==0:
            __OBSIt.UpdateNameScenesItem(data.input_name, data.old_input_name)
            __UpdateTable("Source","u",[data.input_name, data.old_input_name,False])   

    def on_scene_created(event,data):
        global __OBSIt,__UpdateTable,__NoUpdateScene
        if __NoUpdateScene==0:
            if data.is_group:
                pass
                #__OBSIt.UpdateScenesItem(None,None,None,data.scene_name)
                #__UpdateTable("Source","a",[data.scene_name,data.source_name,data.scene_item_index,data.scene_item_id])
            else:    
                __OBSIt.UpdateScenes(data.scene_name)
                __UpdateTable("Sc","a",data.scene_name) 

    def on_scene_removed(event,data):
        global __OBSIt,__UpdateTable,__NoUpdateScene
        if __NoUpdateScene==0:
            if data.is_group:
                pass
            else:
                __OBSIt.RemoveScene(data.scene_name)
                __UpdateTable("Sc","d",data.scene_name)    

    def on_scene_name_changed(event,data):
        global __OBSIt,__UpdateTable,__NoUpdateScene
        if __NoUpdateScene==0:
            if __OBSIt.CheckisGroup(data.old_scene_name):
                __OBSIt.UpdateNameScenesItem(data.scene_name, data.old_scene_name)
                __UpdateTable("Source","u",[data.scene_name, data.old_scene_name,True])   
            else:    
                __OBSIt.UpdateNameScene(data.old_scene_name,data.scene_name)
                __UpdateTable("Sc","u",[data.old_scene_name,data.scene_name])
                       

    def on_exit_started(event,data):
        global __EvClOBS,__OBSIt,__Status,__OBSVe,__OBSWs,__Rcv,__Ticker,__InitializeTable
        __Ticker.clear_callbacks()
        __Rcv.stop()
        __OBSIt=None
        __EvClOBS.unsubscribe()
        __TAutoConnect()
        __InitializeTable()
        dpg.configure_item(__Status,default_value="Connection Status: Disconnected")
        dpg.configure_item(__OBSVe,default_value="OBS Studio Version: -")
        dpg.configure_item(__OBSWs,default_value="OBS WebSocket Version: -")
        print("OBS Exit")