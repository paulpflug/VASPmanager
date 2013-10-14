import os
import vaspconfig as vconf
import fileoperations as files
import pbs
import shutil
import time
import subprocess as sub
import math
class job(object):
    """manages a job"""
    workpath=""
    ## [1,2,3] 1=NameFROM 2=NameTO 3=Move(or copy)
    workfiles=[["POSCAR","POSCAR",False],["mist","log",True],["KPOINTS","KPOINTS",False],
               ["PARCHG","PARCHG",True],
                            ["CONTCAR","CONTCAR",False],["INCAR","INCAR",False],
                            ["OSZICAR","OSZICAR",True],["OUTCAR","OUTCAR",True],
                            ["vasprun.xml","vasprun.xml",True],
                            ["CHGCAR","CHGCAR",False],
                            ["PROCAR","PROCAR",True],
                            ["EIGENVAL","EIGENVAL",True]]
    inputfiles={vconf.par.Incar:"INCAR",
                vconf.par.Kpoints:"KPOINTS",
                vconf.par.Poscar:"POSCAR",
                vconf.par.Chgcar:"CHGCAR",
                vconf.par.Poscar2:"POSCAR2"}
    oldinputfiles=[["CONTCAR","POSCAR"],["CHGCAR","CHGCAR"]]
    potcarpath=""
    potcartype="LDA"
    useoldFiles=False
    changeoldFiles=True
    oldFilesPath=""
    copyWAVECARforth=True
    copyWAVECARback=False
    sequential=False
    oldusedparameters2=False
    parameters=[]
    parameters2=[]
    parameternames=[]
    fixparameters=dict()

    temppath=""
    tempdirstartfile="currenttemp"
    tempdirstart=1
    jobs = dict()
    jobruns = dict()
    jobidfile="/homes3/ifto/qu34cub/Hosts/jobids"
    linkfilestodir=[]
    preexec=[]
    postexec=[]
    runfile=""
    maxnpar=1000
    memorymultiplikator=1
    maxjobs = 1
    sleepduration=15*60
    runs =1
    detailedruns=dict()
    testrun=False
    verbose=False
    #### pbs ####
    name=""
    email=""
    outpath=""
    nodes=1
    ppn=8
    queue=""
    hours=1
    pbsparameters=""
    #############
    startedcalcs=0
    finishedcalcs=0
    calculations=0
    def printstatus(self,jobnr,slist=[]):
        if self.verbose:
            print "jobnr %.0d"%round(jobnr)
            print " ".join(slist)
            print " "
    def copymove(self,jobnr,src,dest,move=False):
        action = "Copy:"
        if move:
            action = "Move:"
        if os.path.exists(src) and os.path.isfile(src):
            if not os.path.getsize(src) > 0:
                self.printstatus(jobnr,["file is empty: ",src])
            else:
                self.printstatus(jobnr,[action,"from",src,"\nto",dest])
                destpath = os.path.dirname(dest)
                if not os.path.exists(destpath):
                    os.makedirs(destpath)
                if move:
                    shutil.move(src,dest)
                else:
                    shutil.copy(src,dest)
        else:
            self.printstatus(jobnr,["couldn't find file:",src])
    def deletehigher(self,jobnr,filename,runnr):
        deleted = files.deleteAllHigher(filename,runnr)
        if len(deleted)>0:
            strings =["Deleted"]
            strings.extend(deleted)
            self.printstatus(jobnr,strings)
    def copyinput(self,jobnr):
        path = self.gettemppath(jobnr)
        for k,v in self.getinputfiles(jobnr).iteritems():
            self.copymove(jobnr,self.workpath+v,path+k)
        if self.useoldFiles:
            for filename in self.oldinputfiles:
                oldFile = self.getoldFile(jobnr,filename[0])
                self.copymove(jobnr,oldFile,path+filename[1])
        if (not self.sequential or jobnr==0) and self.copyWAVECARforth:
            if self.useoldFiles:
                oldFile = self.getoldFile(jobnr,"WAVECAR")
                self.copymove(jobnr,oldFile,path+"WAVECAR")
            else:
                self.copymove(jobnr,self.workpath+"WAVECAR",path+"WAVECAR")

    def copyresult(self,jobnr,runnr):
        savepath = self.workpath+self.getparfolder(jobnr)
        if self.testrun:
            print "savepath "+savepath
            return True
        print "saving in: "+savepath
        if not os.path.isdir(savepath):
            os.mkdir(savepath)
        path = self.gettemppath(jobnr)
        success = True
        for importantfile in ["mist","CONTCAR","OSZICAR","OUTCAR","vasprun.xml"]:
            if not os.path.isfile(path+importantfile):
                success = False
                self.printstatus(jobnr,["file not found:",path+importantfile])
            elif not os.path.getsize(path+importantfile)>0:
                success = False
                self.printstatus(jobnr,["file empty:",path+importantfile])
            if not success:
                print "postprocess broken? ("+self.getparfolder(jobnr)+")"
        if self.oldFilesPath == self.workpath:
            runnr = files.getHighestNumber(savepath+self.workfiles[1][1])
        for workfile in self.workfiles:
            self.deletehigher(jobnr,savepath+workfile[1],runnr)
            self.copymove(jobnr,path+workfile[0],savepath+workfile[1]+str(runnr),workfile[2])
        if self.copyWAVECARback:
            self.deletehigher(jobnr,savepath+"WAVECAR",runnr)
            self.copymove(jobnr,path+"WAVECAR",savepath+"WAVECAR"+str(runnr))
        self.copymove(jobnr,path+"CONTCAR",path+"POSCAR",True)
        return success
    def clean(self,jobnr):
        path = self.gettemppath(jobnr)
        if not self.testrun and (not self.sequential or jobnr == self.calcruns(1)-1):
            shutil.rmtree(path,True)
    def startjob(self,jobnr):
        print "starte job"
        runfile="test.sh"
        if not self.testrun:
            runfile=self.runfile
        scriptname="run.sh"
        path =self.gettemppath(jobnr)
        self.startedcalcs +=1
        decimalcount = int(math.floor(math.log10(self.calculations)))
        fullname = self.name+("_%"+str(decimalcount+1)+"d/%d")%(self.startedcalcs,self.calculations)
        fullname = fullname.replace(" ","0")
        print "Name: "+fullname+" in folder: "+path
        script = pbs.makescript(path,runfile,self.nodes,self.ppn,self.queue,fullname,self.email,self.outpath,self.memorymultiplikator,self.hours,self.pbsparameters)
        scriptfile =path+scriptname
        files.writefile(scriptfile,script)
        jobid =pbs.qsub(scriptfile)
        open(self.jobidfile,"a").write(jobid+"\n")
        return jobid
    def managefinishedjobs(self):
        for finishedjobnr in pbs.qcheck(self.jobs):
            run = 0
            if self.jobruns.has_key(finishedjobnr):
                run = self.jobruns[finishedjobnr]+1
            else:
                run = 1
            success = self.copyresult(finishedjobnr,run)
            if run == self.detailedruns[finishedjobnr] or not success:
                self.clean(finishedjobnr)
                pbs.deljobidfromfile(self.jobidfile,finishedjobnr)
                del self.jobs[finishedjobnr]
                for prozess in self.postexec:
                    if prozess.has_key("call"):
                        call = [self.replaceDirectory(finishedjobnr,s) for s in prozess["call"]]
                        print "call: "+" ".join(call)
                        cwd= os.getcwd()
                        if prozess.has_key("workpath"):
                            cwd=self.replaceDirectory(finishedjobnr,prozess["workpath"])
                        print "workpath: "+cwd
                        time.sleep(1)
                        try:
                            p= sub.Popen(call,cwd=cwd,stdin=sub.PIPE)
                            if prozess.has_key("stdin"):
                                inp = self.replaceDirectory(finishedjobnr,prozess["stdin"])
                                print "input: " + inp
                                p.communicate(input=inp)
                            p.wait()
                            time.sleep(1)
                        except:
                            print "postexec failed"
            else:
                self.jobruns[finishedjobnr] = run
                self.jobs[finishedjobnr] = self.startjob(finishedjobnr)
            self.finishedcalcs +=1
            print "aktive jobs:"+str(len(self.jobs))+" Fertig:"+str(self.finishedcalcs)+"/"+str(self.calculations)
    def getoldFile(self,jobnr,filename):
        oldpath=""
        if self.oldFilesPath == self.workpath or self.oldFilesPath=="":
            oldpath= self.workpath
            run = files.getHighestNumber(oldpath)
            self.detailedruns[jobnr]=run+1
            self.jobruns[jobnr]=run
        else:
            oldpath=self.oldFilesPath
        if len(files.getDirectories(oldpath))==1:
            oldpath = files.getDirectories(self.oldFilesPath)[0]+filename
        else:
            oldpath= oldpath+self.getparfolder(jobnr,usepar2=self.oldusedparameters2)+filename
        newfile = [oldpath]
        print "searching in "+oldpath
        if not files.getHighestVersion(newfile):
            return ""
        if os.path.isfile(newfile[0]):
            return newfile[0]
        else:
            return ""
    def getinputfiles(self,jobnr):
        inputs = {}
        for k,v in self.inputfiles.iteritems():
            filename = v
            for i in range(len(self.parameters)):
                if k == self.parameters[i][0]:
                    filename=self.getpar(jobnr,parnr=i+1)
            for i in range(len(self.parameters2)):
                if k == self.parameters2[i][0]:
                    filename=self.getpar(jobnr,par=2,par2nr=i+1)
            inputs[k]=filename
        return inputs


    def gettemppath(self,jobnr):
        if self.sequential:
            jobnr=0
        path=self.temppath+"d"+str(self.tempdirstart+jobnr)+"/"
        if not os.path.isdir(path):
            os.mkdir(path)
        return path
    def calcruns(self,parnr=1,par2=True,par2nr=1):
        par1runs = len(self.parameters[parnr-1][1])
        par2runs = 1
        if len(self.parameters2)>=par2nr and par2:
            par2runs = len(self.parameters2[par2nr-1][1])
        return par1runs*par2runs
    def getparas(self,jobnr,vconf):
        d = dict()
        for i in range(len(self.parameters)):
            newpar=self.getpar(jobnr,parnr=i+1)
            par=newpar
            name = self.parameters[i][0]
            l =len(self.parameters[i])
            if l>2:
                if d.has_key(name):
                    par = d[name]
                else:
                    par = vconf.getparameter(name)
                if l>3:
                    par[self.parameters[i][2]-1][self.parameters[i][3]-1]=newpar
                else:
                    par[self.parameters[i][2]-1]=newpar
            d[name]=par
        for i in range(len(self.parameters2)):
            newpar=self.getpar(jobnr,par=2,par2nr=i+1)
            par=newpar
            name = self.parameters2[i][0]
            l =len(self.parameters2[i])
            if l>2:
                if d.has_key(name):
                    par = d[name]
                else:
                    par = vconf.getparameter(name)
                if l>3:
                    par[self.parameters2[i][2]-1][self.parameters2[i][3]-1]=newpar
                else:
                    par[self.parameters2[i][2]-1]=newpar
            d[name]=par
        return d
    def getpar(self,jobnr,par=1,parnr=1,par2nr=1):
        par1runs = self.calcruns(par2=False)
        if len(self.parameters2)>0 and par==2:
            return self.parameters2[par2nr-1][1][jobnr/int(par1runs)]
        return self.parameters[parnr-1][1][jobnr%par1runs]
    def getparfolder(self,jobnr,parnr=1,par2nr=1,usepar2=True):
        if(len(self.parameternames)==self.calcruns()):
            return self.parameternames[jobnr]+"/"
        value = self.getpar(jobnr,parnr=parnr)
        try:
            valuestring = "%.4f"%value
        except:
            valuestring =value
        foldername = self.parameters[parnr-1][0]+"_"+valuestring
        if len(self.parameters2)>0 and usepar2:
            value = self.getpar(jobnr,par=2,par2nr=par2nr)
            try:
                valuestring = "%.4f"%value
            except:
                valuestring =value
            foldername=foldername+"+"+self.parameters2[par2nr-1][0]+"_"+valuestring
        else:
            if(len(self.parameters)>parnr):
                value = self.getpar(jobnr,parnr=parnr+1)
                try:
                    valuestring = "%.4f"%value
                except:
                    valuestring =value
                foldername = foldername+"+"+self.parameters[parnr][0]+"_"+valuestring
        return foldername+"/"
    def replaceDirectory(self,jobnr,filestring=""):
        if filestring.find("%workpath")>-1:
            path = self.gettemppath(jobnr)
            filestring = filestring.replace("%workpath",path)
        if filestring.find("%savepath")>-1:
            path = self.workpath+self.getparfolder(jobnr)
            filestring = filestring.replace("%savepath",path)
        if filestring.find("%highest")>-1:
            fullfilename=filestring.rsplit(":",1)
            path = fullfilename[0].replace("%highest","")
            newfile = [path+fullfilename[1]]
            if not files.getHighestVersion(newfile):
                return ""
            filestring=newfile[0]
        return filestring
    def setTempdirstart(self,count):
        if self.sequential:
            count=1
        file =self.temppath+self.tempdirstartfile
        if os.path.isfile(file):
            self.tempdirstart = int(files.readfile(file)[0])
        else:
            self.tempdirstart=1
        files.writefile(file,"%.0d"%(self.tempdirstart+count+1))
    def run(self):
        if self.sequential:
            self.maxjobs=1;
        self.fixparameters[vconf.par.Nparallel]=vconf.getnpar(self.ppn*self.nodes)
        if self.fixparameters[vconf.par.Nparallel] > self.maxnpar:
            self.fixparameters[vconf.par.Nparallel] = self.maxnpar
        self.fixparameters[vconf.par.LPlane]=".TRUE."
        if self.testrun:
            self.sleepduration=10
        i = 0
        iend = self.calcruns(1)
        self.setTempdirstart(iend)
        self.calculations= iend*self.runs
        print "Datenpunkte: "+"%.0d"%round(iend)
        while i < iend:
            for link in self.linkfilestodir:
                if os.path.isfile(link):
                    linkname = self.gettemppath(i)+os.path.basename(link)
                    if os.path.lexists(linkname):
                        os.remove(linkname)
                    os.symlink(link,linkname)
            self.detailedruns[i]=self.runs
            self.copyinput(i)
            conf = vconf.vaspconfig(self.gettemppath(i))
            conf.highestFileVersion = False
            paras = self.getparas(i,conf)
           # if not self.oldFilesPath:
            if self.oldFilesPath == "" or (not self.oldFilesPath == "" and self.changeoldFiles):
                for key,val in paras.iteritems():
                    self.fixparameters[key]=val
            if not vconf.par.Potpath in self.fixparameters:
                self.fixparameters[vconf.par.Potpath] =self.potcarpath
            if not vconf.par.Pottype in self.fixparameters:
                self.fixparameters[vconf.par.Pottype] =self.potcartype
            conf.setparameter(self.fixparameters)
            for prozess in self.preexec:
                prozess = [self.replaceDirectory(i,s) for s in prozess]
                time.sleep(1)
                sub.Popen(prozess)
                time.sleep(1)
            self.jobs[i] = self.startjob(i)
            while len(self.jobs) >= self.maxjobs:
                time.sleep(self.sleepduration)
                self.managefinishedjobs()
            i+=1
        while len(self.jobs)>0:
            time.sleep(self.sleepduration)
            self.managefinishedjobs()
        print "Fertig"
pass
