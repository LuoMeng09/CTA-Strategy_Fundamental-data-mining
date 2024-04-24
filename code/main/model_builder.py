# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
import os
import re
from code.data_processor import *


def Winning_Ratio(data,a,b,mark_price_train,mark_signal,res,name=None):
    '''
    Calculate the win rate of the ab values that have been screened out.
    Params:
    data: A collection of factors.
    name: The name of a single instance of a factor.
    ab: The threshold values that have been screened out.
    mark_signal: The target signal.
    res: The correlation.
    '''
    mark_signal = pd.DataFrame(mark_signal)
    mark_price_train = pd.DataFrame(mark_price_train)

        
    if name == None:
        temp = data
        temp_roll = pd.Series(0, index=temp.index)
        a_roll = temp.expanding().apply(lambda x: np.percentile(x, a), raw=True)
        b_roll = temp.expanding().apply(lambda x: np.percentile(x, b), raw=True)
        temp_roll[temp>a_roll] = 1
        temp_roll[temp<b_roll] = -1
    else:
        temp = data.loc[:,name].dropna()
        temp_roll = pd.Series(0, index=temp.index)
        a_roll = temp.expanding().apply(lambda x: np.percentile(x, a), raw=True)
        b_roll = temp.expanding().apply(lambda x: np.percentile(x, b), raw=True)
        if res.loc[name,'IC']>0 :
            temp_roll[temp>a_roll] = 1
            temp_roll[temp<b_roll] = -1
        else :
            temp_roll[temp>a_roll] = -1
            temp_roll[temp<b_roll] = 1
    x1 = temp_roll  # testing sgl
    x2 = mark_signal.iloc[:,0]  # actual sgl
    sumlen = sum(x1!=0)
    if sumlen == 0:
        count = np.nan
    else :
        count = (sum((x1==1)&(x2==1)) + sum((x1==-1)&(x2==-1)))  / sumlen
        

        
    return count,temp_roll

def ScaleWeight(scale):
    '''factor weight'''
    
    scale = pd.DataFrame(scale)
    scale_index = scale.copy()
    scale_sum = pd.DataFrame(scale_index.sum(axis=0))
    for i in scale.index:
        for j in scale.columns:
            scale_index.loc[i,j] = scale_index.loc[i,j]/scale_sum.loc[j,0]
            
    return scale_index


def FactorSum(factor,res,mark_price,weight = 'ratioweight'):
    '''
    counting factor intensity 
    '''
    category = factor.copy()
    for fac in category.columns:
        print(fac)
        temp = category.loc[:,fac]
        a = res.loc[fac,'a']
        b = res.loc[fac,'b']
        a_roll = temp.expanding().apply(lambda x: np.percentile(x, a), raw=True)
        b_roll = temp.expanding().apply(lambda x: np.percentile(x, b), raw=True)

        if res.loc[fac,'IC']>0:
            temp_roll = temp.where((temp>a_roll) | (temp<b_roll) ,0)
        else :
            temp_roll = -temp.where((temp>a_roll) | (temp<b_roll),0)
        category.loc[:,fac] = temp_roll
    category_sgl = category.applymap(lambda x:Compare(0,0,x))  
    mark_signal = mark_price.iloc[:,0].apply(lambda x:Compare(0,0,x)) 
    
    # scaling factors according to winratio
    res = res.loc[res.index.isin(category.columns),:]
    ratio_temp = ScaleWeight(res['ab_winratio']) # singel factor weight
    
    if weight == 'ratioweight':
        for i in category.columns:
            category.loc[:,i] = category.loc[:,i]*ratio_temp.loc[i,'ab_winratio']
    else : pass
    sum_temp = category.sum(axis=1)
    return category,category_sgl,sum_temp,mark_signal,ratio_temp


#%%
def ClassRenew(mark_price, factor, ratio, res, classname, start_date, weight='ratioweight',res_roll=None,roll=False):
    
    '''Each factor is synthesized into a major factor category based on the odd ratio as the weight.'''
    winratiostb = pd.DataFrame()
    categorystb = factor.copy()
    
    categorystb,mark_pricestb = DateSame(categorystb, mark_price)
    category_rankstb,category_sglstb,sum_tempstb,mark_signalstb,ratio_temp = FactorSum(categorystb,res,mark_pricestb)
    
    winratiostb.loc[classname,'a'],winratiostb.loc[classname,'b'] = ratio['a'][0],ratio['b'][0]
    winratiostb.loc[classname,'ab_winratio'],signal_tempstb = Winning_Ratio(sum_tempstb,ratio['a'][0],ratio['b'][0],mark_price,mark_signalstb,res,name=None)
    
    signal_tempstb = signal_tempstb[start_date:]
    
    return signal_tempstb


