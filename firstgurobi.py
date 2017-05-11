# -*- coding: utf-8 -*-
from gurobipy import *

#简单的数据初始化
V=6
''''可能会存在一个c'''
C=[0,10,0,0,5,0,
   10,0,0,0,0,6,
   0,0,0,14,3,0,
   0,0,14,0,0,8,
   5,0,3,0,0,4,
   0,6,0,8,4,0]
W=3
sts=['1-2','1-3','1-4']

dst={}
dst[sts[0]]=[1,2,0]
dst[sts[1]]=[1,2,3]
dst[sts[2]]=[0,0,1]

cst=[1,2,3]

apst={}
apst[sts[0]]=[2,3,0]
apst[sts[1]]=[4,6,3]
apst[sts[2]]=[0,0,6]

B=[8,8,8,8,10,10]
e=[0,1,0,0,1,0,
   1,0,0,0,0,1,
   0,0,0,1,1,0,
   0,0,1,0,0,1,
   1,0,1,0,0,1,
   0,1,0,1,1,0]


#后面再去试图变成一个读入文本的结构吧

try:
# Create a new model
    m = Model("test")

# Create variables
    x={}
    for st in range(0,len(sts)):
        for i in range(0,V):
            for j in range(0,V):
                x[st*V*V+i*V+j]=m.addVar(vtype=GRB.BINARY, name="x"+sts[st]+"-"+str(i+1)+str(j+1))
    y={}
    for st in range(0,len(sts)):
        for i in range(0,V):
            y[st*V+i]=m.addVar(vtype=GRB.BINARY, name="y"+sts[st]+"-"+str(i+1))
    g={}
    for st in range(0,len(sts)):
        for i in range(0,V):
            for p in range(0,W):
                g[st*V*W+i*V+p]=m.addVar(vtype=GRB.BINARY, name="g"+sts[st]+"-"+str(i+1)+str(p+1))
    u={}
    for st in range(0,len(sts)):
        for i in range(0,V):
            u[st*V+i]=m.addVar(vtype=GRB.INTEGER, name="u"+sts[st]+"-"+str(i+1))
            
    u0 = m.addVar(vtype=GRB.INTEGER, name="u0")

# Integrate new variables
    m.update()

# Set objective
    m.setObjective(u0, GRB.MINIMIZE)

# Add constraint: 
    for st in range(0,len(sts)):
        for i in range(0,V):
            for j in range(0,V):
                if i == j:
                    m.addConstr(x[st*V*V+i*V+j] == 0)

    tmp6={}
    tmp7={}
    for st in range(0,len(sts)):
        arr = sts[st].split('-')
        s = eval(arr[0]) - 1
        t = eval(arr[1]) - 1
        for j in range(0,V):
            tmp6[j] = 0
            tmp7[j] = 0
            for i in range(0,V):
                tmp6[j] = tmp6[j] + x[st*V*V+i*V+j]
            for k in range(0,V):
                tmp7[j] = tmp7[j] + x[st*V*V+j*V+k]
            if j == t:
                m.addConstr(tmp6[j] - tmp7[j] == 1)
            elif j == s:
                m.addConstr(tmp7[j] - tmp6[j] == 1)
            else:
                m.addConstr(tmp6[j] - tmp7[j] == 0)
 
    tmp4={}
    tmp5={}
    for st in range(0,len(sts)):
        for i in range(0,V):
            tmp4[i] = 0
            tmp5[i] = 0
            for j in range(0,V):
                tmp4[i] = tmp4[i] + x[st*V*V+i*V+j]
                tmp5[i] = tmp5[i] + x[st*V*V+j*V+i]
            m.addConstr(tmp4[i] <= y[st*V+i])
            m.addConstr(tmp5[i] <= y[st*V+i])
            m.addConstr(y[st*V+i] <= tmp4[i] + tmp5[i])

    for st in range(0,len(sts)):
        for i in range(0,V):
            for p in range(0,W):
                m.addConstr(g[st*V*W+i*V+p] - y[st*V+i] <= 0)

    for st in range(0,len(sts)):
        for i in range(0,V):
            for j in range(0,V):
                m.addConstr(x[st*V*V+i*V+j] - e[i*V+j] <= 0)

    tmp1={}
    for st in range(0,len(sts)):
        for p in range(0,W):
            tmp1[st*W+p] = 0
            for i in range(0,V):
                tmp1[st*W+p] = tmp1[st*W+p] + g[st*V*W+i*V+p]
            m.addConstr(tmp1[st*W+p] == 1)

    for st in range(0,len(sts)):
        for i in range(0,V):
            m.addConstr(u[st*V+i] >= 1)
            m.addConstr(u[st*V+i] <= V)

    for st in range(0,len(sts)):
        for i in range(0,V):
            for j in range(0,V):
                m.addConstr(u[st*V+i] - u[st*V+j] + V * x[st*V*V+i*V+j] <= V - 1)

    for st in range(0,len(sts)):
        for p in range(0,W):
            for q in range(0,W):
                for i in range(0,V):
                    for j in range(0,V):
                        m.addConstr((dst[sts[st]][q] - dst[sts[st]][p]) * (u[st*V+i] - u[st*V+j])<= W * V * (2 - g[st*V*W+i*V+p] - g[st*V*W+i*V+q]))

    tmp2={}
    for i in range(0,V):
        tmp2[i] = 0
        for st in range(0,len(sts)):
            for p in range(0,W):
                tmp2[i] = tmp2[i] + g[st*V*W+i*V+p] * apst[sts[st]][p]
        m.addConstr(tmp2[i] <= B[i])

    '''tmp3={}
    for i in range(0,V):
        for j in range(0,V):
            tmp3[i*V+j] = 0
            for st in range(0,len(sts)):
                tmp3[i*V+j] = tmp3[i*V+j] + x[st*V*V+i*V+j] * cst[st]
            m.addConstr(tmp3[i*V+j] <= u0)'''

    tmp3=0
    for st in range(0,len(sts)):
        for i in range(0,V):
            for j in range(0,V):
                tmp3 = tmp3 + x[st*V*V+i*V+j] * cst[st] * C[i*V+j]
        m.addConstr(tmp3 <= len(sts)*u0)
    

    m.optimize()
    for v in m.getVars():
        print (v.varName, v.x)
    print ('Obj:', m.objVal)





except GurobiError:
    print ('Error reported')

