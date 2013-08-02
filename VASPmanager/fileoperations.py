import os
def readfile(fullfilename):
    f=open(fullfilename,"r") 
    readData = f.readlines()
    f.close()
    return readData
def writefile(fullfilename,data):
    if os.path.isfile(fullfilename):
        f=open(fullfilename,"r")
        s = f.readlines()
        f.close()
        if not "".join(s)==data:
            f=open(fullfilename,"w")
            f.writelines(data)
            f.close()
    else:
        f=open(fullfilename,"w")
        f.writelines(data)
        f.close()
def writeDictionaryToFile(fullfilename,dictionary):
    s=[]
    for k,v in dictionary.iteritems():
        s.append(k+"="+str(v)+"\n")
       # if len(v)>1:
       #     s.append(k+"="+" ".join(v)+"\n") 
       # else:
        
    writefile(fullfilename,s)        
def toLine(a):
    return str(a)+"\n"
def vecToLine(vec=[],Int=False):
    s = ""
    for i in vec:
        val = i        
        if Int:
            val= int(i)        
        s = s+str(val)+" "        
    return toLine(s.rstrip())
def matrixToLine(matrix=[[]]):
    """takes lists in list"""
    s=""        
    for i in matrix:
        s=s+vecToLine(i)
    return s
def getDirectories(path,fullpath=True):
    folders = []
    if os.path.isdir(path):
        if path[-1] != "/":
            path+="/"
        folders1 = os.listdir(path)        
        for f in folders1:
            if os.path.isdir(path+f):
                if fullpath:
                    folders.append(path+f+"/")
                else:
                    folders.append(f+"/")
    return folders
def deleteAllHigher(fullfilename,number):
    i=number+1
    deleted = []
    while os.path.isfile(fullfilename+str(i)):
        os.remove(fullfilename+str(i))
        deleted.append(fullfilename+str(i))
        i+=1
    return deleted
def getHighestNumber(fullfilename):
    i=1
    while os.path.isfile(fullfilename+str(i)):
        i+=1
    if os.path.isfile(fullfilename+str(i-1)):
        return i-1
    else:
        return 0
def getHighestVersion(outfullfilename):
    filename = outfullfilename[0]
    i = getHighestNumber(filename)
    if i>0:
        outfullfilename[0] = filename+str(i)
        return True
    else:
        if os.path.isfile(filename):
            return True
    return False
def tail( f, window=20 ):
    BUFSIZ = 1024
    f.seek(0, 2)
    bytes = f.tell()
    size = window
    block = -1
    data = []
    while size > 0 and bytes > 0:
        if (bytes - BUFSIZ > 0):
            # Seek back one whole BUFSIZ
            f.seek(block*BUFSIZ, 2)
            # read BUFFER
            data.append(f.read(BUFSIZ))
        else:
            # file too small, start from begining
            f.seek(0,0)
            # only read what was not read
            data.append(f.read(bytes))
        linesFound = data[-1].count('\n')
        size -= linesFound
        bytes -= BUFSIZ
        block -= 1
    return '\n'.join(''.join(data).splitlines()[-window:])