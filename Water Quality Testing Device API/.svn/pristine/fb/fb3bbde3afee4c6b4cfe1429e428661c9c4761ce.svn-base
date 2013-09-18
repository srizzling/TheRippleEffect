import sys
from ResponseGenerator import ResponseGenerator

#
# A class that holds all of the database constants so that the entire project can be easily moved about
# different hosts and servers/DB locations
#
# @author Waterloop
class DBConnection:

	# Database details
	HOST_NAME = "mysql12.000webhost.com"
	USER_NAME = "a9969020_scb"
	PASSWORD = "qaz123"
	DATABASE = "a9969020_scb"

	# Opens an SQL instance or handles error if one is thrown. The caller must tidy the object up
	@staticmethod	
	def getMySQLConnection():

		# Open SQL object
		mysqli = new mysqli(
				DBConnection::hostname,
				DBConnection::username,
				DBConnection::password,
				DBConnection::database
		)

		# Check connection
		if (mysqli_connect_error()):
			ResponseGenerator::generateExceptionNotice(new Exception(
			"Error number: " . mysqli_connect_errno() .
			"\n\nError Description" . mysqli_connect_error(), null)
			)
			sys.exit()

		# Return the connection
		else
			return mysqli