# -*- coding=utf-8 -*-
# 导入需要的包
import os
import time
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from numpy.random import randn
from datetime import datetime
import xlrd
import xlwt
import tkinter as tk
from tkinter import filedialog

root = tk.Tk()
root.withdraw()

file_path = filedialog.askopenfilename(filetypes =[('csv files', '.csv')])
print(file_path)
mytime=time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))
path=file_path.replace('.csv', mytime+'.xls')
f= open(file_path)
xlsx_file = pd.read_csv(f)
df=pd.DataFrame(xlsx_file)
print(df.shape)
print(df.info())


workbook = xlwt.Workbook(encoding = 'ascii')
worksheet = workbook.add_sheet('结果')
worksheet.write(0, 0, label = 'Row 0, Column 0 Value')
workbook.save(path )
