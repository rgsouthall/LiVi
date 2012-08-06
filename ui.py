# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

import bpy
import os
import bpy_extras.io_utils as io_utils
#from . import livi_class
from . import livi_export
from . import livi_calc
from . import livi_display

class SCENE_LiVi_Export_UI(bpy.types.Panel):
    bl_label = "LiVi Export"    
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"

    def draw(self, context):
        scene = bpy.context.scene
        layout = self.layout
        row = layout.row()
        col = row.column()
        col.label(text = 'Animation:')
        row.prop(scene, "livi_anim")
        row = layout.row()
        
        if int(scene.livi_anim) != 1:
            
            col = row.column()
            col.label(text = 'Period Type:')
            row.prop(scene, "livi_export_time_type")
        
            if scene.livi_export_time_type == "0":
                row = layout.row()
                col = row.column()
                col.label(text = 'Sky type:')
               
                row.prop(scene, "livi_export_sky_type")
                sky_type = int(scene.livi_export_sky_type)
               
                    
                    
                if sky_type < 3:
                    row = layout.row()
                    row.prop(scene, "livi_export_latitude")
                    row.prop(scene, "livi_export_longitude")
                    row = layout.row()
                    row.prop(scene, "livi_export_summer_enable")
                    if scene.livi_export_summer_enable:
                        row.prop(scene, "livi_export_summer_meridian")
                    else:
                        row.prop(scene, "livi_export_standard_meridian")
                    row = layout.row()
                    if int(scene.livi_anim) != "1":
                        row.label(text = 'Time:')
                    else:
                        row.label(text = 'Start:')
                    col = row.column()
                    col.prop(scene, "livi_export_start_month")
                    row = layout.row()
                    if scene.livi_export_start_month == "2":
                        row.prop(scene, "livi_export_start_day28")
                    elif scene.livi_export_start_month in (4, 6, 9, 11):
                        row.prop(scene, "livi_export_start_day30")
                    else:
                        row.prop(scene, "livi_export_start_day")
                        
                    row.prop(scene, "livi_export_start_hour")
                    
                elif sky_type == 4:
                    row = layout.row()
                    row.operator(SCENE_LiVi_HDR_Select.bl_idname, text="Select HDR File")
                    row.prop(scene, "livi_export_hdr_name")
            else:
                row = layout.row()
                row.operator(SCENE_LiVi_EPW_Select.bl_idname, text="Select EPW File")
                row.prop(scene, "livi_export_epw_name")
        else:
            col = row.column()
            col.label(text = 'Sky type:')
            row.prop(scene, "livi_export_sky_type_period")
            sky_type = int(scene.livi_export_sky_type_period)
            row = layout.row()
            row.label(text = 'Start:')
            col = row.column()
            col.prop(scene, "livi_export_start_month")
            row = layout.row()
            if scene.livi_export_start_month == "2":
                row.prop(scene, "livi_export_start_day28")
            elif scene.livi_export_start_month in (4, 6, 9, 11):
                row.prop(scene, "livi_export_start_day30")
            else:
                row.prop(scene, "livi_export_start_day")
                
            row.prop(scene, "livi_export_start_hour")
            row = layout.row()
            row.label(text = 'End:')
            col = row.column()
            col.prop(scene, "livi_export_end_month")
            row = layout.row()
            if scene.livi_export_end_month == "2":
                row.prop(scene, "livi_export_end_day28")
            elif scene.livi_export_end_month in ("4", "6", "9", "11"):
                row.prop(scene, "livi_export_end_day30")
            else:
                row.prop(scene, "livi_export_end_day")
                
            row.prop(scene, "livi_export_end_hour")
            row = layout.row()
            row.label(text = 'Interval (Hours)')
            row.prop(scene, "livi_export_interval")
            
        row = layout.row()
        col = row.column()
        col.label(text = 'Calculation Points:')
        row.prop(scene, "livi_export_calc_points")
        row = layout.row()
        row.operator("scene.livi_export", text="Export")

class SCENE_LiVi_HDR_Select(bpy.types.Operator, io_utils.ImportHelper):
    bl_idname = "scene.livi_hdr_select"
    bl_label = "Select HDR image"
    bl_description = "Select the angmap format HDR image file"
    filename = ""
    filename_ext = ".hdr; .HDR"
    filter_glob = bpy.props.StringProperty(default="*.hdr; *.HDR", options={'HIDDEN'})
    bl_register = True
    bl_undo = True

    def draw(self,context):
        layout = self.layout
        row = layout.row()
        row.label(text="Import HDR File with FileBrowser", icon='WORLD_DATA')
         
    def execute(self, context):
        scene = context.scene
        if ".hdr" in self.filepath or ".HDR" in self.filepath and " " not in self.filepath:
            scene.livi_export_hdr_name = self.filepath
        elif " " in self.filepath:
            self.report({'ERROR'}, "There is a space either in the HDR filename or its directory location. Remove this space and retry opening the file.")
        else:
            self.report({'ERROR'},"The HDR must be in Radiance RGBE format (*.hdr). Use Luminance-hdr to convert EXR to HDR.")
        return {'FINISHED'}

    def invoke(self,context,event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}
    
class SCENE_LiVi_EPW_Select(bpy.types.Operator, io_utils.ImportHelper):
    bl_idname = "scene.livi_epw_select"
    bl_label = "Select EPW file"
    bl_description = "Select the EnergyPlus weather file"
    filename = ""
    filename_ext = ".epwdat;.hdr;.epw;.EPW;.vec"
    # No spaces in the extension list
    filter_glob = bpy.props.StringProperty(default="*.epwdat;*.hdr;*.epw;*.EPW;*.vec", options={'HIDDEN'})
    bl_register = True
    bl_undo = True
    
    def draw(self,context):
        layout = self.layout
        row = layout.row()
        row.label(text="Import EPW File with FileBrowser", icon='WORLD_DATA')
        row = layout.row()

    def execute(self, context):
        scene = context.scene
        if  self.filepath.split(".")[-1] in ("epw", "EPW", "epwdat", "vec", "hdr"):
            scene.livi_export_epw_name = self.filepath
        if " " in self.filepath:
            self.report({'ERROR'}, "There is a space either in the EPW filename or its directory location. Remove this space and retry opening the file.")
        return {'FINISHED'}

    def invoke(self,context,event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}
        
class SCENE_LiVi_VEC_Select(bpy.types.Operator, io_utils.ImportHelper):
    bl_idname = "scene.livi_vec_select"
    bl_label = "Select VEC file"
    bl_description = "Select the generated VEC file"
    filename = ""
    filename_ext = ".vec"
    # No spaces in the extension list
    filter_glob = bpy.props.StringProperty(default="*.vec", options={'HIDDEN'})
    bl_register = True
    bl_undo = True
    
    def draw(self,context):
        layout = self.layout
        row = layout.row()
        row.label(text="Import VEC file with fileBrowser", icon='WORLD_DATA')
        row = layout.row()

    def execute(self, context):
        scene = context.scene
        if  self.filepath.split(".")[-1] in ("vec"):
            scene.livi_calc_vec_name = self.filepath
        if " " in self.filepath:
            self.report({'ERROR'}, "There is a space either in the VEC filename or its directory location. Remove this space and retry opening the file.")
        return {'FINISHED'}

    def invoke(self,context,event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

class SCENE_LiVi_Export(bpy.types.Operator, io_utils.ExportHelper):
    bl_idname = "scene.livi_export"
    bl_label = "Export"
    bl_description = "Export the scene to the Radiance file format"
    bl_register = True
    bl_undo = True
    
    def invoke(self, context, event):
        global lexport
        if bpy.data.filepath:
            scene = context.scene
            if scene.livi_export_time_type == "0" or scene.livi_anim == "1":

                if scene.livi_anim == "1":
                    scene['skytype'] = int(scene.livi_export_sky_type_period)
                else:
                    scene['skytype'] = int(scene.livi_export_sky_type)
                
                if scene.livi_export_start_month == 2:
                    startD = scene.livi_export_start_day28
                elif scene.livi_export_start_month in (4, 6, 9, 11):
                    startD = scene.livi_export_start_day30
                else:
                    startD = scene.livi_export_start_day        
                if scene.livi_export_summer_enable == True:
                    TZ = scene.livi_export_summer_meridian
                else:
                    TZ = scene.livi_export_standard_meridian
                    
            elif scene.livi_export_time_type == "1":
                startD = 1
                TZ = 0
                scene['skytype'] = 6
                if scene.livi_export_epw_name == "":
                    self.report({'ERROR'},"Select an EPW weather file.")
                    return {'FINISHED'}

            scene['cp'] = int(scene.livi_export_calc_points)

            if bpy.context.object:
                if bpy.context.object.type == 'MESH' and bpy.context.object.hide == False and bpy.context.object.layers[0] == True:
                    bpy.ops.object.mode_set(mode = 'OBJECT')
            if " " not in bpy.data.filepath:
                lexport = livi_export.LiVi_e(bpy.data.filepath, scene, startD, TZ, self)   

                lexport.scene.display_legend = -1
                    
            elif " " in str(lexport.filedir):    
                self.report({'ERROR'},"The directory path containing the Blender file has a space in it.")
                return {'FINISHED'}
            elif " " in str(lexport.filename):
                self.report({'ERROR'},"The Blender filename has a space in it.")
                return {'FINISHED'}
            return {'FINISHED'}
        else:
            self.report({'ERROR'},"Save the Blender file before exporting")
            return {'FINISHED'} 
        
class SCENE_LiVi_Calc_UI(bpy.types.Panel):
    bl_label = "LiVi Calculator"    
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"       
    
    def draw(self, context):
        try:        
            if lexport.export == 1:
                layout = self.layout
                scene = context.scene
                row = layout.row()
                col = row.column()
                col.label(text = 'Simulation Metric:')
                if scene.livi_export_time_type == "0" or scene.livi_anim == "1":
                    if scene['skytype'] < 3 or scene['skytype'] == 4:
                        row.prop(scene, "livi_metric")
                        lexport.metric = scene.livi_metric
                    elif lexport.sky_type == 3:
                        row.prop(scene, "livi_metricdf")
                        lexport.metric = scene.livi_metricdf
                else:
                    row.prop(scene, "livi_metricdds")
                    lexport.metric = scene.livi_metricdds
                    
                if lexport.metric == "4" and lexport.scene.livi_export_time_type == "1":
                    if  scene.livi_export_epw_name.split(".")[-1] in ("hdr"):
                        row = layout.row()
                        row.operator(SCENE_LiVi_VEC_Select.bl_idname, text="Select VEC File")
                        row.prop(scene, "livi_calc_vec_name")
                    row = layout.row()
                    row.label(text = 'DA Occupancy:')
                    row.prop(scene, "livi_calc_da_weekdays")
                    row = layout.row()
                    row.label(text = 'Start Hour:')
                    row.prop(scene, "livi_calc_dastart_hour")
                    row = layout.row()
                    row.label(text = 'End Hour:')
                    row.prop(scene, "livi_calc_daend_hour")
                    row = layout.row()
                    row.label(text = 'Threshold Lux:')
                    row.prop(scene, "livi_calc_min_lux")
                row = layout.row()
                col = row.column()                
                col.label(text = 'Simulation Accuracy:')
                row.prop(scene, "livi_calc_acc") 
                if scene.livi_calc_acc == "3":
                    row = layout.row()
                    row.prop(scene, "livi_calc_custom_acc")
    
                row = layout.row()
                row.operator("scene.livi_rad_preview", text="Radiance Preview")
                row.operator("scene.livi_rad_calculate", text="Simulate")
                
        except Exception as e:
            print(e)

class SCENE_LiVi_Preview(bpy.types.Operator):
    bl_idname = "scene.livi_rad_preview"
    bl_label = "Radiance Preview"
    bl_description = "Preview the scene with Radiance"
    bl_register = True
    bl_undo = True
    
    def invoke(self, context, event):
        lprev = livi_calc.LiVi_c(lexport, self)
        return {'FINISHED'}

class SCENE_LiVi_Calculator(bpy.types.Operator):
    bl_idname = "scene.livi_rad_calculate"
    bl_label = "Radiance Calculation"
    bl_description = "Calculate values at the sensor points with Radiance"
    bl_register = True
    bl_undo = True
    
    def invoke(self, context, event):
        global lcalc
        scene = bpy.context.scene
        for geo in bpy.context.scene.objects:
            try:
                if geo['calc']:
                    pass
            except:
                geo['calc'] = 0
        scene['metric'] = lexport.metric
        lcalc = livi_calc.LiVi_c(lexport, self)   
        scene['unit'] = lcalc.unit[int(scene['metric'])]
        livi_display.rendview(0)
        lexport.scene.display_legend = -1
        return {'FINISHED'}

class SCENE_LiVi_Disp_UI(bpy.types.Panel):
    bl_label = "LiVi Display"    
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"    
    
    def draw(self, context):
        view = context.space_data
        scene = context.scene
          
        if scene.livi_display_panel == 1:
            layout = self.layout
            row = layout.row()
            row.operator("scene.livi_rad_display", text="Radiance Display")
            row.prop(view, "show_only_render")
            row.prop(scene, "livi_disp_3d")
            if int(context.scene.livi_disp_3d) == 1:
                row = layout.row()
                row.prop(scene, "livi_disp_3dlevel")
        
class SCENE_LiVi_Display(bpy.types.Operator):
    bl_idname = "scene.livi_rad_display"
    bl_label = "Radiance Results Display"
    bl_description = "Display the results on the sensor surfaces"
    bl_register = True
    bl_undo = True
       
    def invoke(self, context, event):
        try:
            ldisplay = livi_display.LiVi_d()
            bpy.ops.view3d.legend_display()
        except:
            self.report({'ERROR'},"No results available for display. Try re-running the calculation.")
            raise
        return {'FINISHED'}
 
class VIEW3D_OT_legend_display(bpy.types.Operator):
    '''Display the measurements made in the 'Measure' panel'''
    bl_idname = "view3d.legend_display"
    bl_label = "Display the measurements made in the" \
        " 'Measure' panel in the 3D View"
    bl_options = {'REGISTER'}
    
    def modal(self, context, event):
        self.event_type = event.type
        if context.scene.display_legend == -1:
            context.region.callback_remove(self._handle)
            return {'CANCELLED'}
        return {'PASS_THROUGH'}        
          
    def execute(self, context):
        from . import livi_display
        if context.area.type == 'VIEW_3D':
            context.window_manager.modal_handler_add(self)
            self._handle = context.region.callback_add(livi_display.rad_3D_legend, (self, context), 'POST_PIXEL')
            context.scene.display_legend = 0
            return {'RUNNING_MODAL'}
        else:
            self.report({'WARNING'}, "View3D not found, cannot run operator")
            return {'CANCELLED'}

class VIEW3D_OT_stats_display(bpy.types.Operator):
    '''Display the results statistics in the 3D view'''
    bl_idname = "view3d.stats_display"
    bl_label = "Display result statistics in the 3D View"
    bl_options = {'REGISTER'}
    
    def modal(self, context, event):
        self.event_type = event.type
        if context.scene.display_legend == -1:
            context.region.callback_remove(self._handle)
            return {'CANCELLED'}
        return {'PASS_THROUGH'}        
          
    def execute(self, context):
        from . import livi_display
        if context.area.type == 'VIEW_3D':
            context.window_manager.modal_handler_add(self)
            self._handle = context.region.callback_add(livi_display.res_stat, (self, context), 'POST_PIXEL')
            context.scene.display_legend = 0
            return {'RUNNING_MODAL'}
        else:
            self.report({'WARNING'}, "View3D not found, cannot run operator")
            return {'CANCELLED'} 
            
class SCENE_LiVi_framechange(bpy.types.Operator):
    '''Display the results statistics in the 3D view'''
    bl_idname = "scene.livi_framechange"
    bl_label = "Display result statistics in the 3D View"
    bl_options = {'REGISTER'}
    
    def execute(self, context):
        from . import livi_display
        livi_display.cyfc(self, context)

class IESPanel(bpy.types.Panel):
    bl_label = "LiVi IES file"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "data"
    
    @classmethod
    def poll(cls, context):
        if context.lamp or 'lightarray' in context.object.name:
            return True

    def draw(self, context):
        layout = self.layout
        lamp = bpy.context.active_object
        layout.operator("livi.ies_select") 
        layout.prop(lamp, "ies_name")
        row = layout.row()
        row.prop(lamp, "ies_unit")
        row = layout.row()
        row.prop(lamp, "ies_strength")

class IES_Select(bpy.types.Operator, io_utils.ImportHelper):
    bl_idname = "livi.ies_select"
    bl_label = "Select IES file"
    bl_description = "Select the lamp IES file"
    filename = ""
    filename_ext = ".ies; .IES"
    filter_glob = bpy.props.StringProperty(default="*.ies; *.IES", options={'HIDDEN'})
    bl_register = True
    bl_undo = True

    def draw(self,context):
        layout = self.layout
        row = layout.row()
        row.label(text="Open an IES File with the file browser", icon='WORLD_DATA')
         
    def execute(self, context):
        lamp = bpy.context.active_object
        if " " not in self.filepath:
            lamp['ies_name'] = self.filepath
        else:
            self.report({'ERROR'}, "There is a space either in the EPW filename or its directory location. Remove this space and retry opening the file.")
        return {'FINISHED'}

    def invoke(self,context,event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}
        
# Derived from the NodeTree base type, similar to Menu, Operator, Panel, etc.
class MyCustomTree(bpy.types.NodeTree):
    # Description string
    '''A custom node tree type that will show up in the node editor header'''
    # Optional identifier string. If not explicitly defined, the python class name is used.
    bl_idname = 'CustomTreeType'
    # Label for nice name display
    bl_label = 'Custom Node Tree'
    # Icon identifier
    # NOTE: If no icon is defined, the node tree will not show up in the editor header!
    #       This can be used to make additional tree types for groups and similar nodes (see below)
    #       Only one base tree class is needed in the editor for selecting the general category
    bl_icon = 'NODETREE'
# Derived from the Node base type.
class MyCustomNode(bpy.types.Node):
    # Description string
    '''A custom node'''
    # Optional identifier string. If not explicitly defined, the python class name is used.
    bl_idname = 'CustomNodeType'
    # Label for nice name display
    bl_label = 'Custom Node'
    # Icon identifier
    bl_icon = 'SOUND'    
