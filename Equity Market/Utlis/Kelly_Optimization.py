import cvxpy as cp 
import numpy as np 
import pandas as pd


class Kelly_Portfolio_Optimization():
    
    def __init__(self,u,risk_free_rate,cov):

        self.u      = u
        self.rf     = risk_free_rate
        self.cov    = cov 
        self.params = cp.Variable(cov.shape[1])

    def constraint_1(self): # Weights Sum 1
        
        return cp.sum(self.params) == 1  

    def constraint_2(self): # Short Constriants

        bound = [ self.params[i] >= float(1e-20) for i in range(self.cov.shape[1]) ] 

        return bound 

    def Optimize(self):

        constraints = []
        constraints.extend( [self.constraint_1()] )
        constraints.extend(  self.constraint_2() )
        
        Objective_Function = self.rf + (self.u - self.rf).T @ self.params  - (1/2) *  cp.quad_form(self.params ,self.cov) 
  

        prob  = cp.Problem( cp.Maximize(Objective_Function) , constraints )
        
        return prob , self.params