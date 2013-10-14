VASPmanager
=====
Tool for managing VASP calculations on a PBS based cluster

### Workflow
To be somewhat efficent, even in research, I developed a workflow for scientific computation, which works quite well for me.
![scientific computation - workflow](../../raw/master/examples/workflow-01.png "scientific computation - workflow")
Rvasp can be found [here](https://github.com/paulpflug/Rvasp)

### Important
Many features originated by a need to solve a specific problem and are propably not generalized enough to declare the general problem fully solved.
All functions are implemented in pure python and are easy to understand. Feel free to read the [source](../../tree/master/VASPmanager/VASPmanager), improve and submit changes.

### Install
#### Tarball as a package
* download [VASPmanager package](https://www.dropbox.com/s/uwo9w7jklokc1pc/VASPmanager-0.1.0.tar.gz)
* install in shell

```
easy_install VASPmanager-0.1.0.tar.gz
```
#### Sourcecode as a package
* download zip from the right
* extract and go to setup.py in VASPmanager-master/
* install in shell
```
python setup.py install
```

#### Raw sourcecode
* clone or download & extract zip from the right
* maybe add VASPmanager/ directory to PYTHONPATH in .profile
```
export PYTHONPATH=$PYTHONPATH:/your/path/to/VASPmanager
```

### What it does
VASPmanager manages a calculation at a PBS based cluster for you. A calculation here is not a single VASP run, but a series of connected VASP runs.
VASPmanager helping you to create, monitor and cleanup your calculations.
#### Calculation creation
The heart of VASPmanager is the setting of calculation parameters, which will be explained later. The process of calculation creation consists of the following steps:
* creating a temporary folder structure
* filling these folders with the right files, this includes a logic for finding the POTCAR and (optional) files of preceding calculations
* setting the parameters
* submitting the job
#### Calculation monitoring
This is a very simple step. VASPmanager constantly checks if a calculation is finished to start the postprocessing. (This done on the mainframe, also to avoid problems with job interuptions)
#### Calculation cleanup
The cleanup consists of saving the needed files in a clean, simple pattern and deleting the temporary folders


### Usage
The package mainly consists of two classes. The ```job``` class manages everything concerning the calculation and the ```par``` class yields the access to the configuration.These classes have to be imported.
#### Installed as a package
If you installed the package use ```import VASPmanager as vm``` to import the package, ```j = vm.job()``` to initiate a job and ```vm.par``` to access the configuration.
#### Using raw source
When using the raw sourcecode, you can import the two classes like this this:
```
from vaspconfig import par
from job import job
```
usage will then be ```j = job()``` to initiate a job and ```vm.par``` to access the configuration.

####
