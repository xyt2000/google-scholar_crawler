from urllib import parse
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
import time
import xlrd
import xlwt
import xlutils.copy
import random

"""
得到url
"""
def paperUrl(name):
    q = name
    params = {
        'q':q
    }
    params = parse.urlencode(params)
    url = ""+params
    return url

"""
获取Bib 
如果成功就返回bib
失败就返回该条目在表里的序号num
"""
def getBib(url,num):
    user_agents = [
        'User-Agent: Mozilla/5.0 (Windows; U; Windows NT 5.1; it; rv:1.8.1.11) Gecko/20071127 Firefox/2.0.0.11',
        'User-Agent: Opera/9.25 (Windows NT 5.1; U; en)',
        'User-Agent: Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; .NET CLR 1.1.4322; .NET CLR 2.0.50727)',
        'User-Agent: Mozilla/5.0 (compatible; Konqueror/3.5; Linux) KHTML/3.5.5 (like Gecko) (Kubuntu)',
        'User-Agent: Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.8.0.12) Gecko/20070731 Ubuntu/dapper-security Firefox/1.5.0.12',
        'User-Agent: Lynx/2.8.5rel.1 libwww-FM/2.14 SSL-MM/1.4.1 GNUTLS/1.2.9',
        "User-Agent: Mozilla/5.0 (X11; Linux i686) AppleWebKit/535.7 (KHTML, like Gecko) Ubuntu/11.04 Chromium/16.0.912.77 Chrome/16.0.912.77 Safari/535.7",
        "User-Agent: Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:10.0) Gecko/20100101 Firefox/10.0 ",
        'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:94.0) Gecko/20100101 Firefox/94.0'
    ]
    hr = ""
    bib = ""
    options = Options()
    options.add_argument('-headless')
    options.add_argument(user_agents[random.randint(0,8)])
    driver = webdriver.Firefox(options=options)
    driver.get(url)   
    for i in range(3):
        try:
            driver.find_element_by_class_name('gs_or_cit.gs_nph').click()
            time.sleep(3)
            s = driver.find_element_by_class_name('gs_citi')
            time.sleep(3)
            if s == '':
                s = driver.find_element_by_class_name('gs_citd')
            if s.text == 'BibTeX':
                hr = s.get_attribute('href')
            driver.get(hr)
            bib = driver.find_element_by_xpath("//*").text
            for i in range(5):
                try:
                    driver.quit()
                    break
                except:
                    time.sleep(0.1)
            break
        except:
            time.sleep(0.2)
    if bib=="":
        return num
    else:
        return bib

"""
将数据单条存入
"""
def saveOneData(savepath,data,num):
    print("save......")
    if num == 0:
        print("当前条数：", num)
        book=xlwt.Workbook(encoding='utf-8',style_compression=0)
        sheet=book.add_sheet('self-supervised',cell_overwrite_ok=False)
        col=('blb','name','year','title')
        for i in range(0,4):
          sheet.write(0,i,col[i])
        for j in range(0, len(data)):
            sheet.write(num + 1, j, data[j])
        book.save(savepath)
    else:
        rd = xlrd.open_workbook(savepath, formatting_info = True)
        wt = xlutils.copy.copy(rd)
        sheets = wt.get_sheet(0)
        print("当前条数：",num)
        for j in range(0, len(data)):
            sheets.write(num + 1, j, data[j])
        wt.save(savepath)

if __name__ == '__main__':
    savepath = ".\\savepath.xls"
    excel = xlrd.open_workbook(savepath) 
    sheet = excel.sheet_by_index(0)  
    rows: list = sheet.row_values(0) 
    index = rows.index('fileName') 
    listindes = sheet.col_values(index)  
    # 遍历该列所有的内容
    List = []
    errors = []
    #指定序数
    num = 0
    for i in range(1, len(listindes)):
        List.append(listindes[i])
    for q in List:
        url = paperUrl(q)
        bib = getBib(url,num)
        if type(bib)==int:
            print(url)
            print("error",bib)
            errors.append(bib)
        else:
            print(url)
            print(bib)
            bib = bib.splitlines(True)
            dic = {}
            for sub in bib[1:len(bib) - 1]:
                info = sub.split('=')
                dic[info[0]] = info[1]
            flag = 0
            data = ""
            def toString(string):
                newString = ""
                for s in string:
                    newString = newString + s
                return newString
            #这里简单分析bib的信息 提取title year jounal三个属性
            for keys, values in dic.items():
                if keys.strip() == "title":
                    data = data + toString(bib) + '%' + values.strip().strip(',').strip('{').strip('}')
            for keys, values in dic.items():
                if keys.strip() == "year":
                    data = data + '%' + values.strip().strip(',').strip('{').strip('}')
            for keys, values in dic.items():
                if flag == 1:
                    break
                elif keys.strip() == "journal":
                    data = data + '%' + values.strip().strip(',').strip('{').strip('}')
                    flag = 1
                elif keys.strip() == "booktitle":
                    data = data + '%' + values.strip().strip(',').strip('{').strip('}')           
                    flag = 1
                else:
                    flag = 0
            if flag == 0:
                data = data + '%' + 'null'
            print("data", data)
            data = data.split('%')
            path = ".\\result.xls"
            saveOneData(path, data, num)
        num = num + 1
    print(errors)
