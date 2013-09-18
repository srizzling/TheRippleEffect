import sys
from ResponseGenerator import ResponseGenerator

#
# Class that will check the status of the client, fetching their token or generating
# a new one if required. All token management should be done through this class alone, other
# classes are to be considered helpers to this
#
# @author Waterloop
class TokenManager:

	#
	# Fetches a token for the user. Resetting it if it is about to expire. Will
	# generate a new token for the client if none exist
	#
	# If a parameter is left null the other parameter MUST BE SET
	#
	# @param userID 			The user ID to generate a token for
	# @param current_token	The current token
	# @return 					The token that was generated
	@staticmethod
	def getTokenForAuthenticatedUser(userID, current_token):

		# Do not attempt if the user has not satisfied the precondition
		if(userID == None and current_token == None):
			return ""

		# Attempt to match for an existing token
		check_existing_token = TokenFetcher.getToken(userID, current_token)

		# There is an existing token that matches for this instance
		if(check_existing_token != False):
			return check_existing_token

		# No token exists, this will generate a new one
		else:
			return TokenGenerator::generateToken(userID)
		
	#
	# Checks the authentication of a token, returning a boolean
	#
	# @param token The token to check the validity of
	# @return 		 True if the token is valid
	@staticmethod
	def checkAuthenticationToken(token):

		# If the process fails, inform the user and end
		if(!TokenChecker.checkToken(token)){
				ResponseGenerator.generateFailure(
				"Unfortunately your session has expired, please login again to continue",
				{"error": {"token": {"status": "invalid_token_error", "debug": "Token \"" + token + "\" returned invalid, log user out and require re-authentication"))),
				token
				)
				sys.exit()