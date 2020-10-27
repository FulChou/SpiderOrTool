import requests
from bs4 import BeautifulSoup
import re 
import json
import os

username = ''
password = ''

userAgent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/537.36\
            (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36'

session = requests.session() 
# 获取登录的 token：
def get_login_id():
    url = 'http://ca.its.csu.edu.cn/Home/Login/69'
    post_data = {
    'userName': username,
    'passWord': password,
    'enter': 'true'
    }
    headers = {
        "Referer": "http://ca.its.csu.edu.cn/Home/Login/69",
        'User-Agent': userAgent,
    }
    req = requests.post(url,post_data,headers)
    html = req.text
    bf = BeautifulSoup(html,'lxml')
    tokenId_input_list = bf.find_all('input',attrs={'name':'tokenId'})
    tokenId = tokenId_input_list[0].get('value')
    return tokenId

##登录到用户的界面：
def login(tokenId) ->str:
    p_data = {
    "tokenId": tokenId,
    "account": username, # 学号
    "Thirdsys": "xsgzx"
    }
    headers = {
        'Referer': 'http://ca.its.csu.edu.cn/',
        'User-Agent': userAgent
    }
    req = session.post('http://202.197.71.125/loginsso.jsp',p_data,headers) 


def get_stu_information():
    if os.path.exists('stu_data.json'): # exists information
        with open('stu_data.json','r') as fl:
            data_list = json.loads(fl.read())
        return data_list
    req = session.get('http://202.197.71.125/a/physicalhealth/gxxl07/gXXL0704/form?type=add')
    ## get data of student
    bstext = BeautifulSoup(req.text,'lxml')
    taglist = bstext.find_all('td',id=True)
    data_list = []
    params_data = {
    'gxxl0703Id': '',
    'gxxl0705Id': '',
    'type': 'edit'
    }
    for td in taglist: 
        td_name = td.find_next_sibling('td')
        td_address = td_name.find_next_sibling('td')
        stu_name = td_name.string
        stu_address = td_address.string
        stu_id = td.string
        # 找link id：
        tds = td.find_parent('tr').find('a')
        id_string = tds.get('onclick') 
        url_id_list = re.findall(r"'\w{32}'|''",id_string) 
        data = {    
        'xsid': '',
        'xh': '',
        'xm': 'stu_name',
        'qs': 'stu_address',
        'lxfs': '13690098765',
        'xyqk': 'A',
        'qgzk': 'A',
        'rjgx': 'A',
        'shqk': 'A',
        'xldj': '1级',
        'zjywtfsj': '无',
        'tj': '1' ,
        'gxxl0703Id':'', 
        'gxxl0705Id':''
        }
        data['xsid'] = stu_id
        data['xh'] = stu_id
        data['xm'] = stu_name
        data['qs'] = stu_address
        data['gxxl0703Id'] = url_id_list[0].strip("'")  
        data['gxxl0705Id'] = url_id_list[1].strip("'")       
        params_data['gxxl0703Id'] = data['gxxl0703Id']
        params_data['gxxl0705Id'] = data['gxxl0705Id']
        phone_num = get_phone_num(params_data)
        data['lxfs'] = phone_num
        data_list.append(data)
    json_data = json.dumps(data_list)
    with open('stu_data.json','w') as fl:
        fl.write(json_data)
    print('success for data')
    return data_list

def get_phone_num(params_data):
    sub_req = session.get('http://202.197.71.125/a/physicalhealth/gxxl07/gXXL0705/toAddDetail?\
    gxxl0703Id='+params_data['gxxl0703Id']+'&\
    gxxl0705Id='+params_data['gxxl0705Id']+'&\
    type=edit',params=params_data)
    bf = BeautifulSoup(sub_req.text,'lxml')
    phone_num = bf.find('input',attrs={'name':'lxfs'}).get('value')
    return phone_num

def upload_data(data_list=None,flag=True):
    if flag:
        for data in data_list:
            req = session.post('http://202.197.71.125/a/physicalhealth/gxxl07/gXXL0704/saveMain',
            data=data) 
            print(req.status_code)
        print("Well-done")


if __name__ == "__main__":
    tokenId = get_login_id()
    login(tokenId)
    data_list = get_stu_information()
    upload_data(data_list)