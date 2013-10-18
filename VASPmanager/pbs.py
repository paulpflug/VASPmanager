import vaspconfig as vconf
import re
import subprocess as sub
def makescript(path,filename,nodes,ppn,queue,name,email,outpath,memorymultiplikator=1,hours=1,parameters=""):
    temp = """\
#!/bin/bash
#
#PBS -l nodes=%d:ppn=%d%s
#PBS -l mem=%dmb
#PBS -l walltime=%d:00:00
#PBS -q %s
#PBS -j oe
#PBS -N %s
#PBS -M %s
#PBS -o %s
#
cd %s
%s
"""
    return temp %(nodes,ppn,parameters,nodes*vconf.getnpar(ppn)*2048*memorymultiplikator,hours,queue,name,email,outpath,path,filename)


def qsub(file):
    out = sub.Popen(["qsub" , file],stdout=sub.PIPE)
    out, err = out.communicate()
    jobid = re.search("\d{5,7}",out).group(0)
    print "Job: "+jobid+" gestartet"
    return jobid

def qcheck(jobdict):
    finishedjobs = []
    for nr,job in jobdict.iteritems():
        out = sub.Popen(["qstat", job],stdout=sub.PIPE,stderr=sub.PIPE)
        out, err = out.communicate()
        if err != "":
            finishedjobs.append(nr)
    return finishedjobs

def qrem(jobs):
    for job in jobs:
        out= sub.Popen(["qdel", job],stdout=sub.PIPE,stderr=sub.PIPE)
        out.wait()

def deljobidfromfile(file,jobid):
    s=open(file,"r").read()
    s=re.sub(str(jobid)+"\n","",s,1)
    open(file,"w").write(s)
