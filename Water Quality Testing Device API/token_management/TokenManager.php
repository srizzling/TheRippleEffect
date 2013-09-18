<?php

/* Requires the token helpers */
require_once("/home/a9969020/public_html/token_management/TokenGenerator.php");
require_once("/home/a9969020/public_html/token_management/TokenFetcher.php");
require_once("/home/a9969020/public_html/token_management/TokenChecker.php");

/* Depends on the response generator for outputting back to the application */
require_once("/home/a9969020/public_html/response_generator/ResponseGenerator.php");

/**
 * Class that will check the status of the client, fetching their token or generating
 * a new one if required. All token management should be done through this class alone, other
 * classes are to be considered helpers to this
 *
 * @author ThreeZeroZero
 *
*/
class TokenManager {

	/**
	 * This has no external instantiation, methods are called statically such as:
	 *
	 * 			-	TokenGenerator::getTokenForAuthenticatedUser();
	 */
	private function __construct(){
	}

	/**
	 * Fetches a token for the user. Resetting it if it is about to expire. Will
	 * generate a new token for the client if none exist
	 *
	 * If a parameter is left null the other parameter MUST BE SET
	 *
	 * @param $userID 			The user ID to generate a token for
	 * @param $current_token	The current token
	 * @return 					The token that was generated
	 */
	public static function getTokenForAuthenticatedUser($userID, $current_token){

		/* Do not attempt if the user has not satisfied the precondition */
		if($userID == null && $current_token == null){
			return "";
		}

		/* Attempt to match for an existing token */
		$check_existing_token = TokenFetcher::getToken($userID, $current_token);

		/* There is an existing token that matches for this instance */
		if($check_existing_token !== false){
			return $check_existing_token;
		}

		/* No token exists, this will generate a new one */
		else{
			return TokenGenerator::generateToken($userID);
		}
	}

	/**
	 * Checks the authentication of a token, returning a boolean
	 *
	 * @param $token The token to check the validity of
	 * @return 		 True if the token is valid
	 */
	public static function checkAuthenticationToken($token){

		/* If the process fails, inform the user and end */
		if(!TokenChecker::checkToken($token)){
				ResponseGenerator::generateFailure(
				"Unfortunately your session has expired, please login again to continue",
				array("error" => array("token" => array("status" => "invalid", debug => "Token returned invalid, log user out and require re-authentication"))),
				$token,
				$errorCode = "403"
				);
				exit();
		}
	}

	/**
	 * Reauthenticates this user and provides a new session token
	 *
	 * @param $token The token to check the validity of
	 */
	public static function reauthenticateUserWithToken($token){

		/* Check the validity of this token */
		TokenManager::checkAuthenticationToken($token);

		/* Token is good - retrieve the user info */
		$user_id = UserDetails::getUserID($token);

		/* Remove the old token */
		TokenChecker::removeToken($token);

		/* Generate a new token */
		return TokenManager::getTokenForAuthenticatedUser($user_id, null);
	}

	/**
	 * Retrieve the token from the headers payload
	 *
	 * @param $token The array of headers for the request
	 * @return 		 Token string
	 */
	public static function parseTokenFromHeaders($headers){
		return $headers["Authorization"];
	}
}

?>