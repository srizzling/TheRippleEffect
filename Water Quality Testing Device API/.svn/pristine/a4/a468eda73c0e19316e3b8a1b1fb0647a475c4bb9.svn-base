import os

# Helper class that will create a new, unique, access token for the client instance
#
# THIS IS STRICTLY A HELPER CLASS, DO NOT ATTEMPT TO ACCESS METHODS HERE - USE THE TOKENMANAGER.PHP
# CLASS INSTEAD
#
# @author Waterloop
class TokenGenerator:

	# Upper bounds for the number of times this can iterate for
	MAX_RECURSION_COUNT = 5

	#
	# Generates a unique token and adds it to the database
	#
	# @param userID 			The user ID to generate a token for
	# @param iterationCounter	Prevent this from recursing indefinitely (does not need to be set),
	# 							MAX_RECURSION_COUNT attempts
	#
	# @return 					The token that was generated
	@staticmethod
	def generateToken(userID, iterationCounter = 0):

		# Generate a random token of 32 bytes length
		token = os.urandom(32)

		# Open SQL object - handles errors
		mysqli = DBConnection::getMySQLConnection()

		# Escape the input values
		userID = intval(userID)
		token = mysqli->real_escape_string(token)

		# Generate a query
		query = "SELECT * FROM expired_tokens WHERE token = \"" . token . "\""
		result = mysqli->query(query)

		# Generate a query
		query = "INSERT INTO connected_clients (token, user_id) VALUES (\"" . token . "\", \"" . userID . "\")"

		# Obtain the result of this
		if mysqli->query(query) === true:

			# End connection
			mysqli->close()

			# Return token
			return token

		# Recurse, token exists in currently connected clients
		else:

			# End connection
			mysqli->close()

			# Do again
			if iterationCounter < MAX_RECURSION_COUNT:
				return TokenGenerator::generateToken(userID, iterationCounter++)

			# Throw an exception
			else:
				throw new Exception("Maximum token generator recursion reached")