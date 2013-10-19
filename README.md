Intuit-PaycheckRecords-Python
=============================

This provides a small python api to Intuit's Paycheck Records site.

What Can It Do
==============
This api can currently only retrieve paystubs from the site.

Directories
===========
* examples/ -- contains examples that demo the api's abilities
	*paycheckProcess.py retrieves your pay stubs between a set period of the month, displays a summary of each paystub, saves 2 copies of the paystubs (original and one sensitive information blacked out) and sums the gross income
* paycheckrecords -- contains the actual api