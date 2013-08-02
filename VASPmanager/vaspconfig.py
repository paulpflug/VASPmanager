import other as o
import math
import fileoperations as files
import random
import os
import shutil
class vaspconfig(object):
    """test"""
    path=""
    __contcar="CONTCAR"
    __oszicar="OSZICAR"
    __kpoints="KPOINTS"
    __poscar="POSCAR"
    __poscar2="POSCAR2"
    __incar="INCAR"
    highestFileVersion= True
    def __init__(self, path):
        self.path=path
    def incar(self,para=dict(),save=True):
        file = self.path+self.__incar
        readData = files.readfile(file) 
        paraold = dict()
        for i in range(len(readData)):
            s = readData[i].split("=")
            if len(s)==2:
                val = s[1].split("#")
                paraold[s[0]]=val[0].rstrip()
        for k,v in para.iteritems():
            paraold[k]=v
        if save:
            files.writeDictionaryToFile(file,paraold)
        return paraold
    def kpoints(self,para=dict(),save=True):
        file = self.path+self.__kpoints
        if self.highestFileVersion:
            newfile = [file]
            if not files.getHighestVersion(newfile):
                return dict()
            file=newfile[0]
        result = dict()
        readData = files.readfile(file)
        if para.has_key(par.Kpoints):
            readData[1] = para[par.Kpoints]
        else:
            s=readData[1].split()[0]
            result[par.Kpoints] = str(s)+'\n'
        ktype =""
        if para.has_key(par.Ktype):
            readData[2] = para[par.Ktype]
            ktype=para[par.Ktype]
        else:
            result[par.Ktype] = readData[2]
            ktype=readData[2]
        if ktype[0].lower()=="l":
            if para.has_key(par.Klinetype):
                readData[3] = para[par.Klinetype]
            else:
                result[par.Klinetype] = readData[3]
            if para.has_key(par.Kline):              
                for i in range(4,len(readData)):               
                    readData[i]=""
                data =[]
                i = 0
                for ks in para[par.Kline]:
                    d=[]
                    for k in ks:
                        d.append(str(k))
                    data.append(" ".join(d))
                    if i%2 == 1:
                        data.append("")
                    i+=1
                readData[4]='\n'.join(data)
            else:
                klinedata =[]                
                for i in range(4,len(readData)):                
                    if readData[i]!="\n":
                        klinedata.append(readData[i].split())
                result[par.Kline]=klinedata
        else:
            if para.has_key(par.Kmesh):
                if len(para[par.Kmesh])==1:
                    val = para[par.Kmesh][0]
                    para[par.Kmesh] = [val,val,val]
                readData[3] =files.vecToLine(para[par.Kmesh],Int=True)
            else:
                if len(readData)>3:
                    s = str(readData[3])
                    result[par.Kmesh]=s.split()        
        if save:
            files.writefile(file,readData)
        return result
    def hasvalidcontcar(self):
        para=self.poscar(file=self.__contcar,save=False)
        for p in par.translation[par.Poscar]:
            if not para.has_key(p):
                return False
        return True
    def contcar(self,para=dict(),save=True):
        return self.poscar(file=self.__contcar,para=para,save=save)
    def poscar(self,file=__poscar, para = dict(),save=True):
        """
        file: Filename of poscar
        para: dictionary of parameters
        """
        file=self.path+file
        if self.highestFileVersion:
            newfile = [file]
            if not files.getHighestVersion(newfile):
                return dict()
            file=newfile[0]
        result = dict()
        readData = files.readfile(file) 
        if para.has_key(par.LatticeConstant):
            readData[1] = files.toLine(para[par.LatticeConstant])
        else:
            if len(readData)>1:
                s = str(readData[1])           
                result[par.LatticeConstant] = s.strip(' \n')
        if para.has_key(par.Basisvectors):
            readData[2] = files.matrixToLine(para[par.Basisvectors])
            readData[3] =""
            readData[4]=""
        else:
            if len(readData)>4:
                bv = list()
                for i in range(2,5):
                    bv.append(filter(None,str(readData[i]).strip(' \n').split(" ")))                    
                result[par.Basisvectors] =bv
        atomcount=0           
        if para.has_key(par.Atoms): 
            readData[5]=""
            readData[6]=""
            for atom in para[par.Atoms]:
                readData[5]+=" "+atom[0]
                readData[6]+=" "+str(int(float(atom[1])))
                atomcount+=int(float(atom[1]))
            readData[5]+='\n'
            readData[6]+='\n'
        else:
            if len(readData)>6:
                s1 = readData[5].strip(' \n').split()
                s2 = readData[6].strip(' \n').split()
                if (len(s1) == len(s2)):
                    atoms = []
                    for i in range(len(s1)):
                        atoms.append([s1[i],s2[i]])
                        atomcount+=int(float(s2[i]))
                    result[par.Atoms]=atoms
        atomcount = int(atomcount)
        atomlines = range(9,9+atomcount)
        text=list()
        for i in atomlines:
            text.append("")
        ### atomcount has to equal #Atompos & #Atommove
        atomtext=list()
        if not (para.has_key(par.Atompos) and para.has_key(par.Atommove)):
            for i in atomlines:
                atomtext.append(filter(None,str(readData[i]).strip(' \n').split(" ")))           
        if para.has_key(par.Atompos):
           if len(para[par.Atompos])==atomcount:
                for i in range(0,atomcount):
                    text[i]=files.vecToLine(para[par.Atompos][i])[:-1]
        else:
           ap= list()                   
           for i in range(0,atomcount):
                ap.append(atomtext[i][0:3])
                text[i]=" ".join(atomtext[i][0:3])
           result[par.Atompos] = ap
        if para.has_key(par.Atommove):
           if len(para[par.Atommove])==atomcount:
                for i in range(0,atomcount):
                    text[i]+=" "+files.vecToLine(para[par.Atommove][i])[:-1]
           elif len(para[par.Atommove])==1:
                for i in range(0,atomcount):
                    text[i]+=" "+files.vecToLine(para[par.Atommove][0])[:-1]
        else:
           am=list()
           for i in range(0,atomcount):
                am.append(atomtext[i][3:6])
                text[i]+=" "+" ".join(atomtext[i][3:6])
           result[par.Atommove] = am
        if len(atomlines) == 0:
            atomlines.append(9)
        for i in range(atomlines[0],len(readData)):
            readData[i]="" 
        while len(readData)<=atomlines[0]:
            readData.append("")            
        readData[atomlines[0]]='\n'.join(text)
        if save:
            files.writefile(file,readData)
        return result
    def oszicar(self,save=True):
        file=self.path+self.__oszicar
        if self.highestFileVersion:
            newfile = [file]
            if not files.getHighestVersion(newfile):
                return dict()
            file=newfile[0]
        result = dict()
        f = open(file,"r")
        s =str.split(files.tail(f,1).strip()," ")
        if len(s)>4:
            s = s[4]
            if s != "" :
                try:
                    result[par.Energy]=float(s)
                except: pass
        f.close()
        return result
    def getparameter(self,parameter):
        for filename,paras in par.translation.iteritems():
            if parameter in paras:
                if filename == par.Poscar:
                    return self.poscar(save=False)[parameter]
                if filename == par.Kpoints:
                    return self.kpoints(save=False)[parameter]
                if parameter == par.Supercell or parameter == par.Dualizesuper1 or parameter == par.Dualizesuper2:
                    return [1,1,1]
                if parameter == par.Vacuum or parameter == par.Dualizetranslation:
                    return [0,0,0]
                if parameter == par.Noise:
                    return [[0,0],[0,0],[0,0]]
                if parameter == par.Noiseatoms:
                    return None
    def setparameter(self,parameters=dict()):
        print("#### Setting parameters ####")
        para = dict()
        for paras in par.translation[par.Poscar]:
            if parameters.has_key(paras):
                para[paras]=parameters[paras]
        if len(para)>0:
            self.poscar(para=para)
        para=dict()
        for paras in par.translation[par.Incar]:
            if parameters.has_key(paras):
                para[paras]=parameters[paras]
        if len(para)>0:
            self.incar(para=para)
        para=dict()
        for paras in par.translation[par.Kpoints]:
            if parameters.has_key(paras):
                para[paras]=parameters[paras]
        if len(para)>0:
            self.kpoints(para=para)
        
        
        if parameters.has_key(par.Dualizesuper1) or parameters.has_key(par.Dualizesuper2) or parameters.has_key(par.Dualizetranslation):
            super1 = [1,1,1]
            if parameters.has_key(par.Dualizesuper1):
                super1 =parameters[par.Dualizesuper1]
            super2 = [1,1,1]
            if parameters.has_key(par.Dualizesuper2):
                super2 =parameters[par.Dualizesuper2]
            translate = [0,0,0]
            if parameters.has_key(par.Dualizetranslation):
                translate =parameters[par.Dualizetranslation]
            rotate = 0
            if parameters.has_key(par.Dualizerotation):
                rotate =parameters[par.Dualizerotation]
            moves1=[]
            if parameters.has_key(par.Dualizemove1):
                moves1 =parameters[par.Dualizemove1]
            moves2=[]
            if parameters.has_key(par.Dualizemove2):
                moves2 =parameters[par.Dualizemove2]
            flipbottom=False
            if parameters.has_key(par.Dualizeflipbottom):
                flipbottom=parameters[par.Dualizeflipbottom]
            self.dualize(translate,super1,super2,rotate,moves1,moves2,flipbottom=flipbottom,save=True)
        if parameters.has_key(par.Supercell):
            moveatoms=[]
            if parameters.has_key(par.Supermoveatoms):
                moveatoms = parameters[par.Supermoveatoms]
            atommoves = []
            if parameters.has_key(par.Superatommoves):
                atommoves = parameters[par.Superatommoves]
            self.makesupercell(parameters[par.Supercell],save=True,atommoves=atommoves,moveatoms=moveatoms)
        if parameters.has_key(par.Vacuum):
            self.addvacuum(parameters[par.Vacuum],save=True)
        if parameters.has_key(par.Noise):
            Atoms = None
            if parameters.has_key(par.Noiseatoms):
                Atoms=parameters[par.Noiseatoms]
            self.noiseonposition(parameters[par.Noise],atoms=Atoms,save=True)
        if parameters.has_key(par.Potpath) and parameters.has_key(par.Pottype):
            ### selecting right potcar            
            para = self.poscar()
            potcar = open(self.path+"POTCAR",'wb')
            potpath = parameters[par.Potpath]
            if (not os.path.isdir(potpath)):
                raise IOError('POTCAR path not found: '+potpath)
            availpotcars = os.listdir(potpath)
            splitpotcars = [str.split(s,"_") for s in availpotcars]
            found =0
            for atom,acount in para[par.Atoms]:
                for i,a in enumerate(splitpotcars):
                    if (a[1]==atom and a[2]==parameters[par.Pottype]):
                        found+=1
                        print "found POTCAR: "+potpath+availpotcars[i]
                        shutil.copyfileobj(open(potpath+availpotcars[i],'rb'), potcar)
                        break
            potcar.close()          
            if (not found == len(para[par.Atoms])):
                raise IOError("No POTCAR found")
    def noiseonposition(self,d,atoms=None,para=None,save=False):
        if len(d) ==1:
            d.append(d[0])
            d.append(d[0])
        newpara= dict()
        if not para:
            para = self.poscar()
        atpos = para[par.Atompos]  
        if not atoms:
            atoms = range(0,len(atpos))
        for i in atoms:
            for j in range(0,3):                
                val =float(atpos[i][j])
                valrandom = random.gauss(d[j][0],d[j][1])
                if(random.randint(0,1)):
                    val =val+valrandom
                else:
                    val =val-valrandom
                atpos[i][j]=str(val)
        newpara[par.Atompos]=atpos
        newpara[par.Atommove]=para[par.Atommove]
        if save:
            print("saving noised Poscar")
            self.poscar(para=newpara,save=save)
        return newpara
    def addvacuum(self,d,para=None,save=False):
        vac=[0,0,0]
        if len(d) ==1:
            d.append(d[0])
            d.append(d[0])
        newpara= dict()
        if not para:
            para = self.poscar()
        bv = para[par.Basisvectors]  
        a = float(para[par.LatticeConstant])
        factor = [1,1,1]
        for i in range(0,3):
            factor[i]=o.length(bv[i])
            vac[i]=d[i]/a/factor[i]
            for j in range(0,3):
                bv[i][j]=str(float(bv[i][j])+vac[i]*float(bv[i][j]))
            factor[i]=factor[i]/o.length(bv[i])
        newpara[par.Basisvectors]=bv          
        atompos = para[par.Atompos]
        means =[0,0,0]
        for atom in atompos:
            for i in range(0,3):
                means[i]+=float(atom[i])
        for i in range(0,3):
            means[i] = means[i]/len(atompos)*factor[i]        
        for atom in atompos:
            for i in range(0,3):
                    atom[i]=str(float(atom[i])*factor[i]+0.5-means[i])
        
        newpara[par.Atompos]=atompos
        newpara[par.Atoms] = para[par.Atoms]
        newpara[par.Atommove] = para[par.Atommove]
        newpara[par.LatticeConstant] = para[par.LatticeConstant]
        if save:
            print("saving vacuumedposcar")
            self.poscar(para=newpara,save=save)
        return newpara 
    def dualize(self,translation,super1,super2,rotation=0,atommoves1=[],atommoves2=[],flipbottom=False,save=True):
        para1 = self.poscar()
        para2 = self.poscar(file=self.__poscar2)
        newpara1 = self.makesupercell(super1,para=para1,atommoves=atommoves1)
        newpara2 = self.makesupercell(super2,para=para2,atommoves=atommoves2)
        zdist = float(newpara2[par.Basisvectors][2][2])*float(newpara2[par.LatticeConstant])*(1+translation[2])
        newpara1 = self.addvacuum(d=[0,0,zdist*2], para=newpara1)
        newz = float( newpara1[par.Basisvectors][2][2])*float(newpara1[par.LatticeConstant])
        atompos1 = newpara1[par.Atompos]
        atompos2 = newpara2[par.Atompos]
        firstoldz = float(atompos1[0][2])
        lastoldz = float(atompos1[len(atompos1)-1][2])
        newatompos =[]
        for ap in atompos2:
            newap = [0,0,0]
            x=float(ap[0])
            y=float(ap[1])
            newap[0] = str((math.cos(rotation/180*math.pi)*x-math.sin(rotation/180*math.pi)*y+translation[0])%1)
            newap[1] = str((math.sin(rotation/180*math.pi)*x+math.cos(rotation/180*math.pi)*y+translation[1])%1)
            newap[2] = str(firstoldz-(float(ap[2])+translation[2])*float(newpara2[par.Basisvectors][2][2])*float(newpara2[par.LatticeConstant])/newz)
            newatompos.append(newap)
        for ap in atompos1:
            newatompos.append(ap)
        for ap in atompos2:
            newap = [0,0,0]
            x=float(ap[0])
            y=float(ap[1])
            z=float(ap[2])
            if flipbottom:
                print "flipping bottom"
                x=-x
                y=-y
                z=(z-0.5)*(-1)+0.5
            newx = math.cos(rotation/180*math.pi)*x-math.sin(rotation/180*math.pi)*y+translation[0]
            newy = math.sin(rotation/180*math.pi)*x+math.cos(rotation/180*math.pi)*y+translation[1]
            if flipbottom:
                newx -=2*translation[0]
                newy -=2*translation[1]
            newap[0] = str(newx%1)
            newap[1] = str(newy%1)
            newap[2] = str(lastoldz+(float(ap[2])+translation[2])*float(newpara2[par.Basisvectors][2][2])*float(newpara2[par.LatticeConstant])/newz)
            newatompos.append(newap)
        newpara1[par.Atompos]=newatompos
        newatoms =[]
        for at in newpara2[par.Atoms]:
            newatoms.append(at)
        for at in newpara1[par.Atoms]:
            newatoms.append(at)
        for at in newpara2[par.Atoms]:
            newatoms.append(at)
        newpara1[par.Atoms]=newatoms   
        newatommove =[]
        for at in newpara2[par.Atommove]:
            newatommove.append(at)
        for at in newpara1[par.Atommove]:
            newatommove.append(at)
        for at in newpara2[par.Atommove]:
            newatommove.append(at)
        newpara1[par.Atommove]=newatommove  
        if save:
            print("saving dualised poscar")
            self.poscar(para=newpara1,save=save)
        return newpara1 
    def sortatoms(self,d=3,para=None,save=False):
        atompos = para[par.Atompos]
        atommove = para[par.Atommove]
        atoms = para[par.Atoms]
        if len(atoms)==1:
            newatomlist = list()
            for i in range(0,len(atompos)):
                newatomlist.append(atompos[i]+atommove[i])                           
            newlist = sorted(newatomlist, key=lambda k: k[d-1]) 
            atompos = list()
            atommove = list()
            for i in range(0,len(newlist)):
                atompos.append(newlist[i][0:3])
                atommove.append(newlist[i][3:6])
        para[par.Atommove]=atommove
        para[par.Atompos]=atompos
        if save:
            print("saving sorted poscar")
            self.poscar(para=para,save=save)
        else:
            print("sorted poscar")
        return para  
    def makesupercell(self,d,para=None,save=False,atommoves=[],moveatoms=[]):
        newd=[d[0]]
        if len(d) ==1:
            newd.append(d[0])
            newd.append(d[0])
        else:
            newd.append(d[1])
            newd.append(d[2])
        newpara= dict()
        if not para:
            para = self.poscar()
        atompos = para[par.Atompos]
#        layers =[[],[],[]]
#        extralayers=[[],[],[]]        
#        for i in range(0,len(atompos)):
#            for j in range(0,3):
#                layers[j].append(atompos[i][j])
#        for i in range(0,3):
#            offset =(newd[i]-math.floor(newd[i]))
#            if offset >0:
#                newoff=0
#                newoff2=1
#                for j in range(0,len(layers[i])):
#                    if float(layers[i][j])<=offset and float(layers[i][j])>newoff:
#                        newoff=float(layers[i][j])
#                for j in range(0,len(layers[i])):
#                    if float(layers[i][j])>newoff and float(layers[i][j])<newoff2:
#                        newoff2 = float(layers[i][j])
#                for j in range(0,len(layers[i])):
#                    if float(layers[i][j])<=newoff:
#                        extralayers[i].append(j)
#                if len(extralayers[i])>0:
#                    newd[i] = newd[i]-offset+newoff2
        bv = para[par.Basisvectors]        
        for i in range(0,3):
            for j in range(0,3):
                bv[i][j]=str(newd[i]*float(bv[i][j]))
        newpara[par.Basisvectors]=bv
        atomcount = len(atompos)
        atommove = para[par.Atommove]
        atoms = para[par.Atoms]
        newatoms =[]
        newatompos=[]
        newatommove=[]
        atomtranslater=[]
        for i in range(0,len(atoms)):
            newatoms.append([atoms[i][0],0])
            for j in range(0,int(atoms[i][1])):
                atomtranslater.append(i)
        for i in range(0,3):
            for a in range(0,atomcount):
                atompos[a][i]=str(float(atompos[a][i])/newd[i]) 
        dx = o.range(0,1,1./newd[0])        
        dy = o.range(0,1,1./newd[1])
        dz = o.range(0,1,1./newd[2])
        for a in range(0,atomcount):
            for i in dz:
                for j in dy:  
                    for k in dx:
                        #if ((i>0 or j>0) or k>0 ):                        
                        r=[0,0,0]
                        r[0]=str(float(atompos[a][0])+k)
                        r[1]=str(float(atompos[a][1])+j)
                        r[2]=str(float(atompos[a][2])+i)
                        if float(r[0])<1 and float(r[1])<1 and float(r[2])<1:
                            newatoms[atomtranslater[a]][1]=str(int(newatoms[atomtranslater[a]][1])+1)
                            newatompos.append(r)
                            newatommove.append(atommove[a])
        if len(moveatoms)>0:
            for moveatom in moveatoms:
                print moveatom
                for i in [0,1,2]:
                    newatompos[moveatom[0]][i]=str(float(newatompos[moveatom[0]][i])+moveatom[1][i])
        newpara[par.Atompos]=newatompos
        newpara[par.Atommove]=newatommove   
        newpara[par.Atoms]=newatoms
        newpara[par.LatticeConstant]=para[par.LatticeConstant]                 
        newpara=self.sortatoms(para=newpara)                    
        if len(atommoves)>0:  
            if len(atommoves)<len(atommove):
                for i in range(0,len(atommove)-len(atommoves)):                    
                    atommoves.append(["F"])
            for i,moves in enumerate(atommoves):
                if len(moves)==1:
                    atommoves[i] = moves*3
            newpara[par.Atommove]=atommoves
#        newatoms =[]
#        for i in range(0,len(atoms)):
#            newatoms.append([atoms[i][0],
#                             str(
#                             int(
#                             int(atoms[i][1])
#                             *math.floor(newd[0])*math.floor(newd[1])*math.floor(newd[2])
#                             ))])
#            for j in range(0,3):
#                for layernumber in extralayers[j]:
#                    if layernumber <= int(atoms[i][1]):
#                        newatoms[i][1]= str(int(newatoms[i][1])+int(math.floor(newd[j-1])*math.floor(newd[j-2])))
        
        
        if save:
            print("saving superposcar with: %.3f %.3f %.3f"%(newd[0],newd[1],newd[2]))
            self.poscar(para=newpara,save=save)
        else:
            print("made supercell with: %.3f %.3f %.3f"%(newd[0],newd[1],newd[2]))
        return newpara        
pass
class par:
    Poscar="poscar"
    Oszicar="oszicar"
    Incar="incar"
    Kpoints="kpoints"
    custom="custom"    
    
    Energy="E"
    
    Pottype="pottype"
    Potpath="potpath"
    
    Kpoints="kpoints"
    Ktype="ktype"
    Kmesh="k"
    Klinetype="kltype"
    Kline="kline"    
    
    Basisvectors="r"
    Atoms="atoms"
    Atompos="ra"
    Atommove="va"
    LatticeConstant = "a"
    
    Nparallel="NPAR"
    NBands="NBANDS" #determines the actual number of bands in the calculation
    EnergyCut="ENCUT"
    EnergyDifference="EDIFF" #specifies the global break condition for the electronic SC-loop
    Smearing="ISMEAR"
    SmearSigma="SIGMA"
    Nsw="NSW"
    Algo="ALGO"
    Precision="PREC"
    ICharge="ICHARG"
    LCharge="LCHARG"
    LWave="LWAVE"
    LReal="LREAL"
    LPlane="LPLANE"
    Lscalu="LSCALU"
    NSim="NSIM"
    KPointUse="KPUSE"
    IBand="IBAND"
    EInt="EINT"

    
    Dualizetranslation="dualize"
    Dualizerotation="dualizerot"
    Dualizesuper1="dualizes1"
    Dualizesuper2="dualizes2"
    Dualizemove1="dualizem1"
    Dualizemove2="dualizem2"
    Dualizeflipbottom="dualizeflp"
    Supercell="super"
    Superatommoves="satommove"
    Supermoveatoms="smoveatom"
    Vacuum="vac"    
    Noise="noise"
    Noiseatoms="noiseatoms"    
    
    translation ={Poscar:[LatticeConstant,Basisvectors,Atoms,Atompos,Atommove],
                  Incar:[Nparallel,NBands,EnergyCut,EnergyDifference,Smearing,SmearSigma
                  ,Nsw,ICharge,LCharge,LWave,LReal,KPointUse,IBand,EInt,Algo,Precision
                  ],
                  Kpoints:[Ktype,Kpoints,Klinetype,Kline,
                  Kmesh],
                  custom:[Supercell,Superatommoves,Supermoveatoms,Vacuum,Noise,Noiseatoms
                          ,Dualizetranslation,Dualizerotation,Dualizesuper1,Dualizesuper2,Dualizemove1,Dualizemove2
                            ,Dualizeflipbottom,Pottype,Potpath                  
                          ]
                  }   
pass
class pot:
    path="/ifto3/qu34cub/d_pseudopots/"
    potcar="POTCAR"
    dual="Dual"
    si ="Si"
    ag ="Ag"
    lda ="LDA"
    gga ="GGAPW91"
    @staticmethod
    def lda_si():
        return pot.path+"_".join([pot.potcar,pot.si,pot.lda])
    @staticmethod
    def gga_si():
        return pot.path+"_".join([pot.potcar,pot.si,pot.gga])
    @staticmethod
    def lda_ag():
        return pot.path+"_".join([pot.potcar,pot.ag,pot.lda])
    @staticmethod
    def gga_ag():
        return pot.path+"_".join([pot.potcar,pot.ag,pot.gga])
    @staticmethod
    def lda_si_ag_si():
        return pot.path+"_".join([pot.potcar,pot.dual,pot.si,pot.ag,pot.si,pot.lda])
pass
def printpara(para=dict()):
    for key,val in para.iteritems():
        s="key:"+key+" val:"
        if isinstance(val, list):
            s+= files.matrixToLine(val)
        elif isinstance(val, dict):
            for key,val in val.iteritems():
                s+= key+":"+str(val)+" "
        else:
            s+=str(val)
        print s
def getnpar(ppn):
    for i in range(int(math.sqrt(ppn)),int(ppn/2)):
        if ppn%i == 0:
            return i
    return ppn/2    