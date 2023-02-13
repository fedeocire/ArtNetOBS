import dearpygui.dearpygui as dpg

class TreeNodeTable():

    def treenodeopen(self):
        State=dpg.get_item_user_data(self.__TNode)
        Row=dpg.get_item_parent(self.__TNode)
        Table=dpg.get_item_parent(Row)
        Rows=dpg.get_item_children(Table,1)
        Rowindex=Rows.index(Row)
        Rows=Rows[Rowindex+1:]
        Groupletter=len(self.__group)
        if State==False:
            for row in Rows:
                if dpg.get_item_label(row)[0:Groupletter]==self.__group:
                    dpg.configure_item(row,show=True)
                    # TreeN=dpg.get_item_children(row,1)
                    # print(dpg.get_item_label(TreeN[0]))
                    # if dpg.is_item_toggled_open(TreeN[0]):
                    #     print("aperto")
                    # else:
                    #     print("chiuso")    
                    
            dpg.set_item_user_data(self.__TNode,True)
            if self.__FramePad>0:
                GroupH=dpg.get_item_children(self.__TNode,1)
                btnChild=dpg.get_item_children(GroupH[1],1)
                dpg.configure_item(btnChild[0],direction=dpg.mvDir_Down)
            else:    
                btnChild=dpg.get_item_children(self.__TNode,1)
                dpg.configure_item(btnChild[0],direction=dpg.mvDir_Down)
    
        else:
            for row in Rows:
                if self.__group=="Col":
                    dpg.configure_item(row,show=False)
                    Children=dpg.get_item_children(row,1)
                    for child in Children:
                        dpg.set_item_user_data(child,False)
                        btnChild=dpg.get_item_children(child,1)
                        if len(btnChild)==2:
                            if dpg.get_item_type(btnChild[0])=="mvAppItemType::mvSpacer":
                                btnChild=dpg.get_item_children(btnChild[1],1)
                                dpg.configure_item(btnChild[0],direction=dpg.mvDir_Right)
                            else:    
                                dpg.configure_item(btnChild[0],direction=dpg.mvDir_Right)
                else:    
                    labelrow=dpg.get_item_label(row)
                    if labelrow[0:Groupletter]==self.__group:
                        dpg.configure_item(row,show=False)
                        Treechildren=dpg.get_item_children(row,1)
                        for tree in Treechildren:
                            dpg.set_item_user_data(tree,False)
                            btnChild=dpg.get_item_children(tree,1)
                            if len(btnChild)==2:
                                if dpg.get_item_type(btnChild[0])=="mvAppItemType::mvSpacer":
                                    btnChild=dpg.get_item_children(btnChild[1],1)
                                    dpg.configure_item(btnChild[0],direction=dpg.mvDir_Right)
                                else:    
                                    dpg.configure_item(btnChild[0],direction=dpg.mvDir_Right)
                        if labelrow[0:2]=="Sc":
                            index=Rows.index(row)+1
                            Source=Rows[index:]
                            Sourcerow=labelrow.replace("c","")
                            Groupsceneletter=len(Sourcerow)
                            for rowsource in Source:
                                lblrowsource=dpg.get_item_label(rowsource)
                                if lblrowsource[0:Groupsceneletter]==Sourcerow:
                                     dpg.configure_item(rowsource,show=False)
                                     
            dpg.set_item_user_data(self.__TNode,False)                    
            if self.__FramePad>0:
                GroupH=dpg.get_item_children(self.__TNode,1)
                btnChild=dpg.get_item_children(GroupH[1],1)
            else: 
                btnChild=dpg.get_item_children(self.__TNode,1)
            dpg.configure_item(btnChild[0],direction=dpg.mvDir_Right)            
        # if Rowindex!=len(Rows)-1:
        #     Rowindex+=1
        #     beforerow=Rows[Rowindex]
        # else:
        #     beforerow=0    
       

    def __init__(self,Label,Indent,Group,Framepadding=0):
        self.__Label=Label
        self.__group=Group
        self.__FramePad=Framepadding
        self.TOpen=False
        with dpg.theme() as TreeGroupTheme:
            with dpg.theme_component(dpg.mvGroup):
                dpg.add_theme_color(dpg.mvThemeCol_Button, (0, 0, 0, 0), category=dpg.mvThemeCat_Core)
                dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (0, 0, 0, 0), category=dpg.mvThemeCat_Core)
                dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, (0, 0, 0, 0), category=dpg.mvThemeCat_Core)
                dpg.add_theme_color(dpg.mvThemeCol_FrameBg, (72, 72, 85), category=dpg.mvThemeCat_Core)  
                dpg.add_theme_color(dpg.mvThemeCol_ChildBg, (43, 46, 56), category=dpg.mvThemeCat_Core)
                if Framepadding>0:
                    dpg.add_theme_style(dpg.mvStyleVar_FramePadding, 0,0, category=dpg.mvThemeCat_Core)
            
            
                     
                
        with dpg.item_handler_registry() as node_handlers:
            dpg.add_item_clicked_handler(callback=lambda: self.treenodeopen())
        
        if Framepadding>0:
            with dpg.group(label=Label,indent=Indent,user_data=False) as self.__TNode:
                dpg.add_spacer(height=2)
                with dpg.group(horizontal=True,horizontal_spacing=3):
                    dpg.add_button(arrow=True,direction=dpg.mvDir_Right)
                    dpg.add_button(label=Label)
        else:    
            with dpg.group(label=Label,horizontal=True,horizontal_spacing=3,indent=Indent,user_data=False) as self.__TNode:
                dpg.add_button(arrow=True,direction=dpg.mvDir_Right)
                dpg.add_button(label=Label)

        dpg.bind_item_theme(self.__TNode,TreeGroupTheme)    
        dpg.bind_item_handler_registry(self.__TNode,node_handlers)

