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
        if para.has_key(par.Kcount):
            readData[1] = para[par.Kcount]
        else:
            s=readData[1].split()[0]
            result[par.Kcount] = str(s)+'\n'
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
pass
class par:
    Poscar="POSCAR"

    Incar="INCAR"
    Kpoints="KPOINTS"
    Chgcar="CHGCAR"


    Pottype="pottype"
    Potpath="potpath"

    Kcount="kcount"
    Ktype="ktype"
    Kmesh="k"
    Klinetype="kltype"
    Kline="kline"

    Basisvectors="r"
    Atoms="atoms"
    Atompos="ra"
    Atommove="va"
    LatticeConstant = "a"

    NPAR="NPAR"
    NBANDS="NBANDS"
    ENCUT="ENCUT"
    EDIFF="EDIFF"
    ISMEAR="ISMEAR"
    SIGMA="SIGMA"
    NSW="NSW"
    ALGO="ALGO"
    PREC="PREC"
    ICHARG="ICHARG"
    LCHARG="LCHARG"
    LWAVE="LWAVE"
    LREAL="LREAL"
    LPLANE="LPLANE"
    LSCALU="LSCALU"
    NSIM="NSIM"
    KPUSE="KPUSE"
    IBAND="IBAND"
    EINT="EINT"



    translation ={Poscar:[LatticeConstant,Basisvectors,Atoms,Atompos,Atommove],
                  Incar:[NPAR,
    NBANDS,
    ENCUT,
    EDIFF,
    ISMEAR,
    SIGMA,
    NSW,
    ALGO,
    PREC,
    ICHARG,
    LCHARG,
    LWAVE,
    LREAL,
    LPLANE,
    LSCALU,
    NSIM,
    KPUSE,
    IBAND,
    EINT
                  ],
                  Kpoints:[Ktype,Kcount,Klinetype,Kline,
                  Kmesh],
                  custom:[Pottype,Potpath]
                  }
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
