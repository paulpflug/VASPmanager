# -*- coding: utf-8 -*-
import math
import types
import numpy as np
def toMatrix(array2d):
    return np.array([[float(x)for x in arr] for arr in array2d])
def signif(x,n=1):
    if n>0 and x!=0:
        order = math.floor(math.log10(x))
        fac = 10**(order-(n-1))
        x=fac*float(round(x/fac))
    return x
def inverse(x):
    if type(x) is not types.ListType:
        return 1./x
    for i in range(0,len(x)):
        x[i] = 1./x[i]
    return x
def cbind(listoflists):    
    length=len(listoflists[0])
    result=[[] for i in xrange(length)]
    for item in listoflists:
        if len(item)!= length:
            return False
        for index,value in enumerate(item):            
            if isinstance(value,list):
                result[index]+=value
            else:
                result[index].append(value)
    return result
def range(start,stop,step):
    result=[start]
    i=step
    while i<stop:
        result.append(i)
        i+=step
    return result
def length(vector):
    return math.sqrt(float(vector[0])**2+float(vector[1])**2+float(vector[2])**2)
def joinlists(list1,list2):
    result=list()
    if len(list1)== len(list2):
        for i in range(0,len(list1)):
            obj1 =list1[i]
            obj2 =list2[i]
            if type(obj1) is not types.ListType:
                obj1 = [obj1]
            if type(obj2) is not types.ListType:
                obj2 = [obj2]
            result.append(obj1+obj2)
    return result
    
def uniqify(seq): 
   seen = {}
   result = []
   for item in seq:
       if item in seen: 
           seen[item] = seen[item]+1
           continue
       seen[item] = 1
       result.append(item)
   del seq[:]
   for item in result:
       seq.append(item)
   counts =[]
   for item in result:
       counts.append(seen[item])
   return counts
   
def arguniqifyvectors(matrix): 
   seen = np.asmatrix(matrix[0])
   arg = [0]
   for i,vec1 in enumerate(matrix):
       append=True
       for vec2 in seen:
           if np.linalg.norm(vec1-vec2)<0.0001:
               append=False
               continue
       if append:
           arg.append(i)
           seen = np.append(seen,[vec1],axis=0)
   return arg