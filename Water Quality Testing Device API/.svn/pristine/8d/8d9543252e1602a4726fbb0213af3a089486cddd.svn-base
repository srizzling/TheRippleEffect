#
# Helper class that will fetch check the validity of an access token
#
# THIS IS STRICTLY A HELPER CLASS, DO NOT ATTEMPT TO ACCESS METHODS HERE - USE THE TOKENMANAGER.PY
# CLASS INSTEAD
#
# @author Waterloop
class TokenChecker:

	#
	# Checks the authentication of a token, returning a boolean
	#
	# @param token 	The token to check the validity of
	# @return 		True if the token is valid
	#
	@staticmethod
	def checkToken(token):

		# Open SQL object - handles errors
		mysql = DBConnection::getMySQLConnection()

		# Escape the input values
		token = mysqli->real_escape_string(token)

		# Generate a query
		query = "SELECT * FROM connected_clients WHERE token = \"" + token + "\""
		result = mysqli->query(query)
		
		# Kill the connection 
		mysqli->close()

		# Determine the result
		return result -> num_rows >= 1