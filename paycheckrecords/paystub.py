import datetime
class paystub:
	def __init__(self, payDate, TotalPay, NetPay, html = None):
		if type(payDate) is not datetime and type(payDate) is not datetime.datetime:
			raise ValueError("payDate is not a datetime object")
		
		if type(TotalPay) is not float:
			raise ValueError("TotalPay needs to be a float")
		if type(NetPay) is not float:
			raise ValueError("NetPay needs to be a float")
		
		self.PayDate = payDate
		self.TotalPay = TotalPay
		self.NetPay = NetPay
		self.HTML = html
