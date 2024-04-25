# -*- coding: utf-8 -*-

from code.data_loader import *
from code.data_processor import *
from code.model_builder import *
from code.backtest import *
from code.data_index import *

import pandas as pd
import numpy as np
import os

import warnings
warnings.simplefilter('ignore')
plt.style.use('seaborn')

class_list = ['supply','demand','inventory','price_diff']
def Data_load(path,filename,class_list):
    dfs = {}

    for classname in class_list:
        daily, weekly, monthly = pd.DataFrame(),pd.DataFrame(),pd.DataFrame()
        for sheet_name in xls.sheet_names:
            num =1
            if classname in sheet_name:
                sheetname = sheet_name
                classname = classname+str(num)
                print(classname)
                daily_tp, weekly_tp, monthly_tp = Load_Data(path,filename,classname,sheetname = sheetname)    
                daily = pd.concat([daily,daily_tp],axis=1)
                weekly = pd.concat([weekly,weekly_tp],axis=1)
                monthly = pd.concat([monthly,monthly_tp],axis=1)
                num = num+1
                data = pd.concat([daily, weekly, monthly],axis=1)
                data = data.fillna(method='ffill')
                data = data.drop(columns=data.columns[data.isna().any() | ~data.applymap(np.isreal).all()])
                dfs[classname] = data
    return dfs

def IC_test(dfs,subclass,price_return,year_start,year_end):
    ics = {}
    # training set
    dict_method = {'daily':[[2,256+1],[1,2]], # 256 trading days
                    'weekly':[[2,53],[1,2]]} # 52 weeks
    
    for i in class_list: 

        result_ = pd.DataFrame()
        # counting weight of factors
        for fac in dfs[subclass].columns: 
            for windows in range(dict_method['weekly'][0][0],dict_method['weekly'][0][1]): 
                print('windows=',windows)
                temp_fac = DataFre(dfs[subclass][fac],windows,method=1,year=year_start,fre='weekly') 
                if len(temp_fac) == 0:
                    pass
                else:
                    temp_train = pd.DataFrame(temp_fac.loc[temp_fac.index.year <= year_end]) 
                    temp_train, price_train = DateSame(temp_train,price_return)
                    ic = Get_IC_Result(price_train, temp_train, part=fac, adf='True') 
                    winratio_ab = Odd_Winratio(factor=temp_train,mark_price_change=price_train,res=ic)
                    ic.loc[fac,'windows'] = windows
                    result = pd.concat([ic,winratio_ab],axis=1)
                    ics[i] = pd.concat([ics[i],result],axis=0)
    return ics

        
def Factor_Select(class_list,ics,dfs,year_start,year_end):
    fac ={}
    for i in class_list:
        print(i)
        data_train = pd.DataFrame()
        data_test = pd.DataFrame()
        for fac in ics[i]['IC'].index:
            print(fac)
            windows = int(ics[i]['IC'].loc[fac,'windows'])
            if (fac in dfs[i].columns):
                if all(dfs[i][fac])==0 :
                    pass
                else:
                    temp_fac = pd.DataFrame(DataFre(dfs[i][fac],windows,method=1,year=year_start,k=None,fre='weekly'))
                    temp_train = pd.DataFrame(temp_fac.loc[temp_fac.index.year <= year_end])
                    data_train = pd.concat([data_train,temp_train],axis=1).dropna()
                    temp_test = pd.DataFrame(temp_fac.loc[temp_fac.index.year > year_end]) 
                    data_test = pd.concat([data_test,temp_test],axis=1).dropna()
                
        # processing data
        data_train = DataProcessing(data_train,i)
        data_train = Outlier_Seperate(data_train) 
        data_test = DataProcessing(data_test,i)
        data_test = Outlier_Seperate(data_test)            
        fac[i] = pd.concat([data_train,data_test],join='inner').dropna()
        

def Trading_Sgl(dfs,price_return,ics,start_date):
    fac_sgl = pd.DataFrame() 
    for i in class_list:
        print(i)
        fac_test, price_test = DateSame(dfs[i],price_return)   
        start_date = pd.Timestamp(start_date)
        sub_sgl = ClassRenew(price_test, fac_test, ics[i]['weight'], ics[i]['IC'], classname=i,start_date=start_date, weight = 'ratioweight')       
        fac_sgl = pd.concat([fac_sgl,sub_sgl],axis=1)
    
    return fac_sgl
    


    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    

                
   



