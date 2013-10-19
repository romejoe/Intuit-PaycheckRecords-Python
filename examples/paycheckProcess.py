
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
from bs4 import BeautifulSoup
import re
from getpass import getpass

import sys
sys.path.append("../")
from paycheckrecords import *

def checkRowForAll(row):
	for col in row.findAll('td'):
		if "Federal Income Tax" in str(col):
			return True
		if "Social Security" in str(col):
			return True
		if "Medicare" in str(col):
			return True
		if "NY Income Tax" in str(col):
			return True
		if "Cell Phone" in str(col):
			return True
		if "Deductions" in str(col):
			return True
		if "Taxes" in str(col):
			return True
		
	return False
	
def blackOut(html):
	soup = BeautifulSoup(html)
	
	#blackout net pay
	tmp = soup.findAll('u')
	for tag in tmp:
		if "Net Pay" in str(tag.parent):
			tag["style"] = "background-color:black; -webkit-print-color-adjust: exact;"
	tableList = ["paystub_pay_tbl", "paystub_ee_taxes_tbl", "paystub_summary_tbl"]
	
	#black out all
	for curTable in tableList:
		tmpTable = soup.find("table", {"id": curTable})
		allrows = tmpTable.findAll('tr')
		for row in allrows:
			if checkRowForAll(row):
				for col in row.findAll('td'):
					if '.' in str(col):
						col["style"] = "background-color:black;  -webkit-print-color-adjust: exact;"
	
	
	
	#black out netthispay
	elem = soup.find(text=re.compile('.*Net This Check:.*'))
	elem = elem.findNext('td')
	elem["style"] = "background-color:black;  -webkit-print-color-adjust: exact;"
	
	#black out account
	elem = soup.find(text=re.compile('.*Acct#.*'))
	
	nelem = elem.findNext('td')
	nelem["style"] = "background-color:black;  -webkit-print-color-adjust: exact;"
	
	contents = elem.string
	contentsList = contents.split("#")
	newcontent = contentsList[0] + "#<span style = \"background-color:black;  -webkit-print-color-adjust: exact;\">"
	contentsList = contentsList[1].split(":")
	newcontent = newcontent + contentsList[0] + "</span>:" + contentsList[1]
	elem.replaceWith(newcontent)
	
	return str(soup.prettify(formatter=None))

def main():
	
	_day = int(input("Day:"))
	username = raw_input("Username:")
	password = getpass("Password:")
	
	paycheckinst = paycheckrecords(username, password)
	try:
		
		now = date.today()
		
		if now.day > _day:
			startdate = now.replace(day=_day+1)
			enddate = startdate + timedelta(days=32)
			enddate = enddate.replace(day = _day)

		else:

			
			enddate = now.replace(day=_day)
			tmpdate = now.replace(day=1) - timedelta(days=1)
			startdate = tmpdate.replace(day=_day+1)
			
			
		
		ret = paycheckinst.getPayStubsInRange(startdate, enddate)
		gross = 0.0
		for stub in ret:
			print "Date: ", stub.PayDate
			print "Total Pay: ", stub.TotalPay
			print "Net Pay: ", stub.NetPay
			print ""
			gross = gross + stub.TotalPay
			filename = "paystub " + stub.PayDate.strftime("%m-%d-%Y")
			out = open(filename + ".html", "w")
			out.write(stub.HTML)
			out.close()
			
			out = open(filename + "(blacked out).html", "w")
			out.write(blackOut(stub.HTML))
			out.close()
		print "Gross: " + str(gross)
	finally:
		paycheckinst.close()
	
main()
