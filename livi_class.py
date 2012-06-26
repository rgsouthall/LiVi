import os
class LiVi_bc(object):
    def __init__(self, filepath, scene):
        self.filepath = filepath
        self.filename = os.path.splitext(os.path.basename(self.filepath))[0]
        self.filedir = os.path.dirname(self.filepath)
#        self.rfilename = os.path.splitext(os.path.basename(self.filepath))[0].replace(" ", "_")
#        self.rfiledir = os.path.dirname(self.filepath).replace(" ", "\ ")
        if not os.path.isdir(self.filedir+"/"+self.filename):
            os.makedirs(self.filedir+"/"+self.filename)        
        self.newdir = self.filedir+"/"+self.filename
        self.filebase = self.newdir+"/"+self.filename
#        self.nproc = multiprocessing.cpu_count()
        self.scene = scene
        self.scene['newdir'] = self.newdir
#        self.tz = tz
#        self.sd = sd
        
#        self.rnewdir = self.rfiledir+"/"+self.rfilename
#        self.rad_poly = open(self.newdir+"/"+self.filename+".poly", "w")
#        self.rad_mat = open(self.newdir+"/"+self.filename+".mat", "w")
#        self.rad_rtrace = open(self.newdir+"/"+self.filename+".rtrace", "w")
#        self.rad_lights = open(self.newdir+"/"+self.filename+".lights", "w")
#        self.rad_export = open(self.newdir+"/"+self.filename+".export", "w")
#        self.startD = startD
#        self.TZ = TZ
#        self.simacc = None
#        self.metric = None
#        self.d3d = None
#        self.d3dlevel = None
#        self.cp = CP
#        self.ga = GA
#        self.calcverts = None
#        self.cvorig = None
#        self.calcfaces = None
#        self.obreslist = None
#        self.simtime = []
#        self.fe = None
#        self.paramsp = (("-dj 1 -ps 1 -ab 2 -dr 2 -dp 0 -ss 1 -st 0 -ad 512 -av 0 0 0", "-ds 1 -dj 1 -ps 1 -st 0 -dr 2 -ab 3 -ad 1024 -as 512 -ar 512 -aa 0.1 -av 0 0 0", "-st 1 -dr 3 -ab 3 -ad 1024 -as 512 -ar 512 -aa 0.05 -av 0 0 0"))
#        self.paramss = (("-dj 1 -ab 2 -dr 2 -dp 0 -ss 1 -st 0 -ad 256 -av 0 0 0", "-ab 3 -ad 512 -as 128 -ar 128 -aa 0.1 -av 0 0 0", "-ab 4 -ad 2048 -as 1024 -ar 1024 -aa 0.01 -av 0 0 0"), ("-ab 1 -ad 256 -av 0 0 0", "-ab 2 -ad 512 -as 128 -ar 128 -aa 0.1 -av 0 0 0", "-ab 3 -ad 1024 -as 256 -ar 256 -aa 0.08 -av 0 0 0"), ("-ab 2 -ad 256 -av 0 0 0", "-ab 3 -ad 512 -as 128 -ar 128 -aa 0.1 -av 0 0 0", "-ab 4 -ad 1024 -as 256 -ar 256 -aa 0.08 -av 0 0 0"))
#        self.vecvals = None



       
            
