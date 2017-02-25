import sys
import getopt
def usage():
	print "-h for help" 
	print "-D:database #use a database"
	print "-T:table    #use a table"
	print "-C:column   #use a column"
	print "--db        #show current db"
	print "--dbs       #show all of dbs"
	print "--table     #show all of table"
	print "--column    #show all of column"
	print "--dump      #show data"
def get_cmd(argv):
	try:
		opts,args = getopt.getopt(argv[1:],"hD:T:C:",["db","dbs","table","column","dump"])
	except getopt.GetoptError,err:
		print "can't understand your opt"
		usage()
		sys.exit(0)
	for o,a in opts:
		if o in ("-h","--help"):
			usage()
if __name__ == '__main__':
	get_cmd(sys.argv)