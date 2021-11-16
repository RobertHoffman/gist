from WindPy import w
import pandas as pd
import os

start_date, end_date = '2019-01-01', '2021-11-12'
w.start()

"""consump_week = w.edb(
    "S9977720",
    start_date, end_date, usedf=True)[1]
consump_week.index = pd.DatetimeIndex(consump_week.index)
consump_week = consump_week.resample('W-Sun').last()  # 会选取每周最后一个值，如果没有就显示nan"""

# 读取指标库
inds = pd.read_excel(r'E:\桌面\建投工作文件\中观数据库\中观数据库指标库.xlsx', sheet_name='指标列表', engine='openpyxl')
inds_str = ','.join(inds['Wind编号'].tolist())

# 读取已有数据、日期
if not os.path.exists(r'E:\桌面\建投工作文件\中观数据库\中观数据库.csv'):
    exist_data = pd.DataFrame()
    exist_days = []
else:
    exist_data = pd.read_csv(r'E:\桌面\建投工作文件\中观数据库\中观数据库.csv', index_col=0)
    exist_days = exist_data.index

# 计算时间序列
time_starts = pd.date_range(start_date, end_date, freq='MS').strftime('%Y-%m-%d').to_list()
time_stops = pd.date_range(start_date, end_date, freq='M').strftime('%Y-%m-%d').to_list()
if len(time_starts) > len(time_stops):
    time_stops.append(end_date)

# 只获取未获取日期的数据，如果数据超限会进行提示
wdata_collection = [exist_data]
for i in range(len(time_starts)):
    if time_starts[i] in exist_days and time_stops[i] in exist_days:
        continue
    elif time_starts[i] in exist_days and time_stops[i] not in exist_days:
        time_starts[i] = exist_days[-1]
    else:
        pass

    wdata_tmp = w.edb(inds_str, time_starts[i], time_stops[i], usedf=True)

    if not wdata_tmp[0] == 0:
        print(wdata_tmp[1])
        break
    else:
        print(f'收集数据截至：{time_stops[i]}')
        wdata_collection.append(wdata_tmp[1])

# 整合获取数据
output_data = pd.concat(wdata_collection, axis=0)
output_data.index = list(map(lambda x: x.strftime('%Y-%m-%d') if type(x) != str else x, output_data.index))  # 将索引化作字符串
output_data = output_data.reset_index().drop_duplicates(
    subset='index', keep='last').set_index('index').sort_index()  # Wind会自动导入前一个值，因此有必要去重
output_data.to_csv(r'E:\桌面\建投工作文件\中观数据库\中观数据库.csv')

# 获取周频、月频指标列表
week_list = inds[inds['频率'] == '周']['Wind编号'].tolist()
month_list = inds[inds['频率'] == '月']['Wind编号'].tolist()
week_label, month_label = pd.DataFrame(), pd.DataFrame()

for i in week_list:
    week_label.loc['指标名', i] = inds[inds['Wind编号'] == i]['变量名称'].iloc[0]
    week_label.loc['类别', i] = inds[inds['Wind编号'] == i]['类别'].iloc[0]
for i in month_list:
    month_label.loc['指标名', i] = inds[inds['Wind编号'] == i]['变量名称'].iloc[0]
    month_label.loc['类别', i] = inds[inds['Wind编号'] == i]['类别'].iloc[0]

# 降采样
week_data = pd.concat([week_label, output_data[week_list].resample('W-Sun').last()], axis=0)
month_data = pd.concat([month_label, output_data[month_list].resample('M').last()], axis=0)

# 输出数据
with pd.ExcelWriter(r'E:\桌面\建投工作文件\中观数据库\中观数据分析报表.xlsx', datetime_format='YYYY-MM-DD') as writer:
    week_data.to_excel(writer, sheet_name='周频底稿', engine='openpyxl')
    month_data.to_excel(writer, sheet_name='月频底稿', engine='openpyxl')