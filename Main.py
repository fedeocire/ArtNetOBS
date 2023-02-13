import dearpygui.dearpygui as dpg
import os
import sys
import json
import obsws_python as obs
from Ticker import Ticker
from DMXReceiver import DMXReceiver
from EventReceiver import EventReceiver
from OBSItem import OBSItem
from TreeNodeTable import TreeNodeTable
from time import sleep
import subprocess



ticker=Ticker() # Timer Ticker for loop Artnet Receiving (DMXReceiver) 
ticker.start()  # and EventClient OBS (EventReceiver)
Reqclient=None  # RequestClient OBS Variable    
Receiver=None   # Artnet Receiver Variable
Universe=1      # Universe Variable assigned by GeneralUniv-1
Address=1       # Address Variable assigned by GeneralAddr
OBSWsIPAddr="127.0.0.1" #Ip Address OBS WebSocket 
OBSWsPort=4455          #Port OBS WebSocket
OBSWsPass="Artnetobs"   #Password OBS WebSocket
OBSIt=None              #OBS Item Variable
Eventclient=None
BtnConnect=None
folder = os.path.dirname(os.path.abspath(__file__))
filename = 'config.json'
if hasattr(sys, '_MEIPASS'):
    # PyInstaller >= 1.6
    os.chdir(sys._MEIPASS)
    sysex=sys.executable.replace(sys.executable.split("\\")[-1],"")
    filename=os.path.join(sysex, filename)
   
elif '_MEIPASS2' in os.environ:
    # PyInstaller < 1.6 (tested on 1.5 only)
    os.chdir(os.environ['_MEIPASS2'])
    #filename=os.path.join(os.environ['_MEIPASS2'], filename)
    sysex=sys.executable.replace(sys.executable.split("\\")[-1],"")
    filename=os.path.join(sysex, filename)
    
else:
    os.chdir(os.path.dirname(sys.argv[0]))
    filename=os.path.join(os.path.dirname(sys.argv[0]), filename)
    


dpg.create_context()
dpg.create_viewport(title='Artnet for OBS', x_pos=10,y_pos=10,width=800,height=600,max_width=800,max_height=600,resizable=False,clear_color=(31,33,42),small_icon=folder+"/Logo.ico",large_icon=folder+"/Logo.ico") 
dpg.setup_dearpygui()

# Load Font Arial
with dpg.font_registry():
    default_font=dpg.add_font(folder+"/arial.ttf", 13)
    bold_font=dpg.add_font(folder+"/arialbd.ttf", 13)

# Theme Global
with dpg.theme() as MainTheme:        
    with dpg.theme_component(dpg.mvAll):
        dpg.add_theme_style(dpg.mvStyleVar_WindowPadding, 10,10, category=dpg.mvThemeCat_Core)
        dpg.add_theme_style(dpg.mvStyleVar_FramePadding, 10,10, category=dpg.mvThemeCat_Core)
        dpg.add_theme_style(dpg.mvStyleVar_ChildBorderSize, 0, category=dpg.mvThemeCat_Core)
        dpg.add_theme_style(dpg.mvStyleVar_ChildRounding, 0, category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_ChildBg, (43, 46, 56), category=dpg.mvThemeCat_Core)
        dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 5, category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_FrameBg, (72, 72, 85), category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_TableHeaderBg, (72, 72, 85), category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_TableRowBg, (118, 118, 118), category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_TableRowBgAlt, (118, 118, 118), category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_Button, (72, 72, 85), category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_TabActive, (72, 72, 85), category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_Text, (255, 255, 255), category=dpg.mvThemeCat_Core)
    
    #Theme for Table
    with dpg.theme_component(dpg.mvTable):
        dpg.add_theme_style(dpg.mvStyleVar_FramePadding, 0,0, category=dpg.mvThemeCat_Core) 
        dpg.add_theme_style(dpg.mvStyleVar_CellPadding, 10,8, category=dpg.mvThemeCat_Core) 
        dpg.add_theme_color(dpg.mvThemeCol_HeaderHovered, (255, 255, 255,0), category=dpg.mvThemeCat_Core)  
        dpg.add_theme_color(dpg.mvThemeCol_HeaderActive, (255, 255, 255,0), category=dpg.mvThemeCat_Core) 
    
    #Theme for InputInt
    with dpg.theme_component(dpg.mvInputInt):
        dpg.add_theme_style(dpg.mvStyleVar_FramePadding, 5,5, category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_FrameBg, (72, 72, 85), category=dpg.mvThemeCat_Core) 
        dpg.add_theme_color(dpg.mvThemeCol_Button, (72, 72, 85), category=dpg.mvThemeCat_Core)

    #Theme for InputInt Disabled
    with dpg.theme_component(dpg.mvInputInt,enabled_state=False):
        dpg.add_theme_style(dpg.mvStyleVar_FramePadding, 5,5, category=dpg.mvThemeCat_Core) 
        dpg.add_theme_color(dpg.mvThemeCol_FrameBg, (40, 40, 40), category=dpg.mvThemeCat_Core) 
        dpg.add_theme_color(dpg.mvThemeCol_Button, (40, 40, 40), category=dpg.mvThemeCat_Core)  

    #Theme for Checkbox
    with dpg.theme_component(dpg.mvCheckbox):
        dpg.add_theme_style(dpg.mvStyleVar_FramePadding, 5,5, category=dpg.mvThemeCat_Core) 

#Theme Button Connect
with dpg.theme() as BtnConnectTheme:
    with dpg.theme_component(dpg.mvAll):
           dpg.add_theme_color(dpg.mvThemeCol_Button, (42, 150, 14), category=dpg.mvThemeCat_Core)
           dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (42, 150, 14), category=dpg.mvThemeCat_Core)
           dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, (42, 150, 14), category=dpg.mvThemeCat_Core)
           
with dpg.theme() as BtnConnectPressedTheme:
    with dpg.theme_component(dpg.mvAll):
           dpg.add_theme_color(dpg.mvThemeCol_Button, (210, 0, 0), category=dpg.mvThemeCat_Core)
           dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (210, 0, 0), category=dpg.mvThemeCat_Core)
           dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, (210, 0, 0), category=dpg.mvThemeCat_Core)


#Theme Port
with dpg.theme() as PortTheme:
    with dpg.theme_component(dpg.mvAll):
           dpg.add_theme_style(dpg.mvStyleVar_FramePadding, 10,10, category=dpg.mvThemeCat_Core)

#Theme Text
with dpg.theme() as TextTheme:
    with dpg.theme_component(dpg.mvAll):
           dpg.add_theme_style(dpg.mvStyleVar_FramePadding, 0,5, category=dpg.mvThemeCat_Core)

#Theme AutoConnect
with dpg.theme() as AutoCTheme:
    with dpg.theme_component(dpg.mvAll):
           dpg.add_theme_style(dpg.mvStyleVar_FramePadding, 0,0, category=dpg.mvThemeCat_Core)

#Theme Group container Table
with dpg.theme() as GroupTheme:
    with dpg.theme_component(dpg.mvAll):
            dpg.add_theme_color(dpg.mvThemeCol_ChildBg, (118, 118, 118), category=dpg.mvThemeCat_Core)

#Theme Modal Window Save OK
with dpg.theme() as ModalTheme:
    with dpg.theme_component(dpg.mvAll):
           dpg.add_theme_style(dpg.mvStyleVar_WindowRounding, 5, category=dpg.mvThemeCat_Core)
           
#Connect to OBS
def callback():
    global ticker,OBSIt,Universe,Address,OBSWsIPAddr,OBSWsPort,OBSWsPass,Reqclient,Receiver,BtnConnect,Eventclient
    if dpg.get_value(Status)=="Connection Status: Disconnected":
        try:
            Reqclient=None
            Receiver=None

            #Initialize Request Client OBS
            Reqclient = obs.ReqClient(host=OBSWsIPAddr, port=OBSWsPort, password=OBSWsPass)
            
            #In itialize and Get Item (Collection,Scene,Source,Profile) from OBS
            OBSIt=OBSItem()
            OBSIt.SetReqClient(Reqclient)
            OBSIt.GetAllItem()
            
            InitializeTable()
            #Load OBS Item in Table
            SetItemtoTable(OBSIt)
            
            OBSIt.UnivGeneral=Universe
            OBSIt.AddrGeneral=Address
                        
            #Start Artnet Receiver
            Receiver=DMXReceiver(Universe,Address,ticker,OBSIt,Reqclient)
            
            #Initialize and Get Event from OBS
            Eventclient = obs.EventClient(host=OBSWsIPAddr, port=OBSWsPort, password=OBSWsPass)
            Event=EventReceiver(Eventclient,OBSIt,Status,OBSVe,OBSWs,Receiver,ticker,ToggleAutoConnect,UpdateTable,InitializeTable)
            
            dpg.configure_item(Status,default_value="Connection Status: Connected")
            dpg.configure_item(OBSVe,default_value="OBS Studio Version: "+str(OBSIt.VersionOBS))
            dpg.configure_item(OBSWs,default_value="OBS WebSocket Version: "+str(OBSIt.VersionOBSWS))
            
            LoadSetting()
            
            
        except:
            print("OBS not found")
    
    # if dpg.get_item_label(BtnConnect)=="Disconnect":
    #     Eventclient.unsubscribe()
    #     Eventclient=None
    #     ticker.clear_callbacks()
    #     Reqclient=None
    #     Receiver.stop()
    #     OBSIt=None
    #     #ToggleAutoConnect()
    #     InitializeTable()
    #     dpg.configure_item(Status,default_value="Connection Status: Disconnected")
    #     dpg.configure_item(OBSVe,default_value="OBS Studio Version: -")
    #     dpg.configure_item(OBSWs,default_value="OBS WebSocket Version: -")
        
    #     dpg.bind_item_theme(BtnConnect,BtnConnectTheme)
    #     dpg.set_item_label(BtnConnect,"Connect")

    if dpg.get_value(Status)=="Connection Status: Connected":
        #dpg.bind_item_theme(BtnConnect,BtnConnectPressedTheme)
        #dpg.set_item_label(BtnConnect,"Disconnect")
        #Disable Autoconnect to connect to OBS
        if dpg.get_value(AutoConnect):
            ticker.remove_callback(callback)
    
        OBSIt.GetScenefromCollSelected(OBSIt.CurrentCollection)
        Receiver.Add_Listener()

        
            

#Initialize Table
def InitializeTable():
    Rows=dpg.get_item_children(TableItem,1)
    GroupChild=dpg.get_item_children(Rows[1],1)
    dpg.set_item_user_data(GroupChild[0],False)
    btnChild=dpg.get_item_children(GroupChild[0],1)
    dpg.configure_item(btnChild[0],direction=dpg.mvDir_Right)
    if len(Rows)>2:
        for indexrow in range(2,len(Rows)):
            dpg.delete_item(Rows[indexrow])

#Setting Item OBS to Table       
def SetItemtoTable(OBSit:OBSItem):
    #Add Collection OBS
    c=1
    for collection in OBSit.Collections:
        with dpg.table_row(parent=TableItem,show=False,label="Col"+str(c)):
            TreeNodeTable(collection,10,"Sc"+str(c))
        
        #Add Scene OBS
        s=1
        indexrow=None
        indexsorow=None
        indexsorowgroup=None
        for scene in OBSit.Scenes: 
            if scene["Collection"]==collection:
                s=scene["sceneIndex"]
                if indexrow==None:
                    with dpg.table_row(parent=TableItem,show=False,label="Sc"+str(c)+str(s)) as indexrow:
                        TreeNodeTable(scene["sceneName"],20,"S"+str(c)+str(s))
                        
                    #Add Source's Scene OBS
                    for source in scene["Sources"]: 
                        so=source["sceneItemIndex"]
                        if indexsorow==None:
                            if source["isGroup"]:
                                gr=source["sceneItemIndex"]
                                with dpg.table_row(parent=TableItem,show=False,label="S"+str(c)+str(s)+str(so)) as indexsorow:
                                    TreeNodeTable(source["sourceName"],40,"G"+str(c)+str(s)+str(gr),5)  
                                    dpg.add_checkbox(tag=scene["Collection"]+source["sourceName"]+str(source["sceneItemId"])+"chkbox",callback=lambda s:ToggleUnivAddr(s))
                                    dpg.add_input_int(tag=scene["Collection"]+source["sourceName"]+str(source["sceneItemId"])+"Univ",width=130,default_value=1,min_value=1,max_value=32768,min_clamped=True,max_clamped=True,enabled=False)
                                    dpg.add_input_int(tag=scene["Collection"]+source["sourceName"]+str(source["sceneItemId"])+"Addr",width=130,default_value=1,min_value=1,max_value=512,min_clamped=True,max_clamped=True,enabled=False)
                                for SourceGroup in source["Sources"]:
                                    so=SourceGroup["sceneItemIndex"]
                                    if indexsorowgroup==None: 
                                        with dpg.table_row(parent=TableItem,show=False,label="G"+str(c)+str(s)+str(gr)+str(so)) as indexsorowgroup:
                                            Sourcetxt=dpg.add_text(default_value=SourceGroup["sourceName"],indent=60)   
                                            dpg.bind_item_theme(Sourcetxt,TextTheme) 
                                            dpg.add_checkbox(tag=scene["Collection"]+SourceGroup["sourceName"]+str(SourceGroup["sceneItemId"])+"chkbox",callback=lambda s:ToggleUnivAddr(s))
                                            dpg.add_input_int(tag=scene["Collection"]+SourceGroup["sourceName"]+str(SourceGroup["sceneItemId"])+"Univ",width=130,default_value=1,min_value=1,max_value=32768,min_clamped=True,max_clamped=True,enabled=False)
                                            dpg.add_input_int(tag=scene["Collection"]+SourceGroup["sourceName"]+str(SourceGroup["sceneItemId"])+"Addr",width=130,default_value=1,min_value=1,max_value=512,min_clamped=True,max_clamped=True,enabled=False)
                                    else:    
                                        oldindexsorowgroup=indexsorowgroup
                                        with dpg.table_row(parent=TableItem,show=False,label="G"+str(c)+str(s)+str(gr)+str(so),before=oldindexsorowgroup) as indexsorowgroup:
                                            Sourcetxt=dpg.add_text(default_value=SourceGroup["sourceName"],indent=60)   
                                            dpg.bind_item_theme(Sourcetxt,TextTheme) 
                                            dpg.add_checkbox(tag=scene["Collection"]+SourceGroup["sourceName"]+str(SourceGroup["sceneItemId"])+"chkbox",callback=lambda s:ToggleUnivAddr(s))
                                            dpg.add_input_int(tag=scene["Collection"]+SourceGroup["sourceName"]+str(SourceGroup["sceneItemId"])+"Univ",width=130,default_value=1,min_value=1,max_value=32768,min_clamped=True,max_clamped=True,enabled=False)
                                            dpg.add_input_int(tag=scene["Collection"]+SourceGroup["sourceName"]+str(SourceGroup["sceneItemId"])+"Addr",width=130,default_value=1,min_value=1,max_value=512,min_clamped=True,max_clamped=True,enabled=False) 
                            else:
                                with dpg.table_row(parent=TableItem,show=False,label="S"+str(c)+str(s)+str(so)) as indexsorow:
                                    Sourcetxt=dpg.add_text(default_value=source["sourceName"],indent=40)   
                                    dpg.bind_item_theme(Sourcetxt,TextTheme) 
                                    dpg.add_checkbox(tag=scene["Collection"]+source["sourceName"]+str(source["sceneItemId"])+"chkbox",callback=lambda s:ToggleUnivAddr(s))
                                    dpg.add_input_int(tag=scene["Collection"]+source["sourceName"]+str(source["sceneItemId"])+"Univ",width=130,default_value=1,min_value=1,max_value=32768,min_clamped=True,max_clamped=True)
                                    dpg.add_input_int(tag=scene["Collection"]+source["sourceName"]+str(source["sceneItemId"])+"Addr",width=130,default_value=1,min_value=1,max_value=512,min_clamped=True,max_clamped=True)
                        else:   
                            oldindexsorow=indexsorow
                            if source["isGroup"]:
                                gr=source["sceneItemIndex"]
                                with dpg.table_row(parent=TableItem,show=False,label="S"+str(c)+str(s)+str(so),before=oldindexsorow) as indexsorow:
                                    TreeNodeTable(source["sourceName"],40,"G"+str(c)+str(s)+str(gr),5)  
                                    dpg.add_checkbox(tag=scene["Collection"]+source["sourceName"]+str(source["sceneItemId"])+"chkbox",callback=lambda s:ToggleUnivAddr(s))
                                    dpg.add_input_int(tag=scene["Collection"]+source["sourceName"]+str(source["sceneItemId"])+"Univ",width=130,default_value=1,min_value=1,max_value=32768,min_clamped=True,max_clamped=True,enabled=False)
                                    dpg.add_input_int(tag=scene["Collection"]+source["sourceName"]+str(source["sceneItemId"])+"Addr",width=130,default_value=1,min_value=1,max_value=512,min_clamped=True,max_clamped=True,enabled=False)
                                indexsorowgroup=None
                                for SourceGroup in source["Sources"]:
                                    so=SourceGroup["sceneItemIndex"]
                                    if indexsorowgroup==None: 
                                        with dpg.table_row(parent=TableItem,show=False,label="G"+str(c)+str(s)+str(gr)+str(so),before=oldindexsorow) as indexsorowgroup:
                                            Sourcetxt=dpg.add_text(default_value=SourceGroup["sourceName"],indent=60)   
                                            dpg.bind_item_theme(Sourcetxt,TextTheme) 
                                            dpg.add_checkbox(tag=scene["Collection"]+SourceGroup["sourceName"]+str(SourceGroup["sceneItemId"])+"chkbox",callback=lambda s:ToggleUnivAddr(s))
                                            dpg.add_input_int(tag=scene["Collection"]+SourceGroup["sourceName"]+str(SourceGroup["sceneItemId"])+"Univ",width=130,default_value=1,min_value=1,max_value=32768,min_clamped=True,max_clamped=True,enabled=False)
                                            dpg.add_input_int(tag=scene["Collection"]+SourceGroup["sourceName"]+str(SourceGroup["sceneItemId"])+"Addr",width=130,default_value=1,min_value=1,max_value=512,min_clamped=True,max_clamped=True,enabled=False)
                                    else:    
                                        oldindexsorowgroup=indexsorowgroup
                                        with dpg.table_row(parent=TableItem,show=False,label="G"+str(c)+str(s)+str(gr)+str(so),before=oldindexsorowgroup) as indexsorowgroup:
                                            Sourcetxt=dpg.add_text(default_value=SourceGroup["sourceName"],indent=60)   
                                            dpg.bind_item_theme(Sourcetxt,TextTheme) 
                                            dpg.add_checkbox(tag=scene["Collection"]+SourceGroup["sourceName"]+str(SourceGroup["sceneItemId"])+"chkbox",callback=lambda s:ToggleUnivAddr(s))
                                            dpg.add_input_int(tag=scene["Collection"]+SourceGroup["sourceName"]+str(SourceGroup["sceneItemId"])+"Univ",width=130,default_value=1,min_value=1,max_value=32768,min_clamped=True,max_clamped=True,enabled=False)
                                            dpg.add_input_int(tag=scene["Collection"]+SourceGroup["sourceName"]+str(SourceGroup["sceneItemId"])+"Addr",width=130,default_value=1,min_value=1,max_value=512,min_clamped=True,max_clamped=True,enabled=False) 
                            else:
                                with dpg.table_row(parent=TableItem,show=False,label="S"+str(c)+str(s)+str(so),before=oldindexsorow) as indexsorow:
                                    Sourcetxt=dpg.add_text(default_value=source["sourceName"],indent=40)   
                                    dpg.bind_item_theme(Sourcetxt,TextTheme) 
                                    dpg.add_checkbox(tag=scene["Collection"]+source["sourceName"]+str(source["sceneItemId"])+"chkbox",callback=lambda s:ToggleUnivAddr(s))
                                    dpg.add_input_int(tag=scene["Collection"]+source["sourceName"]+str(source["sceneItemId"])+"Univ",width=130,default_value=1,min_value=1,max_value=32768,min_clamped=True,max_clamped=True)
                                    dpg.add_input_int(tag=scene["Collection"]+source["sourceName"]+str(source["sceneItemId"])+"Addr",width=130,default_value=1,min_value=1,max_value=512,min_clamped=True,max_clamped=True)
                else:    
                    oldindexrow=indexrow
                    with dpg.table_row(parent=TableItem,show=False,label="Sc"+str(c)+str(s),before=oldindexrow) as indexrow:
                        TreeNodeTable(scene["sceneName"],20,"S"+str(c)+str(s))
                    indexsorow=None
                    #Add Source's Scene OBS
                    for source in scene["Sources"]:
                        so=source["sceneItemIndex"]
                        if indexsorow==None: 
                            if source["isGroup"]:
                                gr=source["sceneItemIndex"]
                                with dpg.table_row(parent=TableItem,show=False,label="S"+str(c)+str(s)+str(so),before=oldindexrow) as indexsorow:
                                    TreeNodeTable(source["sourceName"],40,"G"+str(c)+str(s)+str(gr),5)  
                                    dpg.add_checkbox(tag=scene["Collection"]+source["sourceName"]+str(source["sceneItemId"])+"chkbox",callback=lambda s:ToggleUnivAddr(s))
                                    dpg.add_input_int(tag=scene["Collection"]+source["sourceName"]+str(source["sceneItemId"])+"Univ",width=130,default_value=1,min_value=1,max_value=32768,min_clamped=True,max_clamped=True,enabled=False)
                                    dpg.add_input_int(tag=scene["Collection"]+source["sourceName"]+str(source["sceneItemId"])+"Addr",width=130,default_value=1,min_value=1,max_value=512,min_clamped=True,max_clamped=True,enabled=False)
                                indexsorowgroup=None
                                for SourceGroup in source["Sources"]:
                                    so=SourceGroup["sceneItemIndex"]
                                    if indexsorowgroup==None: 
                                        with dpg.table_row(parent=TableItem,show=False,label="G"+str(c)+str(s)+str(gr)+str(so),before=oldindexrow) as indexsorowgroup:
                                            Sourcetxt=dpg.add_text(default_value=SourceGroup["sourceName"],indent=60)   
                                            dpg.bind_item_theme(Sourcetxt,TextTheme) 
                                            dpg.add_checkbox(tag=scene["Collection"]+SourceGroup["sourceName"]+str(SourceGroup["sceneItemId"])+"chkbox",callback=lambda s:ToggleUnivAddr(s))
                                            dpg.add_input_int(tag=scene["Collection"]+SourceGroup["sourceName"]+str(SourceGroup["sceneItemId"])+"Univ",width=130,default_value=1,min_value=1,max_value=32768,min_clamped=True,max_clamped=True,enabled=False)
                                            dpg.add_input_int(tag=scene["Collection"]+SourceGroup["sourceName"]+str(SourceGroup["sceneItemId"])+"Addr",width=130,default_value=1,min_value=1,max_value=512,min_clamped=True,max_clamped=True,enabled=False)
                                    else:    
                                        oldindexsorowgroup=indexsorowgroup
                                        with dpg.table_row(parent=TableItem,show=False,label="G"+str(c)+str(s)+str(gr)+str(so),before=oldindexsorowgroup) as indexsorowgroup:
                                            Sourcetxt=dpg.add_text(default_value=SourceGroup["sourceName"],indent=60)   
                                            dpg.bind_item_theme(Sourcetxt,TextTheme) 
                                            dpg.add_checkbox(tag=scene["Collection"]+SourceGroup["sourceName"]+str(SourceGroup["sceneItemId"])+"chkbox",callback=lambda s:ToggleUnivAddr(s))
                                            dpg.add_input_int(tag=scene["Collection"]+SourceGroup["sourceName"]+str(SourceGroup["sceneItemId"])+"Univ",width=130,default_value=1,min_value=1,max_value=32768,min_clamped=True,max_clamped=True,enabled=False)
                                            dpg.add_input_int(tag=scene["Collection"]+SourceGroup["sourceName"]+str(SourceGroup["sceneItemId"])+"Addr",width=130,default_value=1,min_value=1,max_value=512,min_clamped=True,max_clamped=True,enabled=False) 
                            else:
                                with dpg.table_row(parent=TableItem,show=False,label="S"+str(c)+str(s)+str(so),before=oldindexrow) as indexsorow:
                                    Sourcetxt=dpg.add_text(default_value=source["sourceName"],indent=40)   
                                    dpg.bind_item_theme(Sourcetxt,TextTheme) 
                                    dpg.add_checkbox(tag=scene["Collection"]+source["sourceName"]+str(source["sceneItemId"])+"chkbox",callback=lambda s:ToggleUnivAddr(s))
                                    dpg.add_input_int(tag=scene["Collection"]+source["sourceName"]+str(source["sceneItemId"])+"Univ",width=130,default_value=1,min_value=1,max_value=32768,min_clamped=True,max_clamped=True)
                                    dpg.add_input_int(tag=scene["Collection"]+source["sourceName"]+str(source["sceneItemId"])+"Addr",width=130,default_value=1,min_value=1,max_value=512,min_clamped=True,max_clamped=True)
                        else:    
                            oldindexsorow=indexsorow
                            if source["isGroup"]:
                                gr=source["sceneItemIndex"]
                                with dpg.table_row(parent=TableItem,show=False,label="S"+str(c)+str(s)+str(so),before=oldindexsorow) as indexsorow:
                                    TreeNodeTable(source["sourceName"],40,"G"+str(c)+str(s)+str(gr),5)  
                                    dpg.add_checkbox(tag=scene["Collection"]+source["sourceName"]+str(source["sceneItemId"])+"chkbox",callback=lambda s:ToggleUnivAddr(s))
                                    dpg.add_input_int(tag=scene["Collection"]+source["sourceName"]+str(source["sceneItemId"])+"Univ",width=130,default_value=1,min_value=1,max_value=32768,min_clamped=True,max_clamped=True,enabled=False)
                                    dpg.add_input_int(tag=scene["Collection"]+source["sourceName"]+str(source["sceneItemId"])+"Addr",width=130,default_value=1,min_value=1,max_value=512,min_clamped=True,max_clamped=True,enabled=False)
                                indexsorowgroup=None
                                for SourceGroup in source["Sources"]:
                                    so=SourceGroup["sceneItemIndex"]
                                    if indexsorowgroup==None: 
                                        with dpg.table_row(parent=TableItem,show=False,label="G"+str(c)+str(s)+str(gr)+str(so),before=oldindexsorow) as indexsorowgroup:
                                            Sourcetxt=dpg.add_text(default_value=SourceGroup["sourceName"],indent=60)   
                                            dpg.bind_item_theme(Sourcetxt,TextTheme) 
                                            dpg.add_checkbox(tag=scene["Collection"]+SourceGroup["sourceName"]+str(SourceGroup["sceneItemId"])+"chkbox",callback=lambda s:ToggleUnivAddr(s))
                                            dpg.add_input_int(tag=scene["Collection"]+SourceGroup["sourceName"]+str(SourceGroup["sceneItemId"])+"Univ",width=130,default_value=1,min_value=1,max_value=32768,min_clamped=True,max_clamped=True,enabled=False)
                                            dpg.add_input_int(tag=scene["Collection"]+SourceGroup["sourceName"]+str(SourceGroup["sceneItemId"])+"Addr",width=130,default_value=1,min_value=1,max_value=512,min_clamped=True,max_clamped=True,enabled=False)
                                    else:    
                                        oldindexsorowgroup=indexsorowgroup
                                        with dpg.table_row(parent=TableItem,show=False,label="G"+str(c)+str(s)+str(gr)+str(so),before=oldindexsorowgroup) as indexsorowgroup:
                                            Sourcetxt=dpg.add_text(default_value=SourceGroup["sourceName"],indent=60)   
                                            dpg.bind_item_theme(Sourcetxt,TextTheme) 
                                            dpg.add_checkbox(tag=scene["Collection"]+SourceGroup["sourceName"]+str(SourceGroup["sceneItemId"])+"chkbox",callback=lambda s:ToggleUnivAddr(s))
                                            dpg.add_input_int(tag=scene["Collection"]+SourceGroup["sourceName"]+str(SourceGroup["sceneItemId"])+"Univ",width=130,default_value=1,min_value=1,max_value=32768,min_clamped=True,max_clamped=True,enabled=False)
                                            dpg.add_input_int(tag=scene["Collection"]+SourceGroup["sourceName"]+str(SourceGroup["sceneItemId"])+"Addr",width=130,default_value=1,min_value=1,max_value=512,min_clamped=True,max_clamped=True,enabled=False) 
                            else:
                                with dpg.table_row(parent=TableItem,show=False,label="S"+str(c)+str(s)+str(so),before=oldindexsorow) as indexsorow:
                                    Sourcetxt=dpg.add_text(default_value=source["sourceName"],indent=40)   
                                    dpg.bind_item_theme(Sourcetxt,TextTheme) 
                                    dpg.add_checkbox(tag=scene["Collection"]+source["sourceName"]+str(source["sceneItemId"])+"chkbox",callback=lambda s:ToggleUnivAddr(s))
                                    dpg.add_input_int(tag=scene["Collection"]+source["sourceName"]+str(source["sceneItemId"])+"Univ",width=130,default_value=1,min_value=1,max_value=32768,min_clamped=True,max_clamped=True)
                                    dpg.add_input_int(tag=scene["Collection"]+source["sourceName"]+str(source["sceneItemId"])+"Addr",width=130,default_value=1,min_value=1,max_value=512,min_clamped=True,max_clamped=True)           
        c=c+1

#Update Item OBS to Table
def UpdateTable(item,type,value):
    global OBSIt
    #item {Col=Collection,Sc=Scene,Source=Source}, type {a=Add,d=Delete,u=Upgrade}
    Rows=dpg.get_item_children(TableItem,1)
    if type=="a":   #Add item OBS to Table
        if item=="Col":
            #Add new Collection
            c=0
            indexalphabet=0
            found=0
            for row in Rows:
                if item in dpg.get_item_label(row):
                    TreeN=dpg.get_item_children(row,1)
                    if dpg.get_item_label(TreeN[0])=="Collections":
                        visibility=dpg.get_item_user_data(TreeN[0])
                    if dpg.get_item_label(TreeN[0])>value and found==0 and dpg.get_item_label(TreeN[0])!="Collections":
                        indexalphabet=row
                        found=1
                    c+=1
            with dpg.table_row(parent=TableItem,show=visibility,label="Col"+str(c),before=indexalphabet):
                TreeNodeTable(value,10,"Sc"+str(c))   

             #Add Scene OBS
            for scene in OBSIt.Scenes: 
                if scene["Collection"]==value:
                    s=scene["sceneIndex"]
                    with dpg.table_row(parent=TableItem,show=False,label="Sc"+str(c)+str(s),before=indexalphabet):
                        TreeNodeTable(scene["sceneName"],20,"S"+str(c)+str(s))
                    #Add Source's Scene OBS
                    for source in scene["Sources"]:
                        so=source["sceneItemId"]
                        with dpg.table_row(parent=TableItem,show=False,label="S"+str(c)+str(s)+str(so),before=indexalphabet):
                            Sourcetxt=dpg.add_text(default_value=source["sourceName"],indent=40)   
                            dpg.bind_item_theme(Sourcetxt,TextTheme) 
                            dpg.add_checkbox(tag=scene["Collection"]+source["sourceName"]+str(source["sceneItemId"])+"chkbox",callback=lambda s:ToggleUnivAddr(s))
                            dpg.add_input_int(tag=scene["Collection"]+source["sourceName"]+str(source["sceneItemId"])+"Univ",width=130,default_value=1,min_value=1,max_value=32768,min_clamped=True,max_clamped=True)
                            dpg.add_input_int(tag=scene["Collection"]+source["sourceName"]+str(source["sceneItemId"])+"Addr",width=130,default_value=1,min_value=1,max_value=512,min_clamped=True,max_clamped=True)
                           
                       
        if item=="Sc":
            #Add Scene
            s=0
            for scene in OBSIt.Scenes: 
                if scene["Collection"]==OBSIt.CurrentCollection:
                     if scene["sceneName"]==value:
                        s=scene["sceneIndex"]
            c=0
            found=0
            indexrow=0
            for row in Rows:
                if "Col" in dpg.get_item_label(row):
                    if found==0:
                        TreeN=dpg.get_item_children(row,1)
                        if dpg.get_item_label(TreeN[0])==OBSIt.CurrentCollection:
                            c=dpg.get_item_label(row)[3:]
                            visibility=dpg.get_item_user_data(TreeN[0])
                            found=1
                    else:
                        indexrow=row  
                        break      
                        

            with dpg.table_row(parent=TableItem,show=visibility,label="Sc"+str(c)+str(s),before=indexrow):
                TreeNodeTable(value,20,"S"+str(c)+str(s))            
        if item=="Source":
            #Add Source to Table
            found=0
            indexrow=None
            for row in Rows:
                if "Col" in dpg.get_item_label(row):
                    c=dpg.get_item_label(row)[3:]
                    TreeN=dpg.get_item_children(row,1)
                    if dpg.get_item_label(TreeN[0])==OBSIt.CurrentCollection:
                        
                        for rowscene in range(Rows.index(row)+1,len(Rows)):
                            if "Sc" in dpg.get_item_label(Rows[rowscene]):
                                TreeN=dpg.get_item_children(Rows[rowscene],1)
                                if dpg.get_item_label(TreeN[0])==value[0]:
                                    
                                    visibility=dpg.get_item_user_data(TreeN[0])
                                    for scene in OBSIt.Scenes: 
                                        if scene["Collection"]==OBSIt.CurrentCollection:
                                            if scene["sceneName"]==value[0]:
                                                s=scene["sceneIndex"] 
                                                for source in scene["Sources"]:
                                                    if source["sourceName"]==value[1] and source["sceneItemId"]==value[3]:
                                                        isGroup=source["isGroup"]
                                                        gr=source["sceneItemIndex"]

                                    so=value[2]         
                                    if rowscene+1>len(Rows)-1:
                                        beforer=0
                                    else:
                                        beforer=Rows[rowscene+1] 
                                    with dpg.table_row(parent=TableItem,show=visibility,label="S"+str(c)+str(s)+str(so),before=beforer):
                                        if isGroup:
                                            
                                            TreeNodeTable(value[1],40,"G"+str(c)+str(s)+str(gr),5)  
                                        else:    
                                            Sourcetxt=dpg.add_text(default_value=value[1],indent=40)   
                                            dpg.bind_item_theme(Sourcetxt,TextTheme) 
                                        dpg.add_checkbox(tag=OBSIt.CurrentCollection+value[1]+str(value[3])+"chkbox",callback=lambda s:ToggleUnivAddr(s))
                                        dpg.add_input_int(tag=OBSIt.CurrentCollection+value[1]+str(value[3])+"Univ",width=130,default_value=1,min_value=1,max_value=32768,min_clamped=True,max_clamped=True,enabled=False)
                                        dpg.add_input_int(tag=OBSIt.CurrentCollection+value[1]+str(value[3])+"Addr",width=130,default_value=1,min_value=1,max_value=512,min_clamped=True,max_clamped=True,enabled=False)
                                    found=1
                                    break
                                    
                                        
    
    if type=="u": #Update Item OBS from Table
        if item=="Col":
            pass
        if item=="Sc":
            #Update Name Scene
            found=0
            indexrow=None
            for row in Rows:
                if "Col" in dpg.get_item_label(row):
                    TreeN=dpg.get_item_children(row,1)
                    if dpg.get_item_label(TreeN[0])==OBSIt.CurrentCollection:
                        
                        for rowscene in range(Rows.index(row)+1,len(Rows)):
                            if item in dpg.get_item_label(Rows[rowscene]):
                                TreeN=dpg.get_item_children(Rows[rowscene],1)
                                
                                if dpg.get_item_label(TreeN[0])==value[0]:
                                    BtnLabel=dpg.get_item_children(TreeN[0],1)
                                    dpg.configure_item(TreeN[0],label=value[1])
                                    dpg.configure_item(BtnLabel[1],label=value[1])
                                    found=1
                                    break
                    if found==1:
                        break                

        if item=="Source":
            
            for row in Rows:
                if "Col" in dpg.get_item_label(row):
                    TreeN=dpg.get_item_children(row,1)
                    if dpg.get_item_label(TreeN[0])==OBSIt.CurrentCollection:
                        
                        for rowscene in range(Rows.index(row)+1,len(Rows)):
                            if "Sc" in dpg.get_item_label(Rows[rowscene]):
                                TreeN=dpg.get_item_children(Rows[rowscene],1)
                                if dpg.get_item_label(TreeN[0])==OBSIt.ActiveScene:
                                    for scene in OBSIt.Scenes: 
                                        if scene["Collection"]==OBSIt.CurrentCollection:
                                            if scene["sceneName"]==OBSIt.ActiveScene:
                                                quantsource=len(scene["Sources"]) 
                                                quantsource+=rowscene+1
                                                break                                    
                                    #Change Name Source
                                    for rowsource in range(rowscene+1,quantsource):
                                        Source=dpg.get_item_children(Rows[rowsource],1)
                                        if value[2]:
                                            if dpg.get_item_label(Source[0])==value[1]:
                                                GroupH=dpg.get_item_children(Source[0],1)
                                                BtnLabel=dpg.get_item_children(GroupH[1],1)
                                                dpg.configure_item(Source[0],label=value[0])
                                                dpg.configure_item(BtnLabel[1],label=value[0])
                                        else:
                                            if dpg.get_value(Source[0])==value[1]:
                                                dpg.set_value(Source[0],value[0])
                                    break
                                      

    if type=="r": #Reorder Item OBS from Table  
        
        if item=="Col":
            pass
        if item=="Sc":
            pass    
        if item=="Source":
            found=0
            indexsource=None
            indexscene=None
            nextscene=None
            for row in Rows:
                #Search Collection
                if "Col" in dpg.get_item_label(row):
                    c=dpg.get_item_label(row)[3:]
                    TreeN=dpg.get_item_children(row,1)
                    if dpg.get_item_label(TreeN[0])==OBSIt.CurrentCollection:
                        #Search Scene
                        for rowscene in range(Rows.index(row)+1,len(Rows)):
                            if "Sc" in dpg.get_item_label(Rows[rowscene]):
                                TreeN=dpg.get_item_children(Rows[rowscene],1)
                                if dpg.get_item_label(TreeN[0])==value[1]:
                                    visibility=dpg.get_item_user_data(TreeN[0])
                                    indexscene=rowscene+1
                                else:
                                    if indexscene!=None:
                                        nextscene=rowscene    
                        if nextscene==None:
                            nextscene=len(Rows) 

                        if indexscene!=None:               
                            for scene in OBSIt.Scenes: 
                                if scene["Collection"]==OBSIt.CurrentCollection:
                                    if scene["sceneName"]==value[1]:
                                        s=scene["sceneIndex"]
                                        break
                            
                            
                            #Search Source
                            for rowsource in range(indexscene,nextscene):
                                dpg.delete_item(Rows[rowsource])

                            NewRows=dpg.get_item_children(TableItem,1)    
                            if indexscene==len(NewRows):
                                oldindexrow=0
                            else:
                                oldindexrow=NewRows[indexscene]      
                                #Add Source's Scene OBS
                            indexsorow=None 
                            for source in scene["Sources"]:
                                so=source["sceneItemIndex"]
                                if indexsorow==None: 
                                    if source["isGroup"]:
                                        gr=source["sceneItemIndex"]
                                        with dpg.table_row(parent=TableItem,show=visibility,label="S"+str(c)+str(s)+str(so),before=oldindexrow) as indexsorow:
                                            TreeNodeTable(source["sourceName"],40,"G"+str(c)+str(s)+str(gr),5)  
                                            dpg.add_checkbox(tag=scene["Collection"]+source["sourceName"]+str(source["sceneItemId"])+"chkbox",default_value=source["ArtnetEnable"],callback=lambda s:ToggleUnivAddr(s))
                                            if source["ArtnetEnable"]:
                                                dpg.add_input_int(tag=scene["Collection"]+source["sourceName"]+str(source["sceneItemId"])+"Univ",width=130,default_value=source["Univ"],min_value=1,max_value=32768,min_clamped=True,max_clamped=True,enabled=True)
                                                dpg.add_input_int(tag=scene["Collection"]+source["sourceName"]+str(source["sceneItemId"])+"Addr",width=130,default_value=source["Addr"],min_value=1,max_value=512,min_clamped=True,max_clamped=True,enabled=True)
                                            else:    
                                                dpg.add_input_int(tag=scene["Collection"]+source["sourceName"]+str(source["sceneItemId"])+"Univ",width=130,default_value=1,min_value=1,max_value=32768,min_clamped=True,max_clamped=True,enabled=False)
                                                dpg.add_input_int(tag=scene["Collection"]+source["sourceName"]+str(source["sceneItemId"])+"Addr",width=130,default_value=1,min_value=1,max_value=512,min_clamped=True,max_clamped=True,enabled=False)
                                        indexsorowgroup=None
                                        for SourceGroup in source["Sources"]:
                                            so=SourceGroup["sceneItemIndex"]
                                            if indexsorowgroup==None: 
                                                with dpg.table_row(parent=TableItem,show=False,label="G"+str(c)+str(s)+str(gr)+str(so),before=oldindexrow) as indexsorowgroup:
                                                    Sourcetxt=dpg.add_text(default_value=SourceGroup["sourceName"],indent=60)   
                                                    dpg.bind_item_theme(Sourcetxt,TextTheme) 
                                                    dpg.add_checkbox(tag=scene["Collection"]+SourceGroup["sourceName"]+str(SourceGroup["sceneItemId"])+"chkbox",default_value=SourceGroup["ArtnetEnable"],callback=lambda s:ToggleUnivAddr(s))
                                                    if SourceGroup["ArtnetEnable"]:
                                                        dpg.add_input_int(tag=scene["Collection"]+SourceGroup["sourceName"]+str(SourceGroup["sceneItemId"])+"Univ",width=130,default_value=SourceGroup["Univ"],min_value=1,max_value=32768,min_clamped=True,max_clamped=True,enabled=True)
                                                        dpg.add_input_int(tag=scene["Collection"]+SourceGroup["sourceName"]+str(SourceGroup["sceneItemId"])+"Addr",width=130,default_value=SourceGroup["Addr"],min_value=1,max_value=512,min_clamped=True,max_clamped=True,enabled=True)
                                                    else:
                                                        dpg.add_input_int(tag=scene["Collection"]+SourceGroup["sourceName"]+str(SourceGroup["sceneItemId"])+"Univ",width=130,default_value=1,min_value=1,max_value=32768,min_clamped=True,max_clamped=True,enabled=False)
                                                        dpg.add_input_int(tag=scene["Collection"]+SourceGroup["sourceName"]+str(SourceGroup["sceneItemId"])+"Addr",width=130,default_value=1,min_value=1,max_value=512,min_clamped=True,max_clamped=True,enabled=False)
                                            else:    
                                                oldindexsorowgroup=indexsorowgroup
                                                with dpg.table_row(parent=TableItem,show=False,label="G"+str(c)+str(s)+str(gr)+str(so),before=oldindexsorowgroup) as indexsorowgroup:
                                                    Sourcetxt=dpg.add_text(default_value=SourceGroup["sourceName"],indent=60)   
                                                    dpg.bind_item_theme(Sourcetxt,TextTheme) 
                                                    dpg.add_checkbox(tag=scene["Collection"]+SourceGroup["sourceName"]+str(SourceGroup["sceneItemId"])+"chkbox",default_value=SourceGroup["ArtnetEnable"],callback=lambda s:ToggleUnivAddr(s))
                                                    if SourceGroup["ArtnetEnable"]:
                                                        dpg.add_input_int(tag=scene["Collection"]+SourceGroup["sourceName"]+str(SourceGroup["sceneItemId"])+"Univ",width=130,default_value=SourceGroup["Univ"],min_value=1,max_value=32768,min_clamped=True,max_clamped=True,enabled=True)
                                                        dpg.add_input_int(tag=scene["Collection"]+SourceGroup["sourceName"]+str(SourceGroup["sceneItemId"])+"Addr",width=130,default_value=SourceGroup["Addr"],min_value=1,max_value=512,min_clamped=True,max_clamped=True,enabled=True)
                                                    else:
                                                        dpg.add_input_int(tag=scene["Collection"]+SourceGroup["sourceName"]+str(SourceGroup["sceneItemId"])+"Univ",width=130,default_value=1,min_value=1,max_value=32768,min_clamped=True,max_clamped=True,enabled=False)
                                                        dpg.add_input_int(tag=scene["Collection"]+SourceGroup["sourceName"]+str(SourceGroup["sceneItemId"])+"Addr",width=130,default_value=1,min_value=1,max_value=512,min_clamped=True,max_clamped=True,enabled=False)             
                                    else:
                                        with dpg.table_row(parent=TableItem,show=visibility,label="S"+str(c)+str(s)+str(so),before=oldindexrow) as indexsorow:
                                            Sourcetxt=dpg.add_text(default_value=source["sourceName"],indent=40)   
                                            dpg.bind_item_theme(Sourcetxt,TextTheme) 
                                            dpg.add_checkbox(tag=scene["Collection"]+source["sourceName"]+str(source["sceneItemId"])+"chkbox",default_value=source["ArtnetEnable"],callback=lambda s:ToggleUnivAddr(s))
                                            if source["ArtnetEnable"]:
                                                dpg.add_input_int(tag=scene["Collection"]+source["sourceName"]+str(source["sceneItemId"])+"Univ",width=130,default_value=source["Univ"],min_value=1,max_value=32768,min_clamped=True,max_clamped=True,enabled=True)
                                                dpg.add_input_int(tag=scene["Collection"]+source["sourceName"]+str(source["sceneItemId"])+"Addr",width=130,default_value=source["Addr"],min_value=1,max_value=512,min_clamped=True,max_clamped=True,enabled=True)
                                            else:
                                                dpg.add_input_int(tag=scene["Collection"]+source["sourceName"]+str(source["sceneItemId"])+"Univ",width=130,default_value=1,min_value=1,max_value=32768,min_clamped=True,max_clamped=True,enabled=False)
                                                dpg.add_input_int(tag=scene["Collection"]+source["sourceName"]+str(source["sceneItemId"])+"Addr",width=130,default_value=1,min_value=1,max_value=512,min_clamped=True,max_clamped=True,enabled=False)
                                else:    
                                    oldindexsorow=indexsorow
                                    if source["isGroup"]:
                                        gr=source["sceneItemIndex"]
                                        with dpg.table_row(parent=TableItem,show=visibility,label="S"+str(c)+str(s)+str(so),before=oldindexsorow) as indexsorow:
                                            TreeNodeTable(source["sourceName"],40,"G"+str(c)+str(s)+str(gr),5)  
                                            dpg.add_checkbox(tag=scene["Collection"]+source["sourceName"]+str(source["sceneItemId"])+"chkbox",default_value=source["ArtnetEnable"],callback=lambda s:ToggleUnivAddr(s))
                                            if source["ArtnetEnable"]:
                                                dpg.add_input_int(tag=scene["Collection"]+source["sourceName"]+str(source["sceneItemId"])+"Univ",width=130,default_value=source["Univ"],min_value=1,max_value=32768,min_clamped=True,max_clamped=True,enabled=True)
                                                dpg.add_input_int(tag=scene["Collection"]+source["sourceName"]+str(source["sceneItemId"])+"Addr",width=130,default_value=source["Addr"],min_value=1,max_value=512,min_clamped=True,max_clamped=True,enabled=True)
                                            else:    
                                                dpg.add_input_int(tag=scene["Collection"]+source["sourceName"]+str(source["sceneItemId"])+"Univ",width=130,default_value=1,min_value=1,max_value=32768,min_clamped=True,max_clamped=True,enabled=False)
                                                dpg.add_input_int(tag=scene["Collection"]+source["sourceName"]+str(source["sceneItemId"])+"Addr",width=130,default_value=1,min_value=1,max_value=512,min_clamped=True,max_clamped=True,enabled=False)
                                        indexsorowgroup=None
                                        for SourceGroup in source["Sources"]:
                                            so=SourceGroup["sceneItemIndex"]
                                            if indexsorowgroup==None: 
                                                with dpg.table_row(parent=TableItem,show=False,label="G"+str(c)+str(s)+str(gr)+str(so),before=oldindexsorow) as indexsorowgroup:
                                                    Sourcetxt=dpg.add_text(default_value=SourceGroup["sourceName"],indent=60)   
                                                    dpg.bind_item_theme(Sourcetxt,TextTheme) 
                                                    dpg.add_checkbox(tag=scene["Collection"]+SourceGroup["sourceName"]+str(SourceGroup["sceneItemId"])+"chkbox",default_value=SourceGroup["ArtnetEnable"],callback=lambda s:ToggleUnivAddr(s))
                                                    if SourceGroup["ArtnetEnable"]:
                                                        dpg.add_input_int(tag=scene["Collection"]+SourceGroup["sourceName"]+str(SourceGroup["sceneItemId"])+"Univ",width=130,default_value=SourceGroup["Univ"],min_value=1,max_value=32768,min_clamped=True,max_clamped=True,enabled=True)
                                                        dpg.add_input_int(tag=scene["Collection"]+SourceGroup["sourceName"]+str(SourceGroup["sceneItemId"])+"Addr",width=130,default_value=SourceGroup["Addr"],min_value=1,max_value=512,min_clamped=True,max_clamped=True,enabled=True)
                                                    else:
                                                        dpg.add_input_int(tag=scene["Collection"]+SourceGroup["sourceName"]+str(SourceGroup["sceneItemId"])+"Univ",width=130,default_value=1,min_value=1,max_value=32768,min_clamped=True,max_clamped=True,enabled=False)
                                                        dpg.add_input_int(tag=scene["Collection"]+SourceGroup["sourceName"]+str(SourceGroup["sceneItemId"])+"Addr",width=130,default_value=1,min_value=1,max_value=512,min_clamped=True,max_clamped=True,enabled=False)
                                            else:    
                                                oldindexsorowgroup=indexsorowgroup
                                                with dpg.table_row(parent=TableItem,show=False,label="G"+str(c)+str(s)+str(gr)+str(so),before=oldindexsorowgroup) as indexsorowgroup:
                                                    Sourcetxt=dpg.add_text(default_value=SourceGroup["sourceName"],indent=60)   
                                                    dpg.bind_item_theme(Sourcetxt,TextTheme) 
                                                    dpg.add_checkbox(tag=scene["Collection"]+SourceGroup["sourceName"]+str(SourceGroup["sceneItemId"])+"chkbox",default_value=SourceGroup["ArtnetEnable"],callback=lambda s:ToggleUnivAddr(s))
                                                    if SourceGroup["ArtnetEnable"]:
                                                        dpg.add_input_int(tag=scene["Collection"]+SourceGroup["sourceName"]+str(SourceGroup["sceneItemId"])+"Univ",width=130,default_value=SourceGroup["Univ"],min_value=1,max_value=32768,min_clamped=True,max_clamped=True,enabled=True)
                                                        dpg.add_input_int(tag=scene["Collection"]+SourceGroup["sourceName"]+str(SourceGroup["sceneItemId"])+"Addr",width=130,default_value=SourceGroup["Addr"],min_value=1,max_value=512,min_clamped=True,max_clamped=True,enabled=True)
                                                    else:
                                                        dpg.add_input_int(tag=scene["Collection"]+SourceGroup["sourceName"]+str(SourceGroup["sceneItemId"])+"Univ",width=130,default_value=1,min_value=1,max_value=32768,min_clamped=True,max_clamped=True,enabled=False)
                                                        dpg.add_input_int(tag=scene["Collection"]+SourceGroup["sourceName"]+str(SourceGroup["sceneItemId"])+"Addr",width=130,default_value=1,min_value=1,max_value=512,min_clamped=True,max_clamped=True,enabled=False)             
                                    else:
                                        with dpg.table_row(parent=TableItem,show=visibility,label="S"+str(c)+str(s)+str(so),before=oldindexsorow) as indexsorow:
                                            Sourcetxt=dpg.add_text(default_value=source["sourceName"],indent=40)   
                                            dpg.bind_item_theme(Sourcetxt,TextTheme) 
                                            dpg.add_checkbox(tag=scene["Collection"]+source["sourceName"]+str(source["sceneItemId"])+"chkbox",default_value=source["ArtnetEnable"],callback=lambda s:ToggleUnivAddr(s))
                                            if source["ArtnetEnable"]:
                                                dpg.add_input_int(tag=scene["Collection"]+source["sourceName"]+str(source["sceneItemId"])+"Univ",width=130,default_value=source["Univ"],min_value=1,max_value=32768,min_clamped=True,max_clamped=True,enabled=True)
                                                dpg.add_input_int(tag=scene["Collection"]+source["sourceName"]+str(source["sceneItemId"])+"Addr",width=130,default_value=source["Addr"],min_value=1,max_value=512,min_clamped=True,max_clamped=True,enabled=True)
                                            else:
                                                dpg.add_input_int(tag=scene["Collection"]+source["sourceName"]+str(source["sceneItemId"])+"Univ",width=130,default_value=1,min_value=1,max_value=32768,min_clamped=True,max_clamped=True,enabled=False)
                                                dpg.add_input_int(tag=scene["Collection"]+source["sourceName"]+str(source["sceneItemId"])+"Addr",width=130,default_value=1,min_value=1,max_value=512,min_clamped=True,max_clamped=True,enabled=False)                 




                                
                                    
                            break 
                        break                
                                            

            
            


    if type=="d": #Delete Item OBS from Table  
        
        if item=="Col":
            #Delete Collection
            found=0
            indexrow=None
            for row in Rows:
                if item in dpg.get_item_label(row):
                    if found==0:
                        TreeN=dpg.get_item_children(row,1)
                        if dpg.get_item_label(TreeN[0])==value:
                            indexcoll=Rows.index(row)
                            found=1
                    else:
                        indexrow=Rows.index(row) 
                        break 

            if indexrow==None:
                indexrow=len(Rows) 

            for c in range(indexcoll,indexrow):
                dpg.delete_item(Rows[c])                

        if item=="Sc":
            #Delete Scene
            found=0
            indexrow=None
            for row in Rows:
                #Search Collection
                if "Col" in dpg.get_item_label(row):
                    TreeN=dpg.get_item_children(row,1)
                    if dpg.get_item_label(TreeN[0])==OBSIt.CurrentCollection:
                        #Search Scene
                        for rowscene in range(Rows.index(row)+1,len(Rows)):
                            if item in dpg.get_item_label(Rows[rowscene]):
                                
                                if found==0:
                                    TreeN=dpg.get_item_children(Rows[rowscene],1)
                                    if dpg.get_item_label(TreeN[0])==value:
                                        
                                        indexscene=rowscene
                                        found=1
                                else:
                                    indexrow=rowscene-1  
                                    break 

            if indexrow==None:
                indexrow=len(Rows)-1 
            if indexscene==indexrow:    
                dpg.delete_item(Rows[indexscene])
            else:    
                for c in range(indexscene,indexrow):
                    dpg.delete_item(Rows[c])
        
        if item=="Source":
            found=0
            indexsource=None
            for row in Rows:
                #Search Collection
                if "Col" in dpg.get_item_label(row):
                    TreeN=dpg.get_item_children(row,1)
                    if dpg.get_item_label(TreeN[0])==OBSIt.CurrentCollection:
                        #Search Scene
                        for rowscene in range(Rows.index(row)+1,len(Rows)):
                            if "Sc" in dpg.get_item_label(Rows[rowscene]):
                                TreeN=dpg.get_item_children(Rows[rowscene],1)
                                if value[4]:
                                    if dpg.get_item_label(TreeN[0])==OBSIt.ActiveScene:
                                        chkbox=OBSIt.CurrentCollection+value[1]+str(value[2])+"chkbox"
                                    
                                        #Search Source
                                        if rowscene+1==len(Rows)-1:
                                            indexsource=rowscene+1
                                        else:    
                                            for rowsource in range(rowscene+1,len(Rows)):
                                                if found==0:
                                                    Source=dpg.get_item_children(Rows[rowsource],1)
                                                    
                                                    if value[4]: #Check is Group or Group Source
                                                        if (dpg.get_value(Source[0])==value[1]) and dpg.get_item_alias(Source[1])==chkbox:
                                                            indexsource=rowsource
                                                            found=1
                                                else:
                                                    break
                                else:    
                                    if dpg.get_item_label(TreeN[0])==value[0]:
                                        chkbox=OBSIt.CurrentCollection+value[1]+str(value[2])+"chkbox"
                                        
                                        #Search Source
                                        if rowscene+1==len(Rows)-1:
                                            indexsource=rowscene+1
                                        else:    
                                            for rowsource in range(rowscene+1,len(Rows)):
                                                if found==0:
                                                    Source=dpg.get_item_children(Rows[rowsource],1)
                                                    
                                                    if value[3]: #Check is Group or Source
                                                        if dpg.get_item_label(Source[0])==value[1] and dpg.get_item_alias(Source[1])==chkbox:
                                                            indexsource=rowsource
                                                            found=1
                                                    else:
                                                        if (dpg.get_value(Source[0])==value[1]) and dpg.get_item_alias(Source[1])==chkbox:
                                                            indexsource=rowsource
                                                            found=1
                                                else:
                                                    break 
                                            

            dpg.delete_item(Rows[indexsource])
            
#Enable/Disable Autoconnect check
def ToggleAutoConnect():
    if dpg.get_value(AutoConnect):
        ticker.add_callback(callback)
    else:  
        ticker.remove_callback(callback)  

#Enable/Disable Universe Address fields of source
def ToggleUnivAddr(sender):
    alias=dpg.get_item_alias(sender)[:-6]
    if dpg.get_value(sender):
        dpg.configure_item(alias+"Univ",enabled=True)
        dpg.configure_item(alias+"Addr",enabled=True)
    else:
        dpg.configure_item(alias+"Univ",enabled=False)
        dpg.configure_item(alias+"Addr",enabled=False)

#Load Setting from config.json
def LoadSetting():
    global Universe,Address,OBSWsIPAddr,OBSWsPort,OBSWsPass,OBSIt,filename

    try:
        with open(filename, 'r') as f:
            data=json.load(f)
          

        OBSWsIPAddr=data["OBSWsIPAddr"]
        OBSWsPort=data["OBSWsPort"]
        OBSWsPass=data["OBSWsPass"]
        dpg.set_value(AutoConnect,data["AutoConnect"])
        if data["AutoConnect"]:
            ticker.add_callback(callback)
        dpg.set_value(GeneralUniv,data["GeneralUniv"])
        dpg.set_value(GeneralAddr,data["GeneralAddr"])
        Universe=dpg.get_value(GeneralUniv)
        Address=dpg.get_value(GeneralAddr)
    except:
        dpg.set_value(AutoConnect,False)
        dpg.set_value(GeneralUniv,Universe)
        dpg.set_value(GeneralAddr,Address)
        
        

    if dpg.get_value(Status)=="Connection Status: Connected": 
        # OBSIt.UnivGeneral=Universe
        # OBSIt.AddrGeneral=Address
        for scene in OBSIt.Scenes:
            for source in scene["Sources"]:
                try:
                    source["ArtnetEnable"]=data[scene["Collection"]+source["sourceName"]+str(source["sceneItemId"])+"chkbox"]
                    dpg.set_value(scene["Collection"]+source["sourceName"]+str(source["sceneItemId"])+"chkbox",data[scene["Collection"]+source["sourceName"]+str(source["sceneItemId"])+"chkbox"])
                    if data[scene["Collection"]+source["sourceName"]+str(source["sceneItemId"])+"chkbox"]:
                        source["Univ"]=data[scene["Collection"]+source["sourceName"]+str(source["sceneItemId"])+"Univ"]
                        source["Addr"]=data[scene["Collection"]+source["sourceName"]+str(source["sceneItemId"])+"Addr"]
                        dpg.set_value(scene["Collection"]+source["sourceName"]+str(source["sceneItemId"])+"Univ",data[scene["Collection"]+source["sourceName"]+str(source["sceneItemId"])+"Univ"])
                        dpg.set_value(scene["Collection"]+source["sourceName"]+str(source["sceneItemId"])+"Addr",data[scene["Collection"]+source["sourceName"]+str(source["sceneItemId"])+"Addr"])
                        dpg.configure_item(scene["Collection"]+source["sourceName"]+str(source["sceneItemId"])+"Univ",enabled=True)
                        dpg.configure_item(scene["Collection"]+source["sourceName"]+str(source["sceneItemId"])+"Addr",enabled=True)
                    else:
                        source["Univ"]=None
                        source["Addr"]=None    
                        dpg.set_value(scene["Collection"]+source["sourceName"]+str(source["sceneItemId"])+"Univ",1)
                        dpg.configure_item(scene["Collection"]+source["sourceName"]+str(source["sceneItemId"])+"Univ",enabled=False)
                        dpg.set_value(scene["Collection"]+source["sourceName"]+str(source["sceneItemId"])+"Addr",1)
                        dpg.configure_item(scene["Collection"]+source["sourceName"]+str(source["sceneItemId"])+"Addr",enabled=False)
                except:
                    source["Univ"]=None
                    source["Addr"]=None    
                    dpg.set_value(scene["Collection"]+source["sourceName"]+str(source["sceneItemId"])+"Univ",1)
                    dpg.configure_item(scene["Collection"]+source["sourceName"]+str(source["sceneItemId"])+"Univ",enabled=False)
                    dpg.set_value(scene["Collection"]+source["sourceName"]+str(source["sceneItemId"])+"Addr",1)
                    dpg.configure_item(scene["Collection"]+source["sourceName"]+str(source["sceneItemId"])+"Addr",enabled=False)        
                if source["isGroup"]:
                    for sourcegroup in source["Sources"]:
                        try:
                            sourcegroup["ArtnetEnable"]=data[scene["Collection"]+sourcegroup["sourceName"]+str(sourcegroup["sceneItemId"])+"chkbox"]
                            dpg.set_value(scene["Collection"]+sourcegroup["sourceName"]+str(sourcegroup["sceneItemId"])+"chkbox",data[scene["Collection"]+sourcegroup["sourceName"]+str(sourcegroup["sceneItemId"])+"chkbox"])
                            if data[scene["Collection"]+sourcegroup["sourceName"]+str(sourcegroup["sceneItemId"])+"chkbox"]:
                                sourcegroup["Univ"]=data[scene["Collection"]+sourcegroup["sourceName"]+str(sourcegroup["sceneItemId"])+"Univ"]
                                sourcegroup["Addr"]=data[scene["Collection"]+sourcegroup["sourceName"]+str(sourcegroup["sceneItemId"])+"Addr"]
                                dpg.set_value(scene["Collection"]+sourcegroup["sourceName"]+str(sourcegroup["sceneItemId"])+"Univ",data[scene["Collection"]+sourcegroup["sourceName"]+str(sourcegroup["sceneItemId"])+"Univ"])
                                dpg.set_value(scene["Collection"]+sourcegroup["sourceName"]+str(sourcegroup["sceneItemId"])+"Addr",data[scene["Collection"]+sourcegroup["sourceName"]+str(sourcegroup["sceneItemId"])+"Addr"])
                                dpg.configure_item(scene["Collection"]+sourcegroup["sourceName"]+str(sourcegroup["sceneItemId"])+"Univ",enabled=True)
                                dpg.configure_item(scene["Collection"]+sourcegroup["sourceName"]+str(sourcegroup["sceneItemId"])+"Addr",enabled=True)
                            else:
                                sourcegroup["Univ"]=None
                                sourcegroup["Addr"]=None    
                                dpg.set_value(scene["Collection"]+sourcegroup["sourceName"]+str(sourcegroup["sceneItemId"])+"Univ",1)
                                dpg.configure_item(scene["Collection"]+sourcegroup["sourceName"]+str(sourcegroup["sceneItemId"])+"Univ",enabled=False)
                                dpg.set_value(scene["Collection"]+sourcegroup["sourceName"]+str(sourcegroup["sceneItemId"])+"Addr",1)
                                dpg.configure_item(scene["Collection"]+sourcegroup["sourceName"]+str(sourcegroup["sceneItemId"])+"Addr",enabled=False)
                        except:
                            sourcegroup["Univ"]=None
                            sourcegroup["Addr"]=None    
                            dpg.set_value(scene["Collection"]+sourcegroup["sourceName"]+str(sourcegroup["sceneItemId"])+"Univ",1)
                            dpg.configure_item(scene["Collection"]+sourcegroup["sourceName"]+str(sourcegroup["sceneItemId"])+"Univ",enabled=False)
                            dpg.set_value(scene["Collection"]+sourcegroup["sourceName"]+str(sourcegroup["sceneItemId"])+"Addr",1)
                            dpg.configure_item(scene["Collection"]+sourcegroup["sourceName"]+str(sourcegroup["sceneItemId"])+"Addr",enabled=False)

#Apply and Save to config.json
def ApplySaveSetting():
    global Universe,Address,OBSWsIPAddr,OBSWsPort,OBSWsPass,OBSIt,filename
    
    address=dpg.get_value(IPAddr)
    address=str(address[0])+"."+str(address[1])+"."+str(address[2])+"."+str(address[3])
    OBSWsIPAddr=address
    OBSWsPort=dpg.get_value(Port)
    OBSWsPass=dpg.get_value(Password) 
    Universe=dpg.get_value(GeneralUniv)
    Address=dpg.get_value(GeneralAddr)
    
    Sourcevalue={}

    if dpg.get_value(Status)=="Connection Status: Connected": 
        OBSIt.UnivGeneral=Universe
        OBSIt.AddrGeneral=Address
        Receiver.Pause()
        for scene in OBSIt.Scenes:
            for source in scene["Sources"]:
                if dpg.get_value(scene["Collection"]+source["sourceName"]+str(source["sceneItemId"])+"chkbox"):
                    source["ArtnetEnable"]=True
                    source["Univ"]=dpg.get_value(scene["Collection"]+source["sourceName"]+str(source["sceneItemId"])+"Univ")
                    source["Addr"]=dpg.get_value(scene["Collection"]+source["sourceName"]+str(source["sceneItemId"])+"Addr")
                    Sourcevalue[scene["Collection"]+source["sourceName"]+str(source["sceneItemId"])+"chkbox"]=True
                    Sourcevalue[scene["Collection"]+source["sourceName"]+str(source["sceneItemId"])+"Univ"]=dpg.get_value(scene["Collection"]+source["sourceName"]+str(source["sceneItemId"])+"Univ")
                    Sourcevalue[scene["Collection"]+source["sourceName"]+str(source["sceneItemId"])+"Addr"]=dpg.get_value(scene["Collection"]+source["sourceName"]+str(source["sceneItemId"])+"Addr")
                else:
                    Sourcevalue[scene["Collection"]+source["sourceName"]+str(source["sceneItemId"])+"chkbox"]=False
                    Sourcevalue[scene["Collection"]+source["sourceName"]+str(source["sceneItemId"])+"Univ"]=None
                    Sourcevalue[scene["Collection"]+source["sourceName"]+str(source["sceneItemId"])+"Addr"]=None
                if source["isGroup"]:
                    for sourcegroup in source["Sources"]:
                        if dpg.get_value(scene["Collection"]+sourcegroup["sourceName"]+str(sourcegroup["sceneItemId"])+"chkbox"):
                            sourcegroup["ArtnetEnable"]=True
                            sourcegroup["Univ"]=dpg.get_value(scene["Collection"]+sourcegroup["sourceName"]+str(sourcegroup["sceneItemId"])+"Univ")
                            sourcegroup["Addr"]=dpg.get_value(scene["Collection"]+sourcegroup["sourceName"]+str(sourcegroup["sceneItemId"])+"Addr")
                            Sourcevalue[scene["Collection"]+sourcegroup["sourceName"]+str(sourcegroup["sceneItemId"])+"chkbox"]=True
                            Sourcevalue[scene["Collection"]+sourcegroup["sourceName"]+str(sourcegroup["sceneItemId"])+"Univ"]=dpg.get_value(scene["Collection"]+sourcegroup["sourceName"]+str(sourcegroup["sceneItemId"])+"Univ")
                            Sourcevalue[scene["Collection"]+sourcegroup["sourceName"]+str(sourcegroup["sceneItemId"])+"Addr"]=dpg.get_value(scene["Collection"]+sourcegroup["sourceName"]+str(sourcegroup["sceneItemId"])+"Addr")
                        else:
                            Sourcevalue[scene["Collection"]+sourcegroup["sourceName"]+str(sourcegroup["sceneItemId"])+"chkbox"]=False
                            Sourcevalue[scene["Collection"]+sourcegroup["sourceName"]+str(sourcegroup["sceneItemId"])+"Univ"]=None
                            Sourcevalue[scene["Collection"]+sourcegroup["sourceName"]+str(sourcegroup["sceneItemId"])+"Addr"]=None    
       
        Receiver.UpdateOBS(OBSIt)
        Receiver.Start()
        
    data = {
        "OBSWsIPAddr":OBSWsIPAddr,
        "OBSWsPort":OBSWsPort,
        "OBSWsPass":OBSWsPass,
        "AutoConnect":dpg.get_value(AutoConnect),
        "GeneralUniv":dpg.get_value(GeneralUniv),
        "GeneralAddr":dpg.get_value(GeneralAddr)
    }

    data.update(Sourcevalue)
    
    json_object = json.dumps(data, indent=4)

    # Writing to config.json
    with open(filename, "w") as outfile:
        outfile.write(json_object) 
   
        

    dpg.configure_item(modalpopup, show=True)
    sleep(1)
    dpg.configure_item(modalpopup, show=False)

                        

#Window UI                    
with dpg.window() as Primary:
    
    with dpg.tab_bar():
        with dpg.tab(label="OBS Websocket Setting") as Tab1: 
            with dpg.child_window(autosize_x=True,height=-45):
                with dpg.group(horizontal=True,pos=[210,50],width=200):
                    dpg.add_text(default_value="IP Address")
                    IPAddr=dpg.add_input_intx(pos=[290,50],width=200,size=4,default_value=[127,0,0,1],min_value=0,max_value=255,min_clamped=True,max_clamped=True)
                with dpg.group(horizontal=True,pos=[210,100],width=200):
                    dpg.add_text(default_value="Port")
                    Port=dpg.add_input_int(pos=[290,100],width=200,default_value=4455,min_value=1,min_clamped=True,max_value=65534,max_clamped=True)
                with dpg.group(horizontal=True,pos=[210,150],width=200):
                    dpg.add_text(default_value="Password")
                    Password=dpg.add_input_text(pos=[290,150],width=200,default_value="Artnetobs",password=True,no_spaces=True) 
                with dpg.group(horizontal=True,pos=[210,250],width=200):
                    AutoConnect=dpg.add_checkbox(pos=[290,250],callback=lambda:ToggleAutoConnect())
                    AutoCTxt=dpg.add_text(default_value="AutoConnect")
                BtnConnect=dpg.add_button(label="Connect",pos=[290,300],width=200,height=50,callback=lambda: callback()) 
                Status=dpg.add_text(default_value="Connection Status: Disconnected",pos=[290,370]) 
                OBSVe=dpg.add_text(default_value="OBS Studio Version: -",pos=[290,390]) 
                OBSWs=dpg.add_text(default_value="OBS WebSocket Version: -",pos=[290,410])   
                               
        with dpg.tab(label="Artnet/DMX Address Setting") as Tab2:   
            with dpg.child_window(autosize_x=True,height=-45):  
                with dpg.group(horizontal=True,pos=[10,10]) as Tbgroup:
                    with dpg.table(pos=[200,50],width=745,height=-10,scrollY=True,row_background=True,reorderable=False,resizable=False,borders_innerV=True,borders_outerV=True,borders_innerH=True,borders_outerH=True) as TableItem:
                        dpg.add_table_column(label="OBS Item")
                        dpg.add_table_column(label="Artnet Enable",width=50,width_fixed=True)
                        dpg.add_table_column(label="Universe",width=100,width_fixed=True)
                        dpg.add_table_column(label="DMX Address",width=100,width_fixed=True)
                        with dpg.table_row(tag="General"):
                            GeneralTxt=dpg.add_text(default_value="General")    
                            dpg.add_text(default_value="")
                            GeneralUniv=dpg.add_input_int(width=130,default_value=1,min_value=1,max_value=32768,min_clamped=True,max_clamped=True)
                            GeneralAddr=dpg.add_input_int(width=130,default_value=1,min_value=1,max_value=512,min_clamped=True,max_clamped=True)
                        with dpg.table_row(label="ColRow"):
                            TNode=TreeNodeTable("Collections",0,"Col")
    
    dpg.add_text(default_value="Ver. 1.0",pos=[dpg.get_viewport_width()-60,5])
    dpg.add_button(label="View Manual",width=100,height=35,pos=[10,dpg.get_viewport_height()-75],callback=lambda:subprocess.Popen(folder+"/Manual.pdf",shell=True))
    ApplyBtn=dpg.add_button(label="Apply & Save",width=100,height=35,pos=[dpg.get_viewport_width()-116,dpg.get_viewport_height()-75],callback=lambda:ApplySaveSetting())
    with dpg.window(show=False,modal=True,no_move=True,no_title_bar=True,width=200,height=100,pos=[(dpg.get_viewport_width()/2)-100,(dpg.get_viewport_height()/2)-50]) as modalpopup:
        dpg.add_text(default_value="Saved", indent=70,pos=[50,33])
        #dpg.add_button(label="Close", indent=63, callback=lambda: dpg.configure_item(modalpopup, show=False))
    


dpg.set_primary_window(Primary,True)
dpg.bind_font(default_font)
dpg.bind_item_font(GeneralTxt,bold_font)
dpg.bind_theme(MainTheme)
dpg.bind_item_theme(Port,PortTheme)
dpg.bind_item_theme(GeneralTxt,TextTheme)
dpg.bind_item_theme(AutoCTxt,AutoCTheme)
dpg.bind_item_theme(Tbgroup,GroupTheme)
dpg.bind_item_theme(modalpopup,ModalTheme)
dpg.bind_item_theme(BtnConnect,BtnConnectTheme)


LoadSetting()



#dpg.show_style_editor()
# dpg.show_imgui_demo()
#dpg.show_item_registry()
dpg.show_viewport(maximized=True)
dpg.start_dearpygui()
dpg.destroy_context()