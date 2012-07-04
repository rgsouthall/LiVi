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

import bpy, os, math, subprocess, datetime, multiprocessing
from math import sin, cos, acos, asin, pi
from mathutils import Vector, Matrix
from subprocess import PIPE, Popen
try:
    import numpy as numpy
    np = 1
except:
    np = 0
nproc = multiprocessing.cpu_count()

class LiVi_bc(object):
    def __init__(self, filepath, scene):
        self.filepath = filepath
        self.filename = os.path.splitext(os.path.basename(self.filepath))[0]
        self.filedir = os.path.dirname(self.filepath)
        if not os.path.isdir(self.filedir+"/"+self.filename):
            os.makedirs(self.filedir+"/"+self.filename)        
        self.newdir = self.filedir+"/"+self.filename
        self.filebase = self.newdir+"/"+self.filename
        self.scene = scene
        self.scene['newdir'] = self.newdir
        
class LiVi_e(LiVi_bc):
    def __init__(self, filepath, scene, sd, tz, export_op):
        LiVi_bc.__init__(self, filepath, scene)
        self.scene = scene       
        self.simtimes = []
        self.TZ = tz
        self.StartD = sd
        self.scene.display_legend = -1
        self.clearscenee()
        self.clearscened()
        self.sky_type = int(scene.livi_export_sky_type)
        self.time_type = int(scene.livi_export_time_type)
        self.merr = 0

        if scene.livi_anim == "0":
            scene.frame_start = 0
            scene.frame_end = 0 
            if scene.livi_export_time_type == "0":
                self.starttime = datetime.datetime(2010, int(scene.livi_export_start_month), int(scene.livi_export_start_day), int(scene.livi_export_start_hour), 0)
            self.fe = 0
            self.frameend = 0

        elif scene.livi_anim == "1":
            self.starttime = datetime.datetime(2010, int(scene.livi_export_start_month), int(scene.livi_export_start_day), int(scene.livi_export_start_hour), 0)
            self.endtime = datetime.datetime(2010, int(scene.livi_export_end_month), int(scene.livi_export_end_day), int(scene.livi_export_end_hour), 0)
            self.hours = (self.endtime-self.starttime).seconds/3600
            scene.frame_start = 0
            scene.frame_end = int(self.hours/scene.livi_export_interval)
            self.fe = int(self.hours/scene.livi_export_interval)
            self.frameend = int(self.hours/scene.livi_export_interval)
        
        elif scene.livi_anim in ("2", "3", "4"):
            self.fe = scene.frame_end
            self.frameend = 0
            if scene.livi_export_time_type == "0":
                self.starttime = datetime.datetime(2010, int(scene.livi_export_start_month), int(scene.livi_export_start_day), int(scene.livi_export_start_hour), 0)
        
        if self.sky_type < 4:    
            self.skytypeparams = ("+s", "+i", "-c", "-c")[self.sky_type]
        
        self.rtrace = self.filebase+".rtrace"  
        
        if self.scene.livi_export_time_type == "0" and self.sky_type in (0, 1, 2, 3) or self.scene.livi_anim == "1":
            self.sunexport()
        
        elif self.sky_type == 4:
            self.hdrexport(self.scene.livi_export_hdr_name)
        
        elif self.scene.livi_export_time_type == "1" and self.scene.livi_anim != "1":
            self.clearscenee()            
            self.ddsskyexport()
        
        for frame in range(0, self.fe + 1):
            if scene.livi_anim == "4":
                self.radlights(frame)
            else:
                if frame == 0:
                    self.radlights(frame)
            
            if scene.livi_anim == "3":
                self.radmat(frame)
            else:
                if frame == 0:
                    self.radmat(frame)
        
        self.rtexport(export_op)
            
        for frame in range(0, self.fe + 1):  
            self.merr = 0
            if scene.livi_anim == "2":
                self.obexport(frame, [geo for geo in self.scene.objects if geo.type == 'MESH' and 'lightarray' not in geo.name and geo.hide == False and geo.layers[0] == True], 0, export_op) 
            if scene.livi_anim == "3":
                self.obmexport(frame, [geo for geo in self.scene.objects if geo.type == 'MESH' and 'lightarray' not in geo.name and geo.hide == False and geo.layers[0] == True], 0, export_op) 
            else:
                if frame == 0:
                    self.obexport(frame, [geo for geo in self.scene.objects if geo.type == 'MESH' and 'lightarray' not in geo.name and geo.hide == False and geo.layers[0] == True], 0, export_op)
        
            self.fexport(frame, export_op)
        
    def poly(self, fr):
        if self.scene.livi_anim == "2" or (self.scene.livi_anim == "3" and self.merr == 0):
            return(self.filebase+"-"+str(fr)+".poly")   
        else:
            return(self.filebase+"-0.poly")
     
    def obj(self, fr):
        if self.scene.livi_anim == "2":
            return(self.filebase+"-"+str(fr)+".obj")
        else:
            return(self.filebase+"-0.obj")
    
    def mesh(self, fr):
        if self.scene.livi_anim in ("2", "3"):
            return(self.filebase+"-"+str(fr)+".mesh")
        else:
            return(self.filebase+"-0.mesh")
    
    def mat(self, fr):
        if self.scene.livi_anim == "3":
            return(self.filebase+"-"+str(fr)+".mat")
        else:
            return(self.filebase+"-0.mat")
    
    def lights(self, fr):
        if self.scene.livi_anim == "4":
            return(self.filebase+"-"+str(fr)+".lights")
        else:
            return(self.filebase+"-0.lights")
    
    def sky(self, fr):
        if self.scene.livi_anim == "1":
            return(self.filebase+"-"+str(fr)+".sky")
        else:
            return(self.filebase+"-0.sky")
    
    def clearscenee(self):
        for sunob in [ob for ob in self.scene.objects if ob.type == 'LAMP' and ob.data.type == 'SUN']:
            self.scene.objects.unlink(sunob)
        
        for ob in [ob for ob in self.scene.objects if ob.type == 'MESH']:
            self.scene.objects.active = ob
            for vcol in ob.data.vertex_colors:
                bpy.ops.mesh.vertex_color_remove()
    
    def clearscened(self):    
        for ob in [ob for ob in self.scene.objects if ob.type == 'MESH']:
            try:
                if ob['res'] == 1:
                   self.scene.objects.unlink(ob)
            except Exception as e:
                print(e)
       
        for mesh in bpy.data.meshes:
            if mesh.users == 0:
                bpy.data.meshes.remove(mesh)
        
        for lamp in bpy.data.lamps:
            if lamp.users == 0:
                bpy.data.lamps.remove(lamp)
        
        for oldgeo in bpy.data.objects:
            if oldgeo.users == 0:
                bpy.data.objects.remove(oldgeo)
                
        for sk in bpy.data.shape_keys:
            if sk.users == 0:
                for keys in sk.keys():
                    keys.animation_data_clear()
                    
    def sparams(self, acc):
        if acc == "3":
            return(self.scene.livi_calc_custom_acc)
        else:
            if acc == "0":
                num = ("2", "256", "128", "128", "0.3", "1", "1", "1", "0", "1", "0.004")
            elif acc == "1":
                num = ("2", "1024", "512", "512", "0.15", "1", "1", "2", "1", "1", "0.001")
            elif acc == "2":
                num = ("3", "4098", "1024", "1024", "0.08", "1", "1", "3", "5", "1", "0.0003")
            return(" -ab %s -ad %s -ar %s -as %s -av 0 0 0 -aa %s -dj %s -ds %s -dr %s -ss %s -st %s -lw %s " %(num))
        
    def pparams(self, acc):
        if acc == "3":
            return(self.scene.livi_calc_custom_acc)
        else:
            if acc == "0":
                num = ("2", "256", "128", "128", "0.3", "1", "1", "1", "0", "1", "0.004")
            elif acc == "1":
                num = ("3", "1024", "512", "512", "0.15", "1", "1", "2", "1", "1", "0.001")
            elif acc == "2":
                num = ("3", "4098", "1024", "1024", "0.08", "1", "1", "3", "5", "1", "0.0003")
            return(" -ab %s -ad %s -ar %s -as %s -av 0 0 0 -aa %s -dj %s -ds %s -dr %s -ss %s -st %s -lw %s " %(num))
    
    def sunexport(self):
        hdr_skies = []
        for frame in range(0, self.frameend + 1):
            bpy.ops.time.end_frame_set = frame
            simtime = self.starttime + frame*datetime.timedelta(seconds = 3600*self.scene.livi_export_interval)
            self.simtimes.append(simtime)
            subprocess.call("gensky "+str(self.simtimes[frame].month)+" "+str(self.simtimes[frame].day)+" "+str(self.simtimes[frame].hour)+":"+str(self.simtimes[frame].minute)+str(self.TZ)+" -a "+str(self.scene.livi_export_latitude)+" -o "+str(self.scene.livi_export_longitude)+" "+self.skytypeparams+" > "+self.sky(frame), shell=True)
            deg2rad = 2*math.pi/360
            if self.scene.livi_export_summer_enable:
                DS = 1 
            else:
                DS = 0
            ([solalt, solazi]) = solarPosition(simtime.timetuple()[7], simtime.hour - DS + (simtime.minute)*0.016666, self.scene.livi_export_latitude, self.scene.livi_export_longitude) 
            if frame == 0:
                bpy.ops.object.lamp_add(type='SUN')
                sun = bpy.context.object
                sun.data.shadow_method = 'RAY_SHADOW'
                sun.data.shadow_ray_samples = 8
                sun.data.sky.use_sky = 1
                if self.scene['skytype'] == 0:
                    sun.data.shadow_soft_size = 0.1
                    sun.data.energy = 5
                elif self.scene['skytype'] == 1:
                    sun.data.shadow_soft_size = 1
                    sun.data.energy = 3
                sun.location = (0,0,10)
            sun.rotation_euler = (90-solalt)*deg2rad, 0, solazi*deg2rad
            sun.keyframe_insert(data_path = 'location', frame = frame)
            sun.keyframe_insert(data_path = 'rotation_euler', frame = frame)
            bpy.ops.object.select_all()
            if self.scene['skytype'] == 3:
                sun.data.energy = 0
                subprocess.call("gensky 12 25 07 "+"-b 22.86 -c"+" > "+self.sky(frame), shell=True)
            self.skyexport(open(self.sky(frame), "a"))           
            subprocess.call("oconv "+self.sky(frame)+" > "+self.filebase+"-"+str(frame)+"sky.oct", shell=True)
            subprocess.call("rpict -vta -vp 0 0 0 -vd 1 0 0 -vu 0 0 1 -vh 360 -vv 360 -x 1000 -y 1000 "+self.filebase+"-"+str(frame)+"sky.oct > "+self.newdir+"/"+str(frame)+".hdr", shell=True)
            hdr_skies.append(self.newdir+"/"+str(frame)+".hdr")
        
            self.hdrexport(hdr_skies)
                
    def hdrexport(self, hdr_skies):
        for frame, sky in enumerate(hdr_skies):
            if self.scene.world.texture_slots[0] == None:
                imgPath = sky
                img = bpy.data.images.load(imgPath)
                if len(hdr_skies) == 1:
                    img.source = 'FILE'
                else:
                    img.source = 'SEQUENCE'
                imtex = bpy.data.textures.new('Radsky', type = 'IMAGE')
                imtex.image = img
                imtex.factor_red = (0.05, 0.000001)[int(self.scene.livi_export_time_type)]
                imtex.factor_green = (0.05, 0.000001)[int(self.scene.livi_export_time_type)]
                imtex.factor_blue = (0.05, 0.000001)[int(self.scene.livi_export_time_type)]
                
                w = bpy.data.worlds['World']
                slot = w.texture_slots.add()
                slot.texture = imtex
                slot.use_map_horizon = True
                slot.use_map_blend = False
                slot.texture_coords = 'ANGMAP'
                
                bpy.context.scene.world.light_settings.use_environment_light = True
                bpy.context.scene.world.light_settings.use_indirect_light = False
                bpy.context.scene.world.light_settings.use_ambient_occlusion = True
                bpy.context.scene.world.light_settings.environment_energy = 1
                bpy.context.scene.world.light_settings.environment_color = 'SKY_COLOR'
                bpy.context.scene.world.light_settings.gather_method = 'APPROXIMATE'
                bpy.context.scene.world.light_settings.passes = 1
                bpy.context.scene.world.use_sky_real = True
                bpy.context.scene.world.use_sky_paper = False
                bpy.context.scene.world.use_sky_blend = False
                if self.scene.livi_export_time_type == "0":
                    bpy.context.scene.world.ambient_color = (0.04, 0.04, 0.04)
                else:
                    bpy.context.scene.world.ambient_color = (0.000001, 0.000001, 0.000001)
                bpy.context.scene.world.horizon_color = (0, 0, 0)
                bpy.context.scene.world.zenith_color = (0, 0, 0)
                render = bpy.context.scene.render
                render.use_raytrace = True
                render.use_textures = True
                render.use_shadows = True
                render.use_color_management = True
                bpy.ops.images.reload
            else:
                for im in bpy.data.images:
                    if ".hdr" in im.name or ".HDR" in im.name:
                        im.filepath = sky
                        bpy.ops.image.reload()
            if self.sky_type == 4:
                self.hdrsky(open(self.sky(frame), "w"), self.scene.livi_export_hdr_name)
            elif self.time_type == 1:
                self.hdrsky(open(self.sky(frame), "w"), sky)

    def skyexport(self, rad_sky):
        rad_sky.write("skyfunc glow skyglow\n0\n0\n")
        if self.scene['skytype'] < 3:
            rad_sky.write("4 .8 .8 1 0\n\n")
        else:
            rad_sky.write("4 1 1 1 0\n\n")    
        rad_sky.write("skyglow source sky\n0\n0\n4 0 0 1  180\n\n")
        rad_sky.write("skyfunc glow groundglow\n0\n0\n4 .8 1.1 .8  0\n\n")
        rad_sky.write("groundglow source ground\n0\n0\n4 0 0 -1  180\n\n")
        rad_sky.close()
        
    def ddsskyexport(self):
        if np == 0:
            vecvals = []
        else:
            vecvals = numpy.zeros((8766, 151))
        i = 0
        j = 0
        null = "0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0"
        prevline = b"0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0"
        if os.path.splitext(os.path.basename(self.scene.livi_export_epw_name))[1] in (".epw", ".EPW"):    
            epw = open(self.scene.livi_export_epw_name, "r")
            vecfile = open(self.newdir+"/"+os.path.splitext(os.path.basename(self.scene.livi_export_epw_name))[0]+".vec", "w")
            for line in epw:
                if i == 0:
                    lat = line.split(",")[6]
                    lon = -float(line.split(",")[7])
                    mer = -15*float(line.split(",")[8])
                elif i > 8 and float(line.split(",")[15]) > 0:
                    time = datetime.datetime(int(line.split(",")[0]), int(line.split(",")[1]), int(line.split(",")[2]), int(line.split(",")[3])-1, int(line.split(",")[4])-60)
                    dirnorm = line.split(",")[14]
                    diffhoz = line.split(",")[15]    
                    dglcmd = "gendaylit "+str(time.month)+" "+str(time.day)+" "+str(time.hour)+" -a "+str(lat)+" -o "+str(lon)+" -m "+str(mer)+" -W "+str(dirnorm)+" "+str(diffhoz)+" -O 1 | genskyvec -c 1 1 1 -m 1 |cut -f1 |tr '\n' ' '"
                    dglrun = Popen(dglcmd, shell = True, stdout = PIPE, stderr = PIPE).communicate()
        
                    if dglrun[1] == b'':
                        vecfile.write(str(time.hour)+" "+str(time.weekday())+" ")
                        vecfile.write(dglrun[0].decode()+"\n")
                        prevline = dglrun[0]
                    else:
                        if diffhoz == 0:
                            vecfile.write(str(time.hour)+" "+str(time.weekday())+" ")
                            vecfile.write(null+"\n")
                        else:
                            vecfile.write(str(time.hour)+" "+str(time.weekday())+" ")
#                            vecfile.write(prevline.decode()+"\n")
                            vecfile.write(null+"\n")
        
                i = i + 1
            
            vecfile.close()
            epw.close()
        
        if os.path.splitext(os.path.basename(self.scene.livi_export_epw_name))[1] in (".epw", ".EPW", ".vec"): 
            if os.path.splitext(os.path.basename(self.scene.livi_export_epw_name))[1] in (".vec"):  
                vecfile = open(self.scene.livi_export_epw_name, "r")
            else:
                vecfile = open(self.newdir+"/"+os.path.splitext(os.path.basename(self.scene.livi_export_epw_name))[0]+".vec", "r")
            if np == 0:
                for li, line in enumerate(vecfile):
                    vecvals.append([negneg(x) for x in line.strip("\n").strip("  ").split(" ")])
                vecfile.close()
            else:
                vecvals = numpy.fromfile(self.newdir+"/"+os.path.splitext(os.path.basename(self.scene.livi_export_epw_name))[0]+".vec", dtype = float, count = -1, sep = " ")
                vecvals = vecvals.reshape((-1, 148))
                vecvals[vecvals < 0] = 0
            
            if np == 0:
                vals = [sum(a) for a in zip(*vecvals)]
            else:
                vals = vecvals.sum(axis=0)
            skyrad = open(self.filebase+".whitesky", "w")    
            skyrad.write("void glow sky_glow \n0 \n0 \n4 1 1 1 0 \nsky_glow source sky \n0 \n0 \n4 0 0 1 180 \nvoid glow ground_glow \n0 \n0 \n4 1 1 1 0 \nground_glow source ground \n0 \n0 \n4 0 0 -1 180\n\n")
            skyrad.close()
            subprocess.call("oconv "+self.filebase+".whitesky > "+self.filebase+"-whitesky.oct", shell=True)
            subprocess.call("vwrays -ff -x 600 -y 600 -vta -vp 0 0 0 -vd 0 1 0 -vu 0 0 1 -vh 360 -vv 360 -vo 0 -va 0 -vs 0 -vl 0 | rtcontrib -bn 146 -fo -ab 0 -ad 512 -n "+str(nproc)+" -ffc $(vwrays -d -x 600 -y 600 -vta -vp 0 0 0 -vd 0 1 0 -vu 0 0 1 -vh 360 -vv 360 -vo 0 -va 0 -vs 0 -vl 0) -V+ -f tregenza.cal -b tbin -o p%d.hdr -m sky_glow "+self.filebase+"-whitesky.oct", shell = True)
            
            for j in range(0, 146):
                subprocess.call("pcomb -s "+str(vals[j+2])+" p"+str(j)+".hdr > ps"+str(j)+".hdr", shell = True)
                subprocess.call("rm  p"+str(j)+".hdr", shell = True) 
            subprocess.call("pcomb -h  ps*.hdr > "+self.newdir+"/"+os.path.splitext(os.path.basename(self.scene.livi_export_epw_name))[0]+".hdr", shell = True)    
            for j in range(0, 146):    
                subprocess.call("rm ps"+str(j)+".hdr" , shell = True) 

        self.hdrexport([self.newdir+"/"+os.path.splitext(os.path.basename(self.scene.livi_export_epw_name))[0]+".hdr"])
    
    
    def hdrsky(self, rad_sky, skyfile):
        rad_sky.write("# Sky material\nvoid colorpict hdr_env\n7 red green blue "+skyfile+" angmap.cal sb_u sb_v\n0\n0\n\nhdr_env glow env_glow\n0\n0\n4 1 1 1 0\n\nenv_glow bubble sky\n0\n0\n4 0 0 0 500\n\n")
        rad_sky.close()
        
    def radmat(self, frame):
        mats = bpy.data.materials
        self.scene.frame_set(frame)
        rad_mat = open(self.mat(frame), "w")
        for meshmat in mats:
            diff = [meshmat.diffuse_color[0]*meshmat.diffuse_intensity, meshmat.diffuse_color[1]*meshmat.diffuse_intensity, meshmat.diffuse_color[2]*meshmat.diffuse_intensity]
            if "calcsurf" in meshmat.name:
                meshmat.use_vertex_color_paint = 1
            if meshmat.use_shadeless == 1:
                rad_mat.write("# Antimatter material\n")
                rad_mat.write("void antimatter " + meshmat.name.replace(" ", "_") +"\n1 void\n0\n0\n\n")
                
            elif meshmat.use_transparency == False and meshmat.raytrace_mirror.use == True and meshmat.raytrace_mirror.reflect_factor >= 0.99:
                rad_mat.write("# Mirror material\n")
                rad_mat.write("void mirror " + meshmat.name.replace(" ", "_") +"\n0\n0\n")
                rad_mat.write("3 " + str(meshmat.mirror_color[0])+ " " +  str(meshmat.mirror_color[1]) + " " +
                                    str(meshmat.mirror_color[2]) + " " + "\n\n")
                
            elif meshmat.use_transparency == True and meshmat.transparency_method == 'RAYTRACE' and round(meshmat.raytrace_transparency.ior, 2) == 1.52 and meshmat.alpha >= 0.01 and meshmat.translucency == 0:
                rad_mat.write("# Glass material\n")
                rad_mat.write("void glass " + meshmat.name.replace(" ", "_") +"\n0\n0\n")
                rad_mat.write("3 %s %s %s %s" % (diff[0], diff[1], diff[2], "\n\n"))
                    
            elif meshmat.use_transparency == True and meshmat.transparency_method == 'RAYTRACE' and round(meshmat.raytrace_transparency.ior, 2) != 1.52 and meshmat.alpha >= 0.01 and meshmat.translucency == 0:
                rad_mat.write("# Dielectric material\n")
                rad_mat.write("void dielectric " + meshmat.name.replace(" ", "_") +"\n0\n0\n")
                rad_mat.write("5 %s %s %s %s" % (diff[0], diff[1], diff[2], " ") +
    				        str(meshmat.raytrace_transparency.ior) + " " + "0" + "\n\n")
                    
            elif meshmat.use_transparency == True and meshmat.alpha < 1.0 and meshmat.translucency > 0.001:
                rad_mat.write("# translucent material\n")
                rad_mat.write("void trans " + meshmat.name.replace(" ", "_")+"\n0\n0\n")
                rad_mat.write("7 %s %s %s %s" % (diff[0], diff[1], diff[2], " ") +
    				        str(meshmat.specular_intensity) + " " +
    				        str(1.0 - meshmat.specular_hardness/511.0) + " " +
    				        str(1.0 - meshmat.alpha) + " " +
                                            str(1.0 - meshmat.translucency) + "\n\n")
            
            elif meshmat.use_transparency == False and meshmat.raytrace_mirror.use == True and meshmat.raytrace_mirror.reflect_factor < 0.99:
                rad_mat.write("# Metal material\n")
                rad_mat.write("void metal " + meshmat.name.replace(" ", "_") +"\n0\n0\n")
                rad_mat.write("5 %s %s %s %s" % (diff[0], diff[1], diff[2], " ") + str(meshmat.specular_intensity) + " " +
                              str(1.0-meshmat.specular_hardness/511.0) + "\n\n")
            else:
                rad_mat.write("# Plastic material\n")
                rad_mat.write("void plastic " + meshmat.name.replace(" ", "_") +"\n0\n0\n")
                rad_mat.write("5 %s %s %s %s" % (diff[0], diff[1], diff[2], " ") + str(meshmat.specular_intensity) + " " +
                                   str(1.0-meshmat.specular_hardness/511.0) + "\n\n")
        rad_mat.close()

    def obexport(self,frame, obs, obno, export_op):
        self.scene.frame_current = frame
        rad_poly = open(self.poly(frame), 'w')
        if obno == 0:
            bpy.ops.export_scene.obj(filepath=self.obj(frame), check_existing=True, filter_glob="*.obj;*.mtl", use_selection=False, use_animation=False, use_apply_modifiers=True, use_edges=False, use_normals=True, use_uvs=True, use_materials=True, use_triangles=True, use_nurbs=True, use_vertex_groups=False, use_blen_objects=True, group_by_object=False, group_by_material=False, keep_vertex_order=True, global_scale=1.0, axis_forward='Y', axis_up='Z', path_mode='AUTO')
            objcmd = "obj2mesh -w -a "+self.mat(frame)+" "+self.obj(frame)+" "+self.mesh(frame)
            objrun = Popen(objcmd, shell = True, stderr = PIPE)
            for line in objrun.stderr:
                if 'fatal' in str(line):
                    self.merr = 1

        if self.merr == 0 and obno == 0:
            rad_poly.write("void mesh id \n1 "+self.mesh(frame)+"\n0\n0\n")

        if self.merr == 1:
            for geo in obs:
                geomatrix = geo.matrix_world
                for face in geo.data.faces:
                    try:
                        vertices = face.vertices[:]
                        rad_poly.write("# Polygon \n")
                        rad_poly.write(geo.data.materials[face.material_index].name.replace(" ", "_") + " polygon " + "poly_"+geo.data.name.replace(" ", "_")+"_"+str(face.index) + "\n")
                        rad_poly.write("0\n0\n"+str(3*len(face.vertices))+"\n")
                        try:
                            if geo.data.shape_keys.key_blocks[0] and geo.data.shape_keys.key_blocks[1]:
                                for vertindex in vertices:
                                    sk0 = geo.data.shape_keys.key_blocks[0]
                                    sk0co = geomatrix*sk0.data[vertindex].co
                                    sk1 = geo.data.shape_keys.key_blocks[1]
                                    sk1co = geomatrix*sk1.data[vertindex].co
                                    rad_poly.write(" " +str(sk0co[0]+(sk1co[0]-sk0co[0])*sk1.value) +  " " + str(sk0co[1]+(sk1co[1]-sk0co[1])*sk1.value) +" "+ str(sk0co[2]+(sk1co[2]-sk0co[2])*sk1.value) + "\n")
                        except:
                            for vertindex in vertices:
                                rad_poly.write(" " +str((geomatrix*geo.data.vertices[vertindex].co)[0]) +  " " + str((geomatrix*geo.data.vertices[vertindex].co)[1]) +" "+ str((geomatrix*geo.data.vertices[vertindex].co)[2]) + "\n")
                        rad_poly.write("\n")
                    except:
                        export_op.report({'ERROR'},"Make sure your object "+geo.name+" has an associated material")
            rad_poly.close()

    def obmexport(self, frame, obs, ob, export_op):
        self.scene.frame_current = frame
        if ob == 0:
            if frame == 0:
                bpy.ops.export_scene.obj(filepath=self.obj(frame), check_existing=True, filter_glob="*.obj;*.mtl", use_selection=False, use_animation=False, use_apply_modifiers=True, use_edges=False, use_normals=True, use_uvs=True, use_materials=True, use_triangles=True, use_nurbs=True, use_vertex_groups=False, use_blen_objects=True, group_by_object=False, group_by_material=False, keep_vertex_order=True, global_scale=1.0, axis_forward='Y', axis_up='Z', path_mode='AUTO')
            objcmd = "obj2mesh -w -a "+self.mat(frame)+" "+self.obj(0)+" "+self.mesh(frame)
            objrun = Popen(objcmd, shell = True, stderr = PIPE)
            for line in objrun.stderr:
                if 'fatal' in str(line):
                    self.merr = 1
         
            if self.merr == 0 and ob == 0:
                rad_poly = open(self.poly(frame), 'w')
                rad_poly.write("void mesh id \n1 "+self.mesh(frame)+"\n0\n0\n")
            
            if self.merr == 1:        
                if frame == 0:
                    rad_poly = open(self.poly(frame), 'w')
                    for geo in obs:
                        geomatrix = geo.matrix_world
                        for face in geo.data.faces:
                            try:
                                vertices = face.vertices[:]
                                rad_poly.write("# Polygon \n")
                                rad_poly.write(geo.data.materials[face.material_index].name.replace(" ", "_") + " polygon " + "poly_"+geo.data.name.replace(" ", "_")+"_"+str(face.index) + "\n")
                                rad_poly.write("0\n0\n"+str(3*len(face.vertices))+"\n")
                                try:
                                    if geo.data.shape_keys.key_blocks[0] and geo.data.shape_keys.key_blocks[1]:
                                        for vertindex in vertices:
                                            sk0 = geo.data.shape_keys.key_blocks[0]
                                            sk0co = geomatrix*sk0.data[vertindex].co
                                            sk1 = geo.data.shape_keys.key_blocks[1]
                                            sk1co = geomatrix*sk1.data[vertindex].co
                                            rad_poly.write(" " +str(sk0co[0]+(sk1co[0]-sk0co[0])*sk1.value) +  " " + str(sk0co[1]+(sk1co[1]-sk0co[1])*sk1.value) +" "+ str(sk0co[2]+(sk1co[2]-sk0co[2])*sk1.value) + "\n")
                                except:
                                    for vertindex in vertices:
                                        rad_poly.write(" " +str((geomatrix*geo.data.vertices[vertindex].co)[0]) +  " " + str((geomatrix*geo.data.vertices[vertindex].co)[1]) +" "+ str((geomatrix*geo.data.vertices[vertindex].co)[2]) + "\n")
                                rad_poly.write("\n")
                            except:
                                export_op.report({'ERROR'},"Make sure your object "+geo.name+" has an associated material")
                                
                    rad_poly.close()
        
    def radlights(self, frame):
        os.chdir(self.newdir)
        self.scene.frame_set(frame)
        rad_lights = open(self.lights(frame), "w")
        for geo in bpy.context.scene.objects:
            if geo.ies_name != "":
                iesname = os.path.splitext(os.path.basename(geo.ies_name))[0]
                if geo.type == 'LAMP':
                    subprocess.call("ies2rad -t default -m "+str(geo.ies_strength)+" -l "+self.newdir+" -d"+geo.ies_unit+" -o "+iesname+"-"+str(frame)+" "+geo.ies_name+" > "+self.filebase+"-"+str(frame)+".lights", shell=True)
                    rad_lights.write("!xform -rx "+str((180/pi)*geo.rotation_euler[0])+" -ry "+str((180/pi)*geo.rotation_euler[1])+" -rz "+str((180/pi)*geo.rotation_euler[2])+" -t "+str(geo.location[0])+" "+str(geo.location[1])+" "+str(geo.location[2])+" "+self.newdir+"/"+iesname+"-"+str(frame)+".rad\n\n")    
                if 'lightarray' in geo.name:
                    spotmatrix = geo.matrix_world
                    subprocess.call("ies2rad -t default -m "+str(geo.ies_strength)+" -l "+self.newdir+" -o "+iesname+"-"+str(frame)+" -d"+geo.ies_unit+" "+geo.ies_name+" > "+self.filebase+"-"+str(frame)+".lights", shell=True)
                    rotation = geo.rotation_euler                    
#                    for face in [face for face in geo.data.faces if 'lightarray' in geo.material_slots[face.material_index].name]:
                    for face in geo.data.faces:
                         rad_lights.write("!xform -rx "+str((180/pi)*rotation[0])+" -ry "+str((180/pi)*rotation[1])+" -rz "+str((180/pi)*rotation[2])+" -t "+str((spotmatrix*face.center)[0])+" "+str((spotmatrix*face.center)[1])+" "+str((spotmatrix*face.center)[2])+" "+self.newdir+"/"+iesname+"-"+str(frame)+".rad\n\n")    
        rad_lights.close()
        
    def rtexport(self, export_op):
    # Function for the exporting of Blender geometry and materials to Radiance files
        rtrace = open(self.rtrace, "w")       
        calcsurfverts = []
        calcsurffaces = []

        if 0 not in [len(mesh.materials) for mesh in bpy.data.meshes]:
            for o, geo in enumerate(self.scene.objects):
                csf = []
                cverts = []
                cvox = []
                cvoy = []
                cvoz = []
                
                self.scene.objects.active = geo
                if geo.type == 'MESH' and 'lightarray' not in geo.name and geo.hide == False and geo.layers[0] == True:
                    bpy.ops.object.mode_set(mode = 'EDIT')
                    bpy.ops.mesh.select_all(action='SELECT')
#                    bpy.ops.mesh.normals_make_consistent(inside=False)
                    bpy.ops.object.mode_set(mode = 'OBJECT')
                    meshorig = geo.data
                    mesh = meshorig.copy()
                    mesh.transform(geo.matrix_world)

                    if len([mat.name for mat in geo.material_slots if 'calcsurf' in mat.name]) != 0:
                        for face in mesh.faces:
                            if "calcsurf" in str(mesh.materials[face.material_index].name):
                                bpy.context.scene.objects.active = geo
                                geo.select = True
                                bpy.ops.object.mode_set(mode = 'OBJECT')                        
                                for vc in geo.data.vertex_colors:
                                    bpy.ops.mesh.vertex_color_remove()
                                fnormx, fnormy, fnormz = (face.normal * geo.matrix_world)[0], (face.normal * geo.matrix_world)[1], (face.normal * geo.matrix_world)[2]
                                if self.scene.livi_export_calc_points == "0":                            
                                    rtrace.write(str(face.center[0])+" "+str(face.center[1])+" "+str(face.center[2])+" "+str(face.normal[0])+" "+str(face.normal[1])+" "+str(face.normal[2])+"\n")
                                calcsurffaces.append((o, face))
                                csf.append(face.index)
                                geo['calc'] = 1
                                
                                for vert in face.vertices:
                                    if (mesh.vertices[vert]) not in calcsurfverts:
                                        vcentx = mesh.vertices[vert].co[0]
                                        vcenty = mesh.vertices[vert].co[1]
                                        vcentz = mesh.vertices[vert].co[2]
                                        vnormx = mesh.vertices[vert].normal[0]
                                        vnormy = mesh.vertices[vert].normal[1]
                                        vnormz = mesh.vertices[vert].normal[2]
                                        if self.scene.livi_export_calc_points == "1":
                                            rtrace.write(str(vcentx)+" "+str(vcenty)+" "+str(vcentz)+" "+str(vnormx)+" "+str(vnormy)+" "+str(vnormz)+"\n")
                                            
                                        calcsurfverts.append(mesh.vertices[vert])
                                        cvox.append(mesh.vertices[vert].co[0] - geo.location[0]) 
                                        cvoy.append(mesh.vertices[vert].co[1] - geo.location[1]) 
                                        cvoz.append(mesh.vertices[vert].co[2] - geo.location[2])
                                        cverts.append(vert)
                                        
                                geo['cverts'] = cverts
                                geo['cvox'] = cvox
                                geo['cvoy'] = cvoy
                                geo['cvoz'] = cvoz
                        if geo['calc'] == 1:              
                            geo['cfaces'] = csf
                        
                        if self.scene.livi_export_calc_points == "1":
                            self.reslen = len(calcsurfverts)
                        else:
                            self.reslen = len(calcsurffaces)
                    else:
                        geo['calc'] = 0
                        for mat in geo.material_slots:
                            mat.material.use_transparent_shadows = True
                
                self.export = 1
            rtrace.close()    
            
        else:
            self.export = 0
            for geo in self.scene.objects:
                if geo.type == 'MESH' and geo.name != 'lightarray':
                    if not geo.data.materials:
                        export_op.report({'ERROR'},"Make sure your object "+geo.name+" has an associated material") 
    
    def fexport(self, frame, export_op):
        try:
            subprocess.call("oconv -w "+self.lights(frame)+" "+self.sky(frame)+" "+self.mat(frame)+" "+self.poly(frame)+" > "+self.filebase+"-"+str(frame)+".oct", shell=True)
        except Exception as e:
            print(e)
            export_op.report({'ERROR'},"There is a problem with geometry export. If created in another package simplify te geometry, and turn off smooth shading")
        self.scene.livi_display_panel = 0        
        export_op.report({'INFO'},"Export is finished")
        self.scene.frame_set(0)                      
#Compute solar position (altitude and azimuth in degrees) based on day of year (doy; integer), local solar time (lst; decimal hours), latitude (lat; decimal degrees), and longitude (lon; decimal degrees).
def solarPosition(doy, lst, lat, lon):
    #Set the local standard time meridian (lsm) (integer degrees of arc)
    lsm = int(lon/15)*15
    #Approximation for equation of time (et) (minutes) comes from the Wikipedia article on Equation of Time
    b = 2*math.pi*(doy-81)/364
    et = 9.87 * math.sin(2*b) - 7.53 * math.cos(b) - 1.5 * math.sin(b)
    #The following formulas adapted from the 2005 ASHRAE Fundamentals, pp. 31.13-31.16
    #Conversion multipliers
    degToRad = 2*math.pi/360
    radToDeg = 1/degToRad
    #Apparent solar time (ast)
    ast = lst + et/60 + (lsm-lon)/15
    #Solar declination (delta) (radians)
    delta = degToRad*23.45 * math.sin(2*math.pi*(284+doy)/365)
    #Hour angle (h) (radians)
    h = degToRad*15 * (ast-12)
     #Local latitude (l) (radians)
    l = degToRad*lat
    #Solar altitude (beta) (radians)
    beta = asin(cos(l) * cos(delta) * cos(h) + sin(l) * sin(delta))
    #Solar azimuth phi (radians)
    phi = acos((sin(beta) * sin(l) - sin(delta))/(cos(beta) * cos(l)))                                                                         
    #Convert altitude and azimuth from radians to degrees, since the Spatial Analyst's Hillshade function inputs solar angles in degrees
    altitude = radToDeg*beta
    if ast<=12:
        azimuth = radToDeg*phi
    else:
        azimuth = 360 - radToDeg*phi
    return([altitude, azimuth])         
    
def negneg(x):
    if float(x) < 0:
        x = 0
    return float(x)
    
