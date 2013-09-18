#
# Helper class that will fetch any existing token or will update an out of date one.
#
# THIS IS STRICTLY A HELPER CLASS, DO NOT ATTEMPT TO ACCESS METHODS HERE - USE THE TOKENMANAGER.PHP
# CLASS INSTEAD
#
# @author Waterloop
class TokenFetcher:

	#
	# Fetches a token for the user. Resetting it if it is about to expire.
	#
	# If a parameter is left null the other parameter MUST BE SET
	#
	# @param userID 		The user ID to generate a token for
	# @param current_token	The current token
	# @return 				The token that was generated
	#
	@staticmethod
	def getToken(userID, current_token):

		# If there is a passed token, try and match on it
		if current_token != None:
			return TokenFetcher.checkForExistingToken(current_token)

		# Check for any user ID matches
		else
			return TokenFetcher.checkForExistingID(userID)

	#
	# Helper fetches an existing token for the user by matching on the token exclusively.
	#
	# Will return false when a token does not exist in the DB
	#
	# @param current_token 	The current token
	# @return 				The token that was generated or false if there is no match
	@staticmethod
	def checkForExistingToken(current_token):

		# Open SQL object - handles errors
		mysqli = DBConnection::getMySQLConnection()

		# Escape the input values
		current_token = mysqli->real_escape_string(current_token)

		# Generate a query
		query = "SELECT * FROM connected_clients WHERE token = \"" + current_token + "\""
		result = mysqli->query(query)

		# Kill the connection
		mysqli->close()

		# This token no longer exists, it'll need to be regenerated for the client
		if result -> num_rows < 1:
			return False

		# Current token is good, return it
		else:
			return current_token

	#
	# Helper fetches an existing token for the user by matching on the ID exclusively.
	#
	# Will return false when a token does not exist in the DB
	#
	# @param userID 	The user ID to generate a token for
	# @return 		  	The token that was generated or false if there is no match
	@staticmethod
	def checkForExistingID(userID):

		# Open SQL object - handles errors #/
		mysqli = DBConnection::getMySQLConnection()

		# Escape the input values #/
		userID = intval(userID)

		# Generate a query #/
		query = "SELECT * FROM connected_clients WHERE user_id = \"" + userID + "\""
		result = mysqli->query(query)

		# Kill the connection #/
		mysqli->close()

		# This token no longer exists, it'll need to be regenerated for the client #/
		if result -> num_rows < 1:
			return False

		# Current token is good, return it #/
		else:

			# Poll the request as an array #/
			as_array = mysqli_fetch_array(result, MYSQLI_ASSOC)

			# Return the token #/
			return as_array["token"]