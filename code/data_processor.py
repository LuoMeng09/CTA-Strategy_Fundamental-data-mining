# -*- coding: utf-8 -*-
"""
Mapping of data with different frequencies.
Data filling and removal of extreme values.
Handling the lag order of the target and input factors.
IC (Information Coefficient) relationship test and ADF (Augmented Dickey-Fuller) test:
IC and ADF tests are conducted on the entire training set and on an annual basis.
The IC test is used to assess the correlation between two sequences.
In this experiment, IC is used to determine the direction and does not require standardization.
When IC values are used for weighting, they need to be standardized to ensure all data are on the same scale.
Standardization:
The mean and variance for standardization can be calculated using a rolling method.
Mechanism for inclusion: Calculate the rolling mean and standard deviation for all data. If the mean deviates by about two standard deviations, re-establish the standardization model."""

import pandas as pd
import numpy as np
import os
import re
import statsmodels.api as sm
from datetime import datetime
from sklearn.preprocessing import MinMaxScaler, StandardScaler
from code.data_loader import *


#%%
def Outlier_Seperate(factor):
    '''outlier processing'''
    factor.dropna(axis=1, how='all', inplace=True) 
    factor = factor.T.drop_duplicates(keep='first').T
    factor_temp = pd.DataFrame(index=factor.index)
    for name in factor.columns: 
        print(name)
        fac_temp = pd.DataFrame()
        fac_temp = factor[name].dropna()
        std_upper, std_lower = fac_temp.mean() + fac_temp.std()*3, fac_temp.mean() - fac_temp.std()*3
        fac_temp[fac_temp > std_upper] = std_upper
        fac_temp[fac_temp < std_lower] = std_lower 
        factor_temp = pd.concat([factor_temp,fac_temp],axis=1)
    factor = factor_temp
    factor = factor.replace(np.inf,np.nan)
    factor = factor.replace(-np.inf,np.nan)
    factor = factor.fillna(method='ffill')
    return factor


def Compare(a, b, x):
    '''signal:1_long;-1_short;0_close position'''
    if x > a:
        x = 1
    elif x < b:
        x = -1
    else:
        x = 0
    return x



def DataFre(data_input,windows,method,year,k=None,fre='daily'):
    '''
    Data Transformation:

    Daily and weekly frequency conversion
    Window period data processing
    '''
    data = data_input.copy()
    data.sort_index(inplace=True)
    data = data[~data.index.duplicated(keep='first')] # del duplicates
    if fre == 'weekly': # weekly sample
        data = data.resample('W-Fri').mean()
    data = data.fillna(method = 'ffill') 
    
    # frequency conversion
    if method == 1: 
        deltadata = data.rolling(window=windows).apply(lambda x: x[1] - x[0]).dropna() 
    elif method == 2: 
        dataroll = data.rolling(window=windows).mean().dropna()
        deltadata = data - dataroll
    elif method == 3: # MA-MA(k_lag)
        dataroll = data.rolling(window=windows).mean().dropna()
        deltadata = dataroll - dataroll.shift(-k)
        
    deltadata = deltadata.replace(np.inf,np.nan) 
    deltadata = deltadata.replace(-np.inf,np.nan)
       
    deltadata = deltadata.replace(0,np.nan)  
    deltadata = deltadata.fillna(method = 'ffill') 
    deltadata.dropna(inplace=True)
    
    if deltadata.index.year[0] > year: 
        deltadata = []
    else:
        deltadata = Outlier(deltadata)
    return deltadata


def StandardSeperate(factor,classname):
    '''Standardize'''    
    factor = factor.T.drop_duplicates(keep='first').T
    factor_temp = pd.DataFrame( index = factor.index )
    num = 0
    for name in factor.columns:       
        fac_temp = pd.DataFrame(factor[name].dropna())
        index_f, columns_f = fac_temp.index , name
        standard_scale = StandardScaler().fit(fac_temp) 
        num = num+1
        fac_temp = pd.DataFrame(standard_scale.transform(fac_temp), index = index_f, columns = [columns_f])
        factor_temp = pd.concat([factor_temp,fac_temp],axis=1)
    factor = factor_temp
    factor = factor.replace(0, np.nan).dropna(axis=1, how='all')
    return factor

def DataProcessing(factor,model_name):
    index_f, columns_f = factor.index, factor.columns
    standard_scale = StandardScaler().fit(factor) 
    factor = pd.DataFrame(standard_scale.transform(factor), index=index_f, columns=columns_f)
    factor = factor.replace(0, np.nan).dropna(axis=1, how='all')
    return factor

def DateSame(factor1,factor2):
    f1 = factor1.copy()
    f2 = factor2.copy()
    f1 = factor1.loc[factor1.index.isin(factor2.index),:]
    f2 = factor2.loc[factor2.index.isin(factor1.index),:]
    return f1,f2

def Get_IC_Result(y, factor_dict, part, rankic=None, adf=None, save=None):
    '''IC test :
    params :
        y：price_return
        factor_dict: testing data
    '''
    reg_result = pd.DataFrame()
    y, factor_dict = DateSame(y, factor_dict)
    year = y.dropna().index[0]
    
    for factor_sheet in factor_dict:
        y_temp = y.copy()
        factor_data = factor_dict[factor_sheet]
        factor_data = pd.DataFrame(factor_data)
        factor_data.dropna(inplace=True)
        y_temp, factor_data = DateSame(y_temp, factor_data)
        factor_data, y_temp = DateSame(factor_data, y_temp)

        for factor in factor_data.columns:
            begin = max(year, factor_data[factor].dropna().index[0])
            end = factor_data[factor].dropna().index[-1]

            reg_data = pd.concat([y_temp, factor_data[factor]], axis=1).loc[begin: end].fillna(method='ffill')
            reg_data = reg_data.dropna()

            reg_result.loc[factor, 'begin_date'] = begin
            reg_result.loc[factor, 'end_date'] = end
            m1 = sm.OLS(reg_data.iloc[:, 0], sm.add_constant(reg_data.iloc[:, 1]), missing='drop').fit()
            reg_result.loc[factor, 'IC'] = reg_data.corr().iloc[0,1]
           
            reg_result.loc[factor, 'adjR2'] = m1.rsquared_adj       
            if rankic =='True':
                reg_result.loc[factor, 'RankIC'] = reg_data.corr(method='spearman').iloc[0, 1]
            if adf =='True':
                reg_result.loc[factor, 'ADF_pvalue'] = sm.tsa.stattools.adfuller(factor_data[factor])[1]
            print( year, begin, end, factor_sheet, factor)
    if save == 'True':
        reg_result.to_excel('IC_test_%s.xlsx'%part) 
    else: pass
    return reg_result





































