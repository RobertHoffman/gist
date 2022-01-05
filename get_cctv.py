import jqdatasdk as jq
import pandas as pd
import time
import os
jq.auth('18500685406', 'W44vzfM!EQUWio5PmBaz')

start_date, end_date = '2009-06-26', '2021-11-22'

a = jq.finance.run_query(jq.query(jq.finance.CCTV_NEWS).filter(jq.finance.CCTV_NEWS.day == '2019-02-19'))

# 读取已有数据
if not os.path.exists(r'E:\桌面\cctv文本.xlsx'):
    exist_data = pd.DataFrame()
    exist_days = []
else:
    exist_data = pd.read_excel(r'E:\桌面\cctv文本.xlsx', index_col=0, engine='openpyxl', parse_dates=False)
    exist_days = [i.strftime('%Y-%m-%d') for i in exist_data['day'].tolist()]

# 对时间段进行划分，分批下载数据
dates = pd.date_range(start_date, end_date, freq='D').strftime('%Y-%m-%d').to_list()
dates = list(set(dates) - set(exist_days))
dates.sort()

# 分批下载数据
data_collection = [exist_data]
for date in dates:
    if date in exist_days:
        continue
    else:
        pass

    data_tmp = jq.finance.run_query(jq.query(jq.finance.CCTV_NEWS).filter(jq.finance.CCTV_NEWS.day == date))
    time.sleep(0.3)

    if data_tmp.empty:
        print(f'取不到数据：{date}')
    else:
        print(f'收集数据截至：{date}')
        data_collection.append(data_tmp)

output_data = pd.concat(data_collection, axis=0)
output_data.to_excel(r'E:\桌面\cctv文本.xlsx')
