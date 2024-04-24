# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
import os
import re


def Time_Process(temp_data,j=None):
    '''extract date'''
    time_pattern = r'(\d{4}-\d{2}-\d{2} 00:00:00)'    
    if j==None :j=0
    temp_list = pd.DataFrame(temp_data.iloc[:,j])
    index_str = temp_list.index.astype(str)
    time_str = index_str.str.extract(time_pattern,expand=False) 
    time_str = time_str.dropna()
    time_str = pd.to_datetime(time_str,errors='coerce') 
    mask = pd.isna(time_str)
    time_str = time_str[~mask]
    temp_list = temp_list.loc[time_str,:]
    temp_list.dropna(inplace=True)
    temp_list = temp_list[~temp_list.index.duplicated(keep='first')] 
    temp_list.sort_index(inplace=True)
    return temp_list



def Mark_Data(data):
    '''change columns'''
    if len(np.where(data.index=='指标名称')[0]) !=0:
        print('修改指标名称')
        data.columns = data.loc['指标名称',:]
    elif len(np.where(data.index=='日期')[0]) !=0:
        print('修改日期名称')
        data.columns = data.loc['日期',:]
    if len(np.where(data.index=='Date')[0]) !=0:
        print('修改Date名称')
        data.columns = data.loc['Date',:]
    data.dropna(how='all',inplace=True)
    return data


def Freq_Data(temp_data,data_daily,data_weekly,data_monthly):
    '''frequency conversion '''
    data_mark = temp_data.iloc[:3,:] 
    if len(np.where(data_mark.index=='频率')[0]) !=0:
        pos = np.where(data_mark.index=='频率')[0]
    elif len(np.where(data_mark.index=='频度')[0]) !=0:
        pos = np.where(data_mark.index=='频度')[0]
    else : pos = 0
    
    if pos > 0:
        for j in range(temp_data.shape[1]):
            if temp_data.iloc[pos[0],j] == '日':
                print('j=',j)
                temp_list = Time_Process(temp_data,j)
                data_daily = pd.concat([data_daily,temp_list],axis=1)
                
            elif temp_data.iloc[pos[0],j] == '周':
                print('j=',j)
                temp_list = Time_Process(temp_data,j)
                data_weekly = pd.concat([data_weekly,temp_list],axis=1)
                
            elif temp_data.iloc[pos[0],j] == '月':
                print('j=',j)
                temp_list = Time_Process(temp_data,j)
                data_monthly = pd.concat([data_monthly,temp_list],axis=1)
    elif pos == 0:
        for j in range(temp_data.shape[1]):
            print('j=',j)
            temp_list = Time_Process(temp_data,j)
            data_daily = pd.concat([data_daily,temp_list],axis=1)
    return data_daily,data_weekly,data_monthly


def Sort_Data(data,fre,classname):
    '''drop nan and duplicates'''
    data = data[~data.index.duplicated(keep='first')]
    data = data.sort_index().dropna(how='all')
    data.dropna(how='all',inplace=True)

    return data

def Data_Process(data,fre,classname):
    data = Sort_Data(data,fre=fre,classname=classname)
    data.sort_index(inplace=True)
    data.index = pd.to_datetime(data.index)
    data = data.loc[~data.index.duplicated()]
    data = data.loc[:,~data.columns.duplicated()]
    data.index = pd.to_datetime(data.index)
    return data

def Load_Data(path,filename,classname,sheetname,year):
    
    file_path = path +'/'+filename
    data = pd.read_excel(file_path, sheet_name=sheetname, index_col=0)
    if data.index.isna().all():
        data.index = data.iloc[:,0]
        data = data.iloc[:,1:]
    data_mark = data.iloc[:3,:]            
    position = []
    for i in range(data_mark.shape[0]):
        position.extend(np.where(data_mark.iloc[i,:]=='指标Id')[0].tolist())
        position.extend(np.where(data_mark.iloc[i,:]=='指标名称')[0].tolist())
        position.extend(np.where(data_mark.iloc[i,:]=='日期')[0].tolist())
    position = list(set(position))
    position.sort(reverse=False)  
    
    data_daily = pd.DataFrame()
    data_weekly = pd.DataFrame()
    data_monthly = pd.DataFrame()
    
    if len(position) == 0:
        data = Mark_Data(data)
        data_daily,data_weekly,data_monthly = Freq_Data(data,data_daily,data_weekly,data_monthly)
    else:
        num = 1
        for i in range(len(position)):
            print(i)
            if i == 0:
                globals()['data'+str(num)] = data.iloc[:,:position[i]]
                globals()['data'+str(num)] = Mark_Data(globals()['data'+str(num)])
                num += 1
            else:
                globals()['data'+str(num)] = data.iloc[:,position[i-1]:position[i]].dropna(axis=1,how='all')                
                globals()['data'+str(num)].index = globals()['data'+str(num)].iloc[:,0]
                globals()['data'+str(num)] = globals()['data'+str(num)].iloc[:,1:]
                globals()['data'+str(num)] = Mark_Data(globals()['data'+str(num)])
                num += 1
                
        for i in range(1,num):
            print('i=',i)
            position = []
            temp_data = globals()['data'+str(i)]
            data_daily,data_weekly,data_monthly = Freq_Data(temp_data,data_daily,data_weekly,data_monthly)

    
    data_daily = Data_Process(data_daily,'日',classname)
    data_weekly = Data_Process(data_weekly,'周',classname)
    data_monthly = Data_Process(data_monthly,'月',classname)

    
    return data_daily, data_weekly, data_monthly

























                    
                    
                    
            
        

        
