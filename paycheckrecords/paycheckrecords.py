from getpass import getpass
import threading
import mechanize
from bs4 import BeautifulSoup
from paystub import paystub
from datetime import datetime
from datetime import timedelta


class paycheckrecords:
	_br = mechanize.Browser()
	_browserSem = threading.Semaphore()
	_thread = None
	_stop = False
	_timer = None
	_threadSleep = threading.Event()
	
	def __init__(self, username, password):
		self._br.set_handle_robots(False)
		self._br.open("https://www.paycheckrecords.com")
		self._br.select_form(name="Login_Form")
		
		self._br.form["userStrId"] = username
		self._br.form["password"] = password
		
		self._br.submit()
		
		self._thread = threading.Thread(target=self.preventTimeOut)
		self._thread.start()
		
	def preventTimeOut(self):
		while not self._stop:
			self._browserSem.acquire()
#			print "aquired lock"
			url = self._br.geturl()
			#print "url = ", url
			self._br.open(url)
#			print "refreshed"
			self._browserSem.release()
#			print "reload page from thread"
			self._threadSleep.wait(30)
#			print "awake"
			self._threadSleep.clear()
	

	
	def getLatestPayStub(self):
		self._browserSem.acquire()
		originalurl = self._br.geturl()
		paystubResponse = self._br.open("https://www.paycheckrecords.com/in/paychecks.jsp")
		
		ret = self._getPaystubsFromTable(paystubResponse.read(), range(1, 2))
		
		self._br.open(originalurl)
		self._browserSem.release()
		return ret[0]
	
	def getPayStubsInRange(self, startDate, endDate, sequence = 0):
		self._browserSem.acquire()
		originalurl = self._br.geturl()
		paystubResponse = self._br.open("https://www.paycheckrecords.com/in/paychecks.jsp")
		self._br.select_form(name="dateSelect")
		self._br.form["startDate"] = startDate.strftime("%m/%d/%Y")
		self._br.form["endDate"] = endDate.strftime("%m/%d/%Y")		
		paystubResponse = self._br.submit()
		ret = self._getPaystubsFromTable(paystubResponse.read(),sequence)
		
		self._br.open(originalurl)
		self._browserSem.release()
		return ret
	
		
	
	def _getPaystubsFromTable(self, html, sequence, GetHtml = True):
		soup = BeautifulSoup(html)
		PayStubTable = soup.find("table", { "class" : "report" })
		payrows = PayStubTable.findAll('tr')
		headerCols = payrows[0].findAll('td')
		ret = []
		i = 0
		DateIndex = -1
		NetIndex = -1
		TotalIndex = -1
		
		for col in headerCols:
			colName = col.string
			if colName == u'Pay Date' and DateIndex == -1:
				DateIndex = i
			elif colName == u'Total Pay' and TotalIndex == -1:
				TotalIndex = i
			elif colName == u'Net Pay' and NetIndex == -1:
				NetIndex = i
			i = i + 1
		if sequence == 0:
			sequence = range(1, len(payrows))
		for index in sequence:
			paystubHtml = None
			rowCols = payrows[index].findAll('td')
			rowDate = rowCols[DateIndex].a.string.strip()
			rowTotalPay = float(rowCols[TotalIndex].string.strip().strip("$"))
			rowNetPay = float(rowCols[NetIndex].string.strip().strip("$"))
			tmpDateTime = datetime.strptime(rowDate, '%m/%d/%Y')
			if GetHtml:
				paystubResponse = self._br.open(rowCols[DateIndex].a['href'])
				paystubHtml = paystubResponse.read()
				self._br.back()
			tmpPayStub = paystub(tmpDateTime, rowTotalPay, rowNetPay, paystubHtml)
			ret.append(tmpPayStub)
		
		return ret

		
	
	def close(self):
		#print "Closing Instance"
		self._stop = True
		#print "_stop set"
		self._threadSleep.set()
		#print "_threadSleep set"
		self._thread.join()
		#print "thread joined"
		self._br.close()
		#print "Closing Done"