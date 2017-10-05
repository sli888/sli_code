import numpy as np
#classification NN
import pandas as pd
def nn (x,w):
    return np.dot(x,w)

def sig (x,dev):
    if (dev==1):
        return x*(1-x)
    else:
        return 1/(1+np.exp(-x))


#layerdef is a list which contains number demention of each hidden layer

def model (x,layerdef):
    W={} #hash of all Weights
    O={} #hash of all output
    indim =x.shape[1] #input dimention
    layerdefnew = list(layerdef)
    layerdefnew.insert(0,indim) #insert the begining matrix 
    for i in range (len(layerdefnew)-1):
        idim=layerdefnew[i]
        odim=layerdefnew[i+1]
        W[i] = 2 *np.random.random ((idim,odim))-1 #random from 0
    return W

def forwardprop (x,W,layerdef):  #nlayer starting from 0
    O={}
    for i in range(len(layerdef)):
        if i ==0:
            O[i] = sig (nn (x,W[i]),0)
        else:
            O[i] = sig(nn (O[i-1],W[i]),0)
    return O

def backprop (x,W,y,layerdef,roh):
    O = forwardprop (x,W,layerdef)
 #   print ("O is\n",O)
 #   print ("W is\n",W)
    G={}
    E={}
    for i in reversed(range(len(layerdef))):
        #print ("the i is",i)
        if i == len(layerdef)-1:
            E[i] = y-O[i]
            G[i] = E[i] * sig (O[i],1)  
            error = E[i]
            #error = np.mean(np.abs(E(i)))
            #print ("the error is\n", error)
        else:
            E[i] = np.dot(G[i+1], W[i+1].T) 
            G[i] = E[i] * sig (O[i],1)

        if (i>0):
            W[i] += np.dot(O[i-1].T, G[i])*roh
        else:
            W[i] += np.dot(x.T, G[i])*roh
    return W, error

def train (x,W,y,layerdef,itter,roh):
    for j in range (itter):
        W, error= backprop (x,W,y,layerdef,roh)
        errornum = np.dot(error.T, error)
        
        print (j, errornum)
        
 
#       print (j, W)
    return W

def minmax (x):
    scale = (x-x.min())/(x.max()-x.min())
    return scale,x.min(),x.max()

def minmax_1 (x,mi,ma):
    scale = (x-mi)/(ma-mi)
    return scale

def minmax_rev (x,mi,ma):
    rev =  x*(ma-mi)+mi
    return rev

       

price = pd.read_csv("baba.csv")





indates = 14
outdate = 1
numdate = len (price)
x = []
y = []
#for i in range (int(numdate/indates)):
for i in range (14):
    startindex = i*indates
    endindex = (i+1)*indates-1
    if (endindex < numdate):
        x=x+[list(price['Close'][startindex:endindex])]
        y=y+[[price['Close'][endindex+1]]]                        
         


x= np.array(x)
y= np.array(y)
xnorm, min_x, max_x = minmax (x) 
ynorm = minmax_1 (y,min_x,max_x) 

print (xnorm,ynorm)

layerdef = [30,30,30,1]
#x=np.random.random ((6,4))                    
#y=np.random.random ((6,1))
W=model(xnorm,layerdef)  
W=train (xnorm,W,ynorm,layerdef,100000,0.1)

            
#tempout= forwardprop(x,W,layerdef)
#print(tempout)
#print (y)                     
