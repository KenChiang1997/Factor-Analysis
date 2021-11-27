import numpy as np 
import pandas as pd
import matplotlib.pyplot as plt 
from scipy.spatial import ConvexHull


def portfolio_convex_hull(CovexHull_DF):
    
    """
    CovexHull_DF Columns : Annual Std ,Returns 
                 Index   : Portfolio
    """

    CovexHull_Dataset   = CovexHull_DF.values
    Unbiased_Std         = CovexHull_DF['Unbiased_Std']
    Expected_Return     = CovexHull_DF['Expected_Returns']
    hull   = ConvexHull(CovexHull_Dataset)


    print(" "*10 + "Equities Covex Hull" )
    print("--" * 20)
    print(CovexHull_DF)
    print("--" * 20)

    # Figure
    fig,ax = plt.subplots(figsize=(8,8))
    ax.set_title('Equities Covex Hull')
    ax.scatter(Unbiased_Std,Expected_Return,color='blue')

    for i in range(Expected_Return.shape[0]):
        ax.annotate(CovexHull_DF.index[i],xy=(Unbiased_Std[i],Expected_Return[i]))

    for simplex in hull.simplices:
        plt.plot(CovexHull_Dataset[simplex, 0], CovexHull_Dataset[simplex, 1], 'k-')

    ax.set_ylabel('Annual Returns')
    ax.set_xlabel('Annual Std')


