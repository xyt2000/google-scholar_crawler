from bs4 import BeautifulSoup               #网页解析，获取数据
import re                                   #正则表达式
import urllib.request,urllib.error          #指定URL，获取数据
import xlwt                                 #进行Excel操作
from urllib.error import URLError
import xlrd
import xlutils.copy                        #excel表的写入
from time import  sleep
import random

"""
作用：请求网页 得到html
参数：网址
"""
def askURL(url):
    user_agents = [
        'Mozilla/5.0 (Windows; U; Windows NT 5.1; it; rv:1.8.1.11) Gecko/20071127 Firefox/2.0.0.11',
        'Opera/9.25 (Windows NT 5.1; U; en)',
        'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; .NET CLR 1.1.4322; .NET CLR 2.0.50727)',
        'Mozilla/5.0 (compatible; Konqueror/3.5; Linux) KHTML/3.5.5 (like Gecko) (Kubuntu)',
        'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.8.0.12) Gecko/20070731 Ubuntu/dapper-security Firefox/1.5.0.12',
        'Lynx/2.8.5rel.1 libwww-FM/2.14 SSL-MM/1.4.1 GNUTLS/1.2.9',
        "Mozilla/5.0 (X11; Linux i686) AppleWebKit/535.7 (KHTML, like Gecko) Ubuntu/11.04 Chromium/16.0.912.77 Chrome/16.0.912.77 Safari/535.7",
        "Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:10.0) Gecko/20100101 Firefox/10.0 ",
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:94.0) Gecko/20100101 Firefox/94.0'
    ]
    html = ""
    headers = {'user-agent':user_agents[random.randint(0,8)] }
    req = urllib.request.Request(url=url, headers=headers)
    for i in range(5):
        try:
            res = urllib.request.urlopen(req, timeout=7)
            html=res.read().decode('utf-8')
            break
        except URLError as e:
            if hasattr(e,"code"):
                print(e.code)
            if hasattr(e,"reason"):
                print(e.reason)
    return html
  
"""
  这是一些正则表达式的设置 可以和re.findall结合使用去查找和正则表达的相对应的结果
  可以根据自己要求去修改
"""
downLoadFileExist_reg=re.compile(r'<div class="gs_ggs gs_fl">')
downLoadFileLink_reg=re.compile(r'href="(.*?)">')
content_reg=re.compile(r'<div class="gs_ri">(.*?)<div class="gs_rs">')
fileLink_reg=re.compile(r'href="(.*?)" id="')
fileName_reg=re.compile(r'<a data-clk="hl=zh-CN&amp;sa=T&amp;ct=res&amp;.*?">(.*?)</a>')
periodicalTime_reg=re.compile(r'<div class="gs_a">.*?- (.*?)</div>')
quteNum_reg=re.compile(r'<div class="gs_fl">.*?hl=zh-CN">被引用次数：(.*?)</a>')


"""
作用：根据url去获取html并分析 调用了askURL方法。
参数：start_url和end_url构建url path指定存储地址  number:需要爬取的页数
注意63行的start_num指定起始爬的论文的序号（即上次爬虫中断的下一号 方便爬虫中断续爬）
注意64行的num 指定当前爬取的是第几个论文 方便根据该序号续写excel
"""
def getData(start_url,end_url,path，number):
    fileName_reg = re.compile(r'<a data-clk="hl=zh-CN&amp;sa=T&amp;ct=res&amp;.*?">(.*?)</a>')
    datalist=[]
    start_num=0
    num = 0
    for i in range(0,number):
        url=start_url+str(start_num)+end_url
        start_num = start_num + 20
        sleep(5)
        html=askURL(url)
        #逐一解析
        soup=BeautifulSoup(html,"html.parser")
        for item in soup.find_all('div',class_="gs_r gs_or gs_scl"):
            data=[]
            content_str = []
            item_str=str(item)
            #re通过正则表达式查找指定的字符串
            if re.findall(content_reg,item_str)!=[]:
                content_str=re.findall(content_reg,item_str)[0]
            if re.findall(fileName_reg,content_str) is None:
                print("none")
            if re.findall(fileName_reg,content_str)==[] or re.findall(fileName_reg,content_str)==None:
                fileName_reg = re.compile(r'<a data-clk="hl=zh-CN&amp;sa=T&amp;oi=ggp&amp;ct=res&amp.*?">(.*?)</a>')
            if re.findall(fileName_reg,content_str)!=[] or re.findall(fileName_reg,content_str)!=None:
                fileName = re.findall(fileName_reg, content_str)[0]
            print(re.findall(fileName_reg, content_str))
            fileName_reg = re.compile(r'<a data-clk="hl=zh-CN&amp;sa=T&amp;ct=res&amp;.*?">(.*?)</a>')
            fileName=re.sub('<b>','',fileName)
            fileName = re.sub('</b>', '', fileName)
            periodicalTime=re.findall(periodicalTime_reg,content_str)[0]
            periodicalTime = re.sub('<b>', '', periodicalTime)
            periodicalTime = re.sub('</b>', '', periodicalTime)
            periodicalTime = re.sub('\xa0', '', periodicalTime)
            m = 0
            time = ""
            flag = 0
            for char in periodicalTime:
                if flag == 1 and m < 5:
                        time = time + char
                        m = m + 1
                if char == ',':
                    flag = 1
            periodicalTime = time
            if re.findall(downLoadFileExist_reg,item_str)==[]:
                downLoadFilelink=''
            else:
                downLoadFilelink=re.findall(downLoadFileLink_reg,item_str)[0]          
            data.append(fileName)
            data.append(periodicalTime)
            data.append(downLoadFilelink)
            saveOneData(path,data,num)
            datalist.append(data)
            num = num + 1
    return datalist
  
#分条存储数据 
def saveOneData(savepath,data,num):
    print("save......")
    if num == 0:
        print("当前条数：", num)
        book=xlwt.Workbook(encoding='utf-8',style_compression=0)
        sheet=book.add_sheet('self-supervised',cell_overwrite_ok=False)
        col=('fileName','periodicalTime','downLoadFilelink')
        for i in range(0,len(data)):
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
"""
start_url 推荐使用国内镜像
end_url 根据自身要求改变参数
savepath 存储结果文件路径
"""     
def main():
    start_url="https://scholar.lanfanshu.cn/scholar?start="
    end_url="&q=test+case+prioritization&hl=zh-CN&as_sdt=0,5&as_vis=1&num=20"
    savepath=".\\1.xls"
    getData(start_url,end_url,savepath) 
    
if __name__=="__main__":
    main()
  
  
