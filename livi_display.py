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


import bpy, blf, colorsys, bgl, math, time
from bpy_extras import image_utils
from . import livi_export

class LiVi_d(livi_export.LiVi_e):
    def __init__(self):
        self.scene = bpy.context.scene
        try:
            self.scene['livi_disp_3d'] = self.scene['livi_disp_3d']
        except:
            self.scene['livi_disp_3d'] = 0
        self.clearscened()
        self.rad_display()
            
    def rad_display(self):
        for a in bpy.app.handlers.frame_change_pre:
            bpy.app.handlers.frame_change_pre.remove(a)
        for a in bpy.app.handlers.frame_change_pre:
            bpy.app.handlers.frame_change_pre.remove(a)  
            
        bpy.app.handlers.frame_change_pre.append(cyfc1)    
        bpy.app.handlers.frame_change_pre.append(bpy.ops.view3d.stats_display())
    
        j = 0 
        o = 0
        obcalclist = []
        cfs = []
        obreslist = []
        imagelist = []
        
        for geo in self.scene.objects:
            try:
                if geo['calc'] == 1:
                    geo.select = True
                    bpy.ops.object.mode_set(mode = 'OBJECT')
                    bpy.ops.object.select_all(action = 'DESELECT')
                    for face in geo.data.faces:
                        if face.index in geo['cfaces']:
                            cfs.append((o, face))
                    obcalclist.append(geo)
                    o = o + 1
            except:
                pass
      
        for frame in range(0, self.scene.frame_end + 1):
            for image in bpy.data.images:
                imagelist.append(image.name)
            if str(frame)+"p.hdr" in imagelist:
                image.reload
            else:
                image_utils.load_image(self.scene['newdir']+"/"+str(frame)+"p.hdr")
                
            bpy.ops.anim.change_frame(frame = frame)
            for obcalc in obcalclist: 
                for vc in obcalc.data.vertex_colors:
                    if frame == int(vc.name):
                        vc.active = 1
                        vc.active_render = 1                        
                    else:
                        vc.active = 0
                        vc.active_render = 0
                    vc.keyframe_insert("active")
                    vc.keyframe_insert("active_render")
                    
        bpy.ops.anim.change_frame(frame = 0)
        bpy.ops.object.select_all(action = 'DESELECT')
        bpy.context.scene.objects.active = None

        if self.scene['livi_disp_3d'] == 1:
            resvertco = []
            fextrude = []
            for i, geo in enumerate(self.scene.objects):
                if geo.type == 'MESH':
                    try:
                        if geo['calc'] == 1:
                            self.scene.objects.active = None
                            bpy.ops.object.select_all(action = 'DESELECT')
                            self.scene.objects.active = geo
                            geo.select = True
                            bpy.ops.object.mode_set(mode = 'EDIT')
                            bpy.context.tool_settings.mesh_select_mode = [False, False, True]
                            bpy.ops.mesh.select_all(action = 'DESELECT')
                            bpy.ops.object.mode_set(mode = 'OBJECT')
                            
                            for face in geo.data.faces:
                                if face.index in geo['cfaces']:
                                    face.select = True
                            bpy.ops.object.mode_set(mode = 'EDIT')  
                            bpy.ops.mesh.duplicate()
                            bpy.ops.mesh.separate()
                            bpy.ops.object.mode_set(mode = 'OBJECT')
                            self.scene.objects[0].name = geo.name+"res"
                            obreslist.append(self.scene.objects[0])
                            self.scene.objects[0]['res'] = 1
                            bpy.ops.object.select_all(action = 'DESELECT')
                            bpy.context.scene.objects.active = None
                    except Exception as e:
                        print(e)
                    
            for obres in obreslist:   
                self.scene.objects.active = obres
                obres.select = True
                fextrude = []
                resvertco = []
                bpy.ops.object.shape_key_add(None)
                for frame in range(0, self.scene.frame_end + 1):
                    bpy.ops.object.shape_key_add(None)
                    obres.active_shape_key.name = str(frame)
                       
                    if self.scene['cp'] == 0:
                        if frame == 0:
                            if len(obres.data.faces) > 1:
                                bpy.ops.object.mode_set(mode = 'EDIT')
                                bpy.ops.mesh.select_all(action = 'SELECT')
                                bpy.ops.mesh.extrude(type='FACES')
                                bpy.ops.object.mode_set(mode = 'OBJECT')
                                bpy.ops.object.select_all(action = 'DESELECT')
                                for face in obres.data.faces:
                                    if face.select == True:
                                        fextrude.append(face)
                                for vert in obres.data.vertices:
                                    resvertco.append((vert.co, vert.normal))
                        for fex in fextrude:
                            for vert in fex.vertices:
                                obres.active_shape_key.data[vert].co = resvertco[vert][0] + 0.1*resvertco[vert][1]*float(self.scene.livi_disp_3dlevel)*(0.75-colorsys.rgb_to_hsv(obres.data.vertex_colors[str(frame)].data[fex.index].color1[0], obres.data.vertex_colors[str(frame)].data[fex.index].color1[1], obres.data.vertex_colors[str(frame)].data[fex.index].color1[2])[0])
                            
                    elif self.scene['cp'] == 1:
                        for vert in obres.data.vertices:
                            k = 0
                            for face in obres.data.faces:
                                if vert.index in face.vertices and k == 0: 
                                    j = [j for j,x in enumerate(face.vertices) if vert.index == x][0]
                                    if j == 0:
                                        obres.active_shape_key.data[vert.index].co = obres.active_shape_key.data[vert.index].co + 0.1*float(self.scene.livi_disp_3dlevel)*(0.75-colorsys.rgb_to_hsv(obres.data.vertex_colors[str(frame)].data[face.index].color1[0], obres.data.vertex_colors[str(frame)].data[face.index].color1[1], obres.data.vertex_colors[str(frame)].data[face.index].color1[2])[0])*(vert.normal)
                                    if j == 1:
                                        obres.active_shape_key.data[vert.index].co = obres.active_shape_key.data[vert.index].co + 0.1*float(self.scene.livi_disp_3dlevel)*(0.75-colorsys.rgb_to_hsv(obres.data.vertex_colors[str(frame)].data[face.index].color2[0], obres.data.vertex_colors[str(frame)].data[face.index].color2[1], obres.data.vertex_colors[str(frame)].data[face.index].color2[2])[0])*(vert.normal)
                                    if j == 2:
                                        obres.active_shape_key.data[vert.index].co = obres.active_shape_key.data[vert.index].co + 0.1*float(self.scene.livi_disp_3dlevel)*(0.75-colorsys.rgb_to_hsv(obres.data.vertex_colors[str(frame)].data[face.index].color3[0], obres.data.vertex_colors[str(frame)].data[face.index].color3[1], obres.data.vertex_colors[str(frame)].data[face.index].color3[2])[0])*(vert.normal)
                                    if j == 3:
                                        obres.active_shape_key.data[vert.index].co = obres.active_shape_key.data[vert.index].co + 0.1*float(self.scene.livi_disp_3dlevel)*(0.75-colorsys.rgb_to_hsv(obres.data.vertex_colors[str(frame)].data[face.index].color4[0], obres.data.vertex_colors[str(frame)].data[face.index].color4[1], obres.data.vertex_colors[str(frame)].data[face.index].color4[2])[0])*(vert.normal)
                                    k = k + 1
    
        for frame in range(0, self.scene.frame_end + 1):
            bpy.ops.anim.change_frame(frame = frame)
            for obres in obreslist: 
                if self.scene.livi_disp_3d == 1:
                    for shape in obres.data.shape_keys.key_blocks:
                            if "Basis" not in shape.name:
                                if int(shape.name) == frame:
                                    shape.value = 1
                                    shape.keyframe_insert("value")
                                else:
                                    shape.value = 0
                                    shape.keyframe_insert("value")
                                
                for vc in obres.data.vertex_colors:
                    if frame == int(vc.name):
                        vc.active = 1
                        vc.active_render = 1
                        vc.keyframe_insert("active")
                        vc.keyframe_insert("active_render")
                    else:
                        vc.active = 0
                        vc.active_render = 0
                        vc.keyframe_insert("active")
                        vc.keyframe_insert("active_render")   
        bpy.ops.wm.save_mainfile(check_existing = False)  
        rendview(1)             
    
def rad_3D_legend(self, context):
    scene = bpy.context.scene
    if bpy.context.scene['metric'] == 2:
        lenres = int(math.floor(math.log10(max(scene['resmax']))) + 2)
    else:
        lenres = int(math.floor(math.log10(max(scene['resmax']))) + 2)
    font_id = 0  
    bgl.glEnable(bgl.GL_BLEND)
    bgl.glColor4f(1.0, 1.0, 1.0, 1.0)
    bgl.glLineWidth(2)
    bgl.glBegin(bgl.GL_POLYGON)                  
    bgl.glVertex2i(20, 20)
    bgl.glVertex2i(70 + lenres*7, 20)
    bgl.glVertex2i(70 + lenres*7, 440)
    bgl.glVertex2i(20, 440)
    bgl.glEnd()
    
    for i in range(20):
        h = 0.75 - 0.75*(i/19)
        bgl.glColor4f(colorsys.hsv_to_rgb(h, 1.0, 1.0)[0], colorsys.hsv_to_rgb(h, 1.0, 1.0)[1], colorsys.hsv_to_rgb(h, 1.0, 1.0)[2], 1.0)
        bgl.glBegin(bgl.GL_POLYGON)                  
        bgl.glVertex2i(20, (i*20)+20)
        bgl.glVertex2i(60, (i*20)+20)
        bgl.glVertex2i(60, (i*20)+40)
        bgl.glVertex2i(20, (i*20)+40)
        bgl.glEnd()
        if bpy.context.scene['metric'] == 2:
            singlelenres = int(math.log10(math.floor(min(scene['resmin'])+i*(max(scene['resmax'])-min(scene['resmin']))/19)+1))
        else:
            singlelenres = int(math.log10(math.floor(min(scene['resmin'])+i*(max(scene['resmax'])-min(scene['resmin']))/19)+1))
        blf.position(font_id, 60, (i*20)+25, 0)
        blf.size(font_id, 20, 48)
        bgl.glColor4f(0.0, 0.0, 0.0, 1.0)
        if bpy.context.scene['metric'] == 2:
            blf.draw(font_id, "  "*(lenres - singlelenres - 2) + str(round(min(scene['resmin'])+i*(max(scene['resmax'])-min(scene['resmin']))/19, 1)+1))
        else:
            blf.draw(font_id, "  "*(lenres - singlelenres - 1) + str(int(min(scene['resmin'])+i*(max(scene['resmax'])-min(scene['resmin']))/19)+1))        
        
    blf.position(font_id, 25, 425, 0)
    blf.size(font_id, 20, 56)
    bgl.glColor4f(0.0, 0.0, 0.0, 1.0)
    blf.draw(font_id, scene['unit'])
    bgl.glLineWidth(1)
    bgl.glDisable(bgl.GL_BLEND)
    bgl.glColor4f(0.0, 0.0, 0.0, 1.0)   
        
def res_stat(self, context):
    font_id = 0
    scene = bpy.context.scene
    curf = scene.frame_current
    if curf in range(bpy.context.scene.frame_start, bpy.context.scene.frame_end + 1):
        bgl.glColor4f(1.0, 1.0, 1.0, 0.8)
        blf.position(font_id, 20, 500, 0)
        blf.size(font_id, 20, 48)
        blf.draw(font_id, "Average: "+'%.1f' % (scene['resav'][curf]))
        blf.position(font_id, 20, 485, 0)
        blf.draw(font_id, "Maximum: "+'%.1f' % (scene['resmax'][curf]))
        blf.position(font_id, 20, 470, 0)
        blf.draw(font_id, "Minimum: "+'%.1f' % (scene['resmin'][curf]))

def cyfc1(self):
    scene = bpy.context.scene
    curf = scene.frame_current
    for materials in bpy.data.materials:
        try:
            nt = materials.node_tree
            nt.nodes["Attribute"].attribute_name = str(curf)
        except:
            pass  
        
    for world in bpy.data.worlds:
        try:        
            nt = world.node_tree
            nt.nodes['Environment Texture'].image.name = "World"
            nt.nodes['Environment Texture'].image.filepath = scene['newdir']+"/"+str(curf)+"p.hdr"
            nt.nodes['Environment Texture'].image.reload()
            bpy.data.worlds[0].node_tree.nodes["Background"].inputs[1].keyframe_insert('default_value')

            if scene.livi_export_geo_export == 1:
                nt.nodes['Environment Texture'].image.filepath = scene['newdir']+"/0p.hdr"
        except Exception as e:
            print(e, 'cyfc1')

def cyfc2(self):
    scene = bpy.context.scene
    curf = scene.frame_current
        
    for materials in bpy.data.materials:
        try:
            nt = materials.node_tree
            nt.nodes["Attribute"].attribute_name = str(curf)
        except:
            pass  
    bpy.data.worlds[0].use_nodes = 0
    time.sleep(1)
    bpy.data.worlds[0].use_nodes = 1
    
def rendview(i):
    for scrn in bpy.data.screens:
        if scrn.name == 'Default':
            bpy.context.window.screen = scrn
            for area in scrn.areas:
                if area.type == 'VIEW_3D':
                    for space in area.spaces:
                        if space.type == 'VIEW_3D':
                            space.viewport_shade = 'SOLID'
                            if i ==  1:
                                space.show_only_render = 1
                                space.show_textured_solid = 1
                            else:
                                space.show_only_render = 0
                                space.show_textured_solid = 0
