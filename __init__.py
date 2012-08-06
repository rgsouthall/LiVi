# LiVi Radiance export and visualisation scripts created by Ryan Southall (rgsouthall)

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

#  THIS SOFTWARE IS PROVIDED ``AS IS'' AND ANY EXPRESSED OR IMPLIED
#  WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES
#  OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
#  DISCLAIMED.   IN NO EVENT SHALL University of Brighton  OR
#  ITS CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
#  SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
#  LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF
#  USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
#  ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
#  OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT
#  OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
#  SUCH DAMAGE.
#  ====================================================================
# 
#  This product includes Radiance software
#                  (http://radsite.lbl.gov/)
#                  developed by the Lawrence Berkeley National Laboratory
#                (http://www.lbl.gov/).
# 
#  The Radiance Software License, Version 1.0
# 
#  Copyright (c) 1990 - 2009 The Regents of the University of California,
#  through Lawrence Berkeley National Laboratory.   All rights reserved.
# 
#  Redistribution and use in source and binary forms, with or without
#  modification, are permitted provided that the following conditions
#  are met:
# 
#  1. Redistributions of source code must retain the above copyright
#          notice, this list of conditions and the following disclaimer.
# 
#  2. Redistributions in binary form must reproduce the above copyright
#        notice, this list of conditions and the following disclaimer in
#        the documentation and/or other materials provided with the
#        distribution.
# 
#  3. The end-user documentation included with the redistribution,
#            if any, must include the following acknowledgment:
#              "This product includes Radiance software
#                  (http://radsite.lbl.gov/)
#                  developed by the Lawrence Berkeley National Laboratory
#                (http://www.lbl.gov/)."
#        Alternately, this acknowledgment may appear in the software itself,
#        if and wherever such third-party acknowledgments normally appear.
# 
#  4. The names "Radiance," "Lawrence Berkeley National Laboratory"
#        and "The Regents of the University of California" must
#        not be used to endorse or promote products derived from this
#        software without prior written permission. For written
#        permission, please contact radiance@radsite.lbl.gov.
# 
#  5. Products derived from this software may not be called "Radiance",
#        nor may "Radiance" appear in their name, without prior written
#        permission of Lawrence Berkeley National Laboratory.
# 
#  THIS SOFTWARE IS PROVIDED ``AS IS'' AND ANY EXPRESSED OR IMPLIED
#  WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES
#  OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
#  DISCLAIMED.   IN NO EVENT SHALL Lawrence Berkeley National Laboratory OR
#  ITS CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
#  SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
#  LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF
#  USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
#  ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
#  OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT
#  OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
#  SUCH DAMAGE.
 

bl_info = {
    "name": "Lighting Visualiser (LiVi)",
    "author": "Ryan Southall",
    "version": (0, 2),
    "blender": (2, 6, 2),
    "api": 34950,
    "location": "3D View > Properties Panel",
    "description": "Radiance exporter and results visualiser",
    "warning": "This is a beta script. Some functionality is still broken",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Import-Export"}

# Revision History:
# 0.2 - Inclusion of IES artificial lights, animation of lights and materials, glare analysis and DDS.
# 0.1.1 - better geometry export and camera alignment (rgsouthall - 10/04/2012)
# 0.1 - animation of time and geometry now functional (rgsouthall - 20/03/2012
# 0.0.4 - fix sunposition and month selection bugs (rgsouthall - 20/06/11)
# 0.0.3 - initial release (rgsouthall - 01/06/11)

if "bpy" in locals():
    import imp
    imp.reload(ui)
else:
    from io_livi import ui

import bpy, os, sys, subprocess
from bpy.props import BoolProperty, IntProperty, FloatProperty, EnumProperty, StringProperty
from . import ui

if str(sys.platform) == 'darwin':
    os.environ["PATH"] = os.environ["PATH"] + ":/Applications/blender-26/LiVi/Radiance/bin" 
    os.environ["RAYPATH"] = "/Applications/blender-26/LiVi/Radiance/lib"
elif str(sys.platform) == 'win32':
    os.environ["PATH"] = os.environ["PATH"] + ";"+os.path.abspath(os.curdir)+"\\radiance\\bin" 
    os.environ["RAYPATH"] = os.path.abspath(os.curdir)+"\\radiance\\lib" 

def register():
    bpy.utils.register_module(__name__)
    
    bpy.types.Object.ies_name = StringProperty(name="Path", description="IES File", maxlen=1024, default="")
    bpy.types.Object.ies_strength = FloatProperty(name="Lamp strength:", description="Strength of IES lamp", min = 0, max = 1, default = 1)
    bpy.types.Object.ies_unit = EnumProperty(
            items=[("m", "Meters", ""),
                   ("c", "Centimeters", ""),
                    ("f", "Feet", ""),
                    ("i", "Inches", ""),
                    ],
            name="IES dimension",
            description="Specify the IES file measurement unit",
            default="m")
    
    Scene = bpy.types.Scene
    
    # LiVi Export panel properties    
    Scene.epwdat_name = StringProperty(name="Path", description="EPW processed data file", maxlen=1024, default="")
            
    Scene.livi_anim = EnumProperty(
            items=[("0", "None", "export for a static scene"),
                   ("1", "Time", "export for a period of time"),
                    ("2", "Geometry", "export for Dynamic Daylight Simulation"),
                    ("3", "Material", "export for Dynamic Daylight Simulation"),
                    ("4", "Lights", "export for Dynamic Daylight Simulation"),
                   ],
            name="",
            description="Specify the animation type",
            default="0")
    if str(sys.platform) != 'win32': 
        Scene.livi_export_time_type = EnumProperty(
                items=[("0", "Moment", "export for a moment time"),
                       ("1", "DDS", "analysis over a year"),],
                name="",
                description="Specify the time type",
                default="0")      
    elif str(sys.platform) == 'win32':
        Scene.livi_export_time_type = EnumProperty(
                items=[("0", "Moment", "export for a moment time"),                 
                        ("1", "DDS", "analysis over a year"),],
                name="",
                description="Specify the time type",
                default="0") 
        
    Scene.livi_export_calc_points = EnumProperty(
            items=[("0", "Faces", "export faces for calculation points"),
                   ("1", "Vertices", "export vertices for calculation points"),
                   ],
            name="",
            description="Specify the type of geometry to act as calculation points",
            default="0")
    Scene.livi_export_geo_export = EnumProperty(
            items=[("0", "Static", "Static geometry export"),
                   ("1", "Dynamic", "Dynamic geometry export"),
                   ],
            name="",
            description="Specify the type of geometry to act as calculation points",
            default="0")
    Scene.livi_export_sky_type = EnumProperty(
            items=[("0", "Sunny", "CIE Sunny Sky description"),
                   ("1", "Partly Coudy", "CIE Sunny Sky description"),
                   ("2", "Coudy", "CIE Partly Cloudy Sky description"),
                   ("3", "DF Sky", "Daylight Factor Sky description"),
                   ("4", "HDR Sky", "HDR file sky"),],
            name="",
            description="Specify the type of sky for the simulation",
            default="0")
    Scene.livi_export_sky_type_period = EnumProperty(
            items=[("0", "Sunny", "CIE Sunny Sky description"),
                   ("1", "Partly Coudy", "CIE Sunny Sky description"),
                   ("2", "Coudy", "CIE Partly Cloudy Sky description"),],
            name="",
            description="Specify the type of sky for the simulation",
            default="0")
    Scene.livi_export_standard_meridian = EnumProperty(
            items=[("0", "YST", ""),
                   ("1", "PST", ""),
                   ("2", "MST", ""),
                   ("3", "CST", ""),
                   ("4", "EST", ""),
                   ("GMT", "GMT", ""),
                   ("6", "CET", ""),
                   ("7", "EET", ""),
                   ("8", "AST", ""),
                   ("9", "GST", ""),
                   ("10", "IST", ""),
                   ("11", "JST", ""),
                   ("12", "NZST", ""),                   ],
            name="Meridian",
            description="Specify the local meridian",
            default="GMT")
    Scene.livi_export_summer_meridian = EnumProperty(
            items=[("0", "YDT", ""),
                   ("1", "PDT", ""),
                   ("2", "MDT", ""),
                   ("3", "CDT", ""),
                   ("4", "EDT", ""),
                   ("BST", "BST", ""),
                   ("6", "CEST", ""),
                   ("7", "EEST", ""),
                   ("8", "ADT", ""),
                   ("9", "GDT", ""),
                   ("10", "IDT", ""),
                   ("11", "JDT", ""),
                   ("12", "NZDT", ""),                   ],
            name="Meridian",
            description="Specify the local Summertime meridian",
            default="BST")
    Scene.livi_export_latitude = FloatProperty(
            name="Latitude", description="Site Latitude",
            min=-90, max=90, default=52)
    Scene.livi_export_longitude = FloatProperty(
            name="Longitude", description="Site Longitude",
            min=-15, max=15, default=0)        
    Scene.livi_export_start_month = IntProperty(
            name="Month", description="Month of the year",
            min=1, max=12, default=1)
    Scene.livi_export_start_day = IntProperty(
            name="Day", description="Day of the year",
            min=1, max=31, default=1)
    Scene.livi_export_start_day30 = IntProperty(
            name="Day", description="Day of the year",
            min=1, max=30, default=1)
    Scene.livi_export_start_day28 = IntProperty(
            name="Day", description="Day of the year",
            min=1, max=28, default=1)
    Scene.livi_export_start_hour = IntProperty(
            name="Hour", description="Hour of the day",
            min=1, max=24, default=12)
    Scene.livi_export_end_month = IntProperty(
            name="Month", description="Month of the year",
            min=1, max=12, default=1)
    Scene.livi_export_end_day = IntProperty(
            name="Day", description="Day of the year",
            min=1, max=31, default=1)
    Scene.livi_export_end_day30 = IntProperty(
            name="Day", description="Day of the year",
            min=1, max=30, default=1)
    Scene.livi_export_end_day28 = IntProperty(
            name="Day", description="Day of the year",
            min=1, max=28, default=1)
    Scene.livi_export_end_hour = IntProperty(
            name="Hour", description="Hour of the day",
            min=1, max=24, default=12)
    Scene.livi_export_interval = FloatProperty(
            name="", description="Interval time",
            min=0.25, max=730, default=1)
    Scene.livi_export_summer_enable = BoolProperty(
            name="Daylight saving", description="Enable daylight saving clock",
            default=True)
    Scene.livi_export_epw_name = StringProperty(
            name="", description="Name of the EnergyPlus weather file", default="")
    Scene.livi_export_hdr_name = StringProperty(
            name="", description="Name of the HDR angmap file", default="")
            
# LiVi Calculation panel ui elements

    Scene.livi_metric = EnumProperty(
            items=[("0", "Illuminance", "Lux calculation"),
                   ("1", "Irradiance", "W/m**2 calculation"),
			  ("3", "Glare", "Glare calculation"),
                   ],
            name="",
            description="specify the lighting metric required",
            default="0")
    Scene.livi_metricdf = EnumProperty(
            items=[("0", "Illuminance", "Lux calculation"),
                   ("1", "Irradiance", "W/m**2 calculation"),
                   ("2", "DF", "Daylight Factor calculation"),
                   ("3", "Glare", "Glare calculation"),
                   ],
            name="",
            description="specify the lighting metric required",
            default="0")
    Scene.livi_metricdds = EnumProperty(
            items=[("0", "Cumulative light exposure", "Cumulative luxhours"),
                   ("1", "Cumulative radiation calculation", "kWh/m**2"),
                   ("4", "Daylight availability", "Daylight availability"),
			  ],
            name="",
            description="specify the lighting metric required",
            default="0")	
    Scene.livi_calc_acc = EnumProperty(
            items=[("0", "Low", "Quick but innacurate simulation"),
                   ("1", "Medium", "Medium accuracy and speed"),
                   ("2", "High", "Slow but accurate simulation"),
                   ("3", "Custom", "Specify command line arguments for Radiance below")
                   ],
            name="",
            description="Specify the speed and accuracy of the simulation",
            default="0")
    Scene.livi_calc_dastart_hour = IntProperty(
            name="Hour", description="Starting hour for occupancy",
            min=1, max=24, default=8)  
    Scene.livi_calc_daend_hour = IntProperty(
            name="Hour", description="Ending hour for occupancy",
            min=1, max=24, default=19)
    Scene.livi_calc_min_lux = IntProperty(
            name="Lux", description="Minimum Lux level required",
            min=1, max=2000, default=200)
    Scene.livi_calc_da_weekdays = BoolProperty(
            name="Weekdays only", description="Calculate Daylight availability for weekdays only",
            default=True)
    Scene.livi_calc_custom_acc = StringProperty(
            name="", description="Custom Radiance simulation parameters", default="")   
    Scene.livi_calc_vec_name = StringProperty(
            name="", description="Name of the generated vector file", default="")
            
    # LiVi Display panel properties
    Scene.display_legend = IntProperty(
            name="Legend Display", description="Shows a colour coded legend for the results in the 3D view",
            default=0)
    Scene.livi_display_panel = IntProperty(
            name="Display Panel", description="Shows the Disply Panel",
            default=0)
    Scene.livi_disp_3d = BoolProperty(
            name="3D Display", description="Enable 3D results analysis",
            default=0)
    Scene.livi_render_view = BoolProperty(
            name="OpenGL Display", description="Enable OpenGL 3D results view",
            default=True)            
    Scene.livi_disp_3dlevel = FloatProperty(
            name="3D level", description="Level of 3D effect",
            min=0.1, max=5000, default=0)

def unregister():
    import bpy
    bpy.utils.unregister_module(__name__)

if __name__ == "__main__":
    register()
