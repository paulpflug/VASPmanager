VASPmanager
=====
Tool for managing VASP calculations on a PBS based cluster

### Workflow
To be somewhat efficent, even in research, I developed a workflow for scientific computation, which works quite well for me.
![scientific computation - workflow](../../raw/master/examples/workflow-01.png "scientific computation - workflow")
Rvasp can be found [here](https://github.com/paulpflug/Rvasp)

### Important
This tool was created for simple and fast PBS Job managing and is currently only used for my specific applications. There is the probability, that you find situations where it is not obeying your command. Feel free to read the [source](../../tree/master/VASPmanager/VASPmanager), improve it and submit changes.
The tool is implemented in pure python and most of it is easy to understand.

### Install
##### Tarball as a package
* download [VASPmanager package](https://www.dropbox.com/s/uwo9w7jklokc1pc/VASPmanager-0.1.0.tar.gz)
* install in shell

```Shell
easy_install VASPmanager-0.1.0.tar.gz
```
##### Sourcecode as a package
* download zip from the right
* extract and go to setup.py in VASPmanager-master/
* install in shell

```Shell
python setup.py install
```

##### Raw sourcecode
* clone or download & extract zip from the right
* (optional) add VASPmanager/ directory to PYTHONPATH in your .profile

```Shell
export PYTHONPATH=$PYTHONPATH:/your/path/to/VASPmanager
```

### What it does
VASPmanager manages a calculation at a PBS based cluster for you. A calculation here is not a single VASP run, but a series of connected VASP runs.
VASPmanager helping you to create, monitor and cleanup your calculations.

##### Calculation creation
The heart of VASPmanager is the setting of calculation parameters, which will be explained later. The process of calculation creation consists of the following steps:
* creating a temporary folder structure
* filling these folders with the right files, this includes a logic for finding the POTCAR and (optional) files of preceding calculations
* setting the parameters
* submitting the job

##### Calculation monitoring
This is a very simple step. VASPmanager constantly checks if a calculation is finished to start the postprocessing. (This done on the mainframe, also to avoid problems with job interuptions)

##### Calculation cleanup
The cleanup consists of saving the needed files in a clean, simple pattern and deleting the temporary folders


### Usage
The package mainly consists of two classes. The ```job``` class manages everything concerning the calculation and the ```par``` class yields the access to the configuration.These classes have to be imported.

##### Installed as a package
If you installed the package, you can use

```python
import VASPmanager as vm
j = vm.job()
vm.par.parameter
```
to import the package, initiate a job and access the configuration.

##### Using raw source
When using the raw sourcecode, it will look like this:

```python
from vaspconfig import par
from job import job
j = job()
par.parameter
```

##### Job Preparation
Create a new folder with the files you need for calculation. (Typically POSCAR, KPOINTS and INCAR). Now create a script, which will use VASPmanager to handle the parameters. Here is a prototypical script:

##### Prototypical script
script.py:

```python
#!/usr/bin/python
import os
import VASPmanager as vm
import numpy as np

j = vm.job()
###### pbs ######
j.name="JobName"
j.email="your@email.com"
j.outpath="/Path/where/PBS/output/will/be/stored"
j.nodes=1 #Nodes to use
j.ppn=1 #Number of processes per node
j.queue="QueueName"
j.hours=50  #Walltime
#################
#### Folders ####
j.workpath=os.getcwd()+"/" #Finished calculations will be stored here
j.temppath="/will/be/used/for/calculation/"
j.potcarpath="/folder/to/your/potcars/"
#################
##### Files #####
j.jobidfile="/file/where/all/jobids/will/be/stored"
j.runfile="/Vasp/binary"
#################
### Parameter ###
j.potcartype="LDA"
j.copyWAVECARback=True
a = np.arange(2,4,0.5)
j.parameters = [[vm.par.LatticeConstant,a]]
#################
###### Job ######
j.testrun=False
j.verbose=False
j.runs =1
j.maxjobs=20
j.sleepduration=60
#################
j.run()
```

#### Typical script call

```Shell
nohup python script.py &
```

#### POTCAR fetching
There is a requirement for successful POTCAR fetching.
All POTCARS have to be named in the following scheme:

```
POTCAR_[Element]_[Type]
```
and have to be placed in one folder
To access a certain POTCAR you have to provide the folder and the type in the script:

```python
j.potcarpath="/folder/to/your/potcars/"
j.potcartype="[Type]"
```

So for a silicon LDA POTCAR use: POTCAR_Si_LDA.
Which elements are used in a calculation is determined by looking at the POSCAR. The corresponding POTCARS are then fetched and merged.
The name for a POTCAR type is choosen by you, just make sure the script knows about the name.

### Parameter usage
The job class has two paramter inputs and the optional posibility to name your calculations.

```python
parameters=[]
parameters2=[]
parameternames=[]
```

```parameters``` and ```parameters2``` work the same way, here a few examples:

```python
# will create two calculations, one with KPOINTS1 and the other with
# KPOINTS2 as KPOINTS file. These calculations will be saved in the
# subfolders Subfolder1 and Subfolder2
parameters=[[vm.par.Kpoints,["KPOINTS1","KPOINTS2"]]]
parameternames=["Subfolder1","Subfolder2"]

# will create two calculations, the first will use the KPOINTS1 and the
# INCAR1 and the second the KPOINTS2 and the INCAR2 files.
parameters=[[vm.par.Kpoints,["KPOINTS1","KPOINTS2"]],
            [vm.par.Incar,["INCAR1","INCAR2"]]]

# will create four calculations, one for each kombination of INCAR1&2
# with KPOINTS1&2.
parameters=[[vm.par.Kpoints,["KPOINTS1","KPOINTS2"]]]
parameters2=[[vm.par.Incar,["INCAR1","INCAR2"]]]

# to access a single number in a matrix provide the corresponding indices.
# This example will make three calculations with the z-component of the
# third basis vector going trough 1, 2 and 3
parameters=[[vm.par.Basisvectors,[1,2,3],3,3]]
```

The optional ```parameternames``` requires only a list of names, if not provided, a name is generated by the first entries of ```parameters``` and ```parameters2```. In the case of ```parameters``` and ```parameters2``` a list of lists is required. One parameter element consists of up to 4 pieces. First the parameter name (e.g. vm.par.Basisvectors), then a list of values (e.g. [1,2,3]), which will be used for the different calculations and two optional numbers to access a single number within a vector or a matrix.
For efficent parameter calculation [numpy](http://www.numpy.org/) is recommended.


##### Currently available parameters

```python
### Basic FILES
vm.par.Poscar
vm.par.Incar
vm.par.Kpoints
vm.par.Chgcar
##### POTCAR
vm.par.Pottype # will override job.potcartype
vm.par.Potpath # will override job.potcarpath

### KPOINTS
vm.par.Kcount # 2nd line in KPOINTS
vm.par.Ktype # "l" for line-mode
vm.par.Kmesh # Vector for normal mode
vm.par.Klinetype # 4th line in KPOINTS for line-mode
vm.par.Kline # (nx3) matrix for line-mode

### POSCAR
vm.par.Basisvectors # (3x3) matrix of the basis vectors
vm.par.Atoms # [n][2] jagged array ex. [["Ag",3],["Si",6],["Ag",9]]
vm.par.Atompos # (nx3) matrix of atom positions
vm.par.Atommove # (nx3) matrix of atome movement (for selectiv dynamics)
vm.par.LatticeConstant

### INCAR
vm.par.NPAR
vm.par.NBANDS
vm.par.ENCUT
vm.par.EDIFF
vm.par.ISMEAR
vm.par.SIGMA
vm.par.NSW
vm.par.ALGO
vm.par.PREC
vm.par.ICHARG
vm.par.LCHARG
vm.par.LWAVE
vm.par.LREAL
vm.par.LPLANE
vm.par.LSCALU
vm.par.NSIM
vm.par.KPUSE
vm.par.IBAND
vm.par.EINT

```

### Job class parameters
parameters for the Job class are given with their default values.

```python
### pbs
name=""
email=""
outpath=""
nodes=1
ppn=8
queue=""
hours=1
pbsparameters=""

### Folders
workpath=""
temppath=""
oldFilesPath=""
potcarpath=""

### Files
tempdirstartfile="currenttemp" # relative to temppath
jobidfile="" # absolute
runfile="" # absolute
linkfilestodir=[] # array of files which will be soft linked in temp dir

### Parameter
j.potcartype=""
useoldFiles=False # determines if this is a consecutiv job
changeoldFiles=True # will the old files be changed according to parameters
copyWAVECARforth=True
copyWAVECARback=False
parameters=[]
parameters2=[]
parameternames=[]
# Preexec and postexec share the same scheme.
# Basically it is a array of entries, which will be forwarded to
# subprocess.Popen,
# see http://docs.python.org/2/library/subprocess.html#subprocess.Popen for usage.
# When you need to use paths, you can use the placeholders %temppath and %savepath
preexec=[] # commands which will be executed in each temp directory befor calculation
postexec=[] # commands which will be executed in each temp directory after calculation

### Job
tempdirstart=1 # counter for temp directory
maxnpar=1000 # npar is automatical calculated, this can be used to cut npar
memorymultiplikator=1 # currently 2gb/processor is assumed. The multiplikator will lower or raise the PBS requirement
maxjobs = 1 # maximum parallel jobs
sequential = False # If True, all jobs will be calculated in one folder only.
sleepduration=60 # sleep duration while checking for finished jobs
runs =1 # possibility to plan consecutive runs for all parameters. Files will be saved like this: POSCAR1, POSCAR2 ...
testrun=False # only creates folders and moves/manipulate files, no calculation
verbose=False # more information to STDOUT, will be ugly!

### Settings
# Cleanup of the job. First entry is the name of the file, second is the
# name by which it will be saved and third is wether it will be moved or
# copied. if runs is set >1 the CONTCAR is then copied over the POSCAR
# WAVECAR is handled seperatly by copyWAVECARforth and copyWAVECARback
workfiles=[["POSCAR","POSCAR",False],
          ["mist","log",True],
          ["KPOINTS","KPOINTS",False],
          ["PARCHG","PARCHG",True],
          ["CONTCAR","CONTCAR",False],
          ["INCAR","INCAR",False],
          ["OSZICAR","OSZICAR",True],
          ["OUTCAR","OUTCAR",True],
          ["vasprun.xml","vasprun.xml",True],
          ["CHGCAR","CHGCAR",False],
          ["PROCAR","PROCAR",True],
          ["EIGENVAL","EIGENVAL",True]]
# Name of the files, which are moved from working to temp directory
inputfiles={vconf.par.Incar:"INCAR",
            vconf.par.Kpoints:"KPOINTS",
            vconf.par.Poscar:"POSCAR",
            vconf.par.Chgcar:"CHGCAR"}
# If useoldFiles is True, it searches in oldFilesPath for the filename which
# is mentioned first and copies it to temp directory with the filename which
# is mentioned last
oldinputfiles=[["CONTCAR","POSCAR"],["CHGCAR","CHGCAR"]]
```
