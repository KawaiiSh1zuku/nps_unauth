import sys
import time
import hashlib
import requests
from urllib.parse import urlparse
from bs4 import BeautifulSoup

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
    "Accept": "*/*",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,ja;q=0.7",
    "Accept-Encoding": "gzip, deflate",
}

def getParam():
    now = time.time()
    m = hashlib.md5()
    m.update(str(int(now)).encode("utf8"))
    auth_key = m.hexdigest()
    return("?auth_key=%s&timestamp=%s" % (auth_key,int(now)))

def getInfo(baseurl, export):
    '''获取 NPS 服务器 Index/Index 页面的基本信息'''
    url = f"{baseurl}/Index/Index{getParam()}"
    response = requests.get(url, headers=headers)
    html = BeautifulSoup(response.text,'lxml')

    print("====基本信息====")

    language_tags = ["word-connectionport", "word-totalclients", "word-onlineclients", "word-tcpconnections"]
    i18n = {
        "word-connectionport": "连接端口",
        "word-totalclients": "客户端总数",
        "word-onlineclients": "在线客户端",
        "word-tcpconnections": "TCP连接数"
    }

    for tag in language_tags:
        title_element = html.find('h5', langtag=tag)
        if title_element:
            title = i18n[tag]
            value_element = title_element.find_parent().find_next_sibling().find('h1', class_='no-margins')
            value = value_element.text.strip()
            print(f"{title}：{value}")
    
def getClients(baseurl, export):
    '''获取 NPS 服务器所有客户端的基本信息'''
    url = f"{baseurl}/client/list{getParam()}"
    payload = {
        "search": "",
        "order": "asc",
        "offest": 0,
        "limit": 1000,
    }
    response = requests.post(url, headers=headers, data=payload)
    clients = response.json()["rows"]
    print("====客户端列表====")
    for client in clients:
        Id = client["Id"]
        Remark = client["Remark"]
        VerifyKey = client["VerifyKey"]
        Addr = client["Addr"]
        print(f"客户端ID: {Id}\n客户端备注: {Remark}\n客户端密钥: {VerifyKey}\n客户端IP: {Addr}\n")
    
    if export:
        url = urlparse(baseurl)
        f = open(f"{url.netloc.split(':')[0]}.txt", "a+")
        f.write(f"====ClientInfo====\n{clients}")
        f.close()
        
def getDomains(baseurl, export):
    '''获取 NPS 服务器所有域名的基本信息'''
    url = f"{baseurl}/index/hostlist{getParam()}"
    payload = {
        "search": "",
        "order": "asc",
        "offest": 0,
        "limit": 1000,
    }
    response = requests.post(url, headers=headers, data=payload)
    domains = response.json()["rows"]
    print("====域名解析列表====")
    for domain in domains:
        Id = domain["Id"]
        Host = domain["Host"]
        ClientId = domain["Client"]["Id"]
        Remark = domain["Remark"]
        print(f"域名ID: {Id}\n域名: {Host}\n域名备注: {Remark}\n绑定客户端: {ClientId}\n")
    
    if export:
        url = urlparse(baseurl)
        f = open(f"{url.netloc.split(':')[0]}.txt", "a+")
        f.write(f"====DomainInfo====\n{domains}")
        f.close()
        
def getTCP(baseurl, export):
    '''获取 NPS 服务器所有 TCP 转发的基本信息'''
    url = f"{baseurl}/index/gettunnel{getParam()}"
    payload = {
        "search": "",
        "type": "tcp",
        "offest": 0,
        "limit": 1000,
    }
    response = requests.post(url, headers=headers, data=payload)
    ports = response.json()["rows"]
    print("====TCP端口列表====")
    for port in ports:
        Id = port["Id"]
        Port = port["Port"]
        ServerIp = port["ServerIp"]
        Remark = port["Remark"]
        Target = port["Target"]["TargetStr"]
        ClientId = port["Client"]["Id"]
        print(f"端口ID: {Id}\n端口: {Port}\n端口备注: {Remark}\n绑定客户端: {ClientId}\n服务器IP: {ServerIp}\n目标: {Target}\n")
    
    if export:
        url = urlparse(baseurl)
        f = open(f"{url.netloc.split(':')[0]}.txt", "a+")
        f.write(f"====TcpPort====\n{ports}")
        f.close()
        
def getUDP(baseurl, export):
    '''获取 NPS 服务器所有 UDP 转发的基本信息'''
    url = f"{baseurl}/index/gettunnel{getParam()}"
    payload = {
        "search": "",
        "type": "udp",
        "offest": 0,
        "limit": 1000,
    }
    response = requests.post(url, headers=headers, data=payload)
    ports = response.json()["rows"]
    print("====UDP端口列表====")
    for port in ports:
        Id = port["Id"]
        Port = port["Port"]
        ServerIp = port["ServerIp"]
        Remark = port["Remark"]
        Target = port["Target"]["TargetStr"]
        ClientId = port["Client"]["Id"]
        print(f"端口ID: {Id}\n端口: {Port}\n端口备注: {Remark}\n绑定客户端: {ClientId}\n服务器IP: {ServerIp}\n目标: {Target}\n")
    
    if export:
        url = urlparse(baseurl)
        f = open(f"{url.netloc.split(':')[0]}.txt", "a+")
        f.write(f"====UdpPort====\n{ports}")
        f.close()

if __name__ == '__main__':
    baseurl = sys.argv[1]
    export = sys.argv[2]
    if export == 1:
        export = True
    else:
        export = False
    
    getInfo(baseurl, export)
    getClients(baseurl, export)
    getDomains(baseurl, export)
    getTCP(baseurl, export)
    getUDP(baseurl, export)