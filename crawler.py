from bs4 import BeautifulSoup
import pandas as pd
import requests
import time
import argparse

session = requests.Session()
session.trust_env = False  # 让爬虫不走代理

parser = argparse.ArgumentParser(description='设置关键词')
parser.add_argument('--key', type=str)
args = parser.parse_args()

params = dict(
    headId='a34970ca076be9ade253b63e65919eae',
    ckId='a34970ca076be9ade253b63e65919eae',
    key=args.key,
)
header = dict(
    user_agent=r'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36',
)


def request_url(url, page):
    params['currentPage'] = page
    try:
        response = session.get(url, params=params, headers=header, timeout=3)
        if response.status_code == 200:
            return response.text
    except requests.RequestException:
        return None


def save_excel(soup):
    j_name, j_loc, j_salary, j_expr_lim, j_edu_lim, j_company, j_label = [], [], [], [], [], [], []
    job_list = soup.find(class_='left-list-box').find_all('li')
    if len(job_list) == 0:  # 如果没有数据，就停止爬取
        return 1

    for job in job_list:
        if job.find(class_='job-list-item') is not None:
            j_name.append(job.find(class_='job-title-box').contents[1].text)
            j_loc.append(job.find(class_='job-dq-box').contents[3].string)
            j_salary.append(job.find(class_='job-salary').string)
            j_expr_lim.append(job.find(class_='job-labels-box').contents[5].string)
            j_edu_lim.append(job.find(class_='job-labels-box').contents[9].string)
            j_company.append(job.find(class_='company-name ellipsis-1').string)
            tmp_label = [i.string for i in job.find(class_='company-tags-box ellipsis-1').find_all('span')]
            j_label.append(' '.join(tmp_label))

    j_data = pd.DataFrame([j_name, j_loc, j_salary, j_expr_lim, j_edu_lim, j_company, j_label],
                          index=['职位名称', '地点', '薪资', '经验要求', '学历要求', '公司名', '标签']).T
    return j_data


if __name__ == '__main__':
    datas = []
    for page in range(1, 10):  # 只能搜索前9页
        url = 'https://www.liepin.com/zhaopin/'
        html = request_url(url, page)
        soup = BeautifulSoup(html, 'lxml')
        data = save_excel(soup)

        if type(data) == int:
            print(f'关键词：{params["key"]}，爬取完成！')
            break
        else:
            datas.append(data)
            print(f'爬取页数：{page}')
            time.sleep(0.5)

    output_data = pd.concat(datas, axis=0)
    output_data.to_excel(rf'E:\桌面\建投工作文件\就业爬数据\高端职业数据 {args.key} {time.time()}.xlsx', sheet_name='猎聘网', engine='openpyxl')

# TODO 包含登录的情况和滑动验证框。
