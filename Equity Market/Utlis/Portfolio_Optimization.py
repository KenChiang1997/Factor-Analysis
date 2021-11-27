# basic
import cvxpy as cp 
import numpy as np 
import pandas as pd
import datetime as dt 
# yahoo data source
import yfinance as yf 
from pandas_datareader import  data as pdr 

# optimization package
from scipy.optimize import minimize
from scipy.spatial import ConvexHull, convex_hull_plot_2d

# matplotlib
import matplotlib.pyplot as plt 


# HW 5 
class CVX_Shortfall_Risk_Optimization():
    
    def __init__(self,u,cov,shortfall_risk,chance):

        self.u      = u 
        self.chance = chance
        self.cov    = cov 
        self.params = cp.Variable(cov.shape[1])
        self.shortfall_risk = shortfall_risk

    def constraint_1(self,params):
        
        return  [ cp.sum(params) <= 2 ]  # Allow leverage 
    
    def constraint_2(self,params):

        bound = [ cp.abs(params[i]) <= 2 for i in range(self.cov.shape[1])] # weights Bound Constriants

        return bound 
    
    def constraint_3(self,params):
        
        chance_paramter = np.sqrt(self.chance/(1-self.chance))
        left_norm2      = np.sqrt(self.cov) @ params  * chance_paramter        
        right           = self.u.T @  params  - self.shortfall_risk/252

        return [ cp.SOC(right , left_norm2) ]


    def Optimize(self):

        constraints = []
        constraints += self.constraint_1(self.params) 
        constraints += self.constraint_2(self.params) 
        constraints += self.constraint_3(self.params) 
        
        Objective_Function = self.u @ self.params  - (1/2) * cp.quad_form(self.params ,self.cov) 

        prob  = cp.Problem( cp.Maximize(Objective_Function) , constraints )
        
        return prob , self.params



class CVX_Markowitz_Optimization():
    
    def __init__(self,u,cov):

        self.u      = u
        self.cov    = cov 
        self.params = cp.Variable(cov.shape[1])

    def constraint_1(self) :
        
        return [ cp.sum(self.params) <= 2 ] # Weights Sum 1 

    def constraint_2(self) :

        bound = [ cp.abs(self.params[i]) <= 2 for i in range(self.cov.shape[1])]

        return bound 
    

    def Optimize(self) :

        constraints = []
        constraints +=  self.constraint_1() 
        constraints +=  self.constraint_2()
        
        Objective_Function = self.u.T @ self.params  - (1/2) *  cp.quad_form(self.params ,self.cov) 
        prob               = cp.Problem( cp.Maximize(Objective_Function) , constraints )
        
        return prob , self.params

    

class CVX_Shortfall_Risk_Uncertainty_Optimization():
    
    def __init__(self,u,cov,shortfall_risk,chance):

        self.u      = u 
        self.chance = chance
        self.cov    = cov 
        self.params = cp.Variable(cov.shape[1])
        self.v      = cp.Variable(1)
        self.shortfall_risk = shortfall_risk

    def constraint_1(self,params):
        
        return  [ cp.sum(params) <= 2 ]  # Allow leverage 
    
    def constraint_2(self,params):

        bound = [ cp.abs(params[i]) <= 2 for i in range(self.cov.shape[1])] # weights Bound Constriants

        return bound 
    
    def constraint_3(self,params):
        
        chance_paramter = np.sqrt(self.chance/(1-self.chance))
        left_norm2      = np.sqrt(self.cov) @ params  * chance_paramter        
        right           = self.u.T @  params  - self.shortfall_risk/252

        return [ cp.SOC(right , left_norm2) ]


    def Optimize(self):

        constraints = []
        constraints += self.constraint_1(self.params) 
        constraints += self.constraint_2(self.params) 
        constraints += self.constraint_3(self.params) 
        constraints += [ self.u == self.u * (1+self.v) , self.cov == self.cov*(1+self.v)  ,  self.v <= 0.4  , self.v >= -0.5]


        Objective_Function = self.u @ self.params  - (1/2) * cp.quad_form(self.params ,self.cov) 
        prob               = cp.Problem( cp.Maximize(Objective_Function) , constraints )
        
        return prob , self.params , self.v