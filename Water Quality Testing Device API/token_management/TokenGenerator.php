<?php

/* Depends on the DBConnection for opening connections to the database */
require_once("/home/a9969020/public_html/database_connection/DBConnection.php");

/**
 * Helper class that will create a new, unique, access token for the client instance
 *
 * THIS IS STRICTLY A HELPER CLASS, DO NOT ATTEMPT TO ACCESS METHODS HERE - USE THE TOKENMANAGER.PHP
 * CLASS INSTEAD
 *
 * @author ThreeZeroZero
 *
*/
class TokenGenerator {

	/* Upper bounds for the number of times this can iterate for */
	private static $MAX_RECURSION_COUNT = 5;

	/**
	 * This has no external instantiation, methods are called statically such as:
	 *
	 * 			-	TokenGenerator::generateToken();
	 */
	private function __construct(){
	}

	/**
	 * Generates a unique token and adds it to the database
	 *
	 * @param $userID 			The user ID to generate a token for
	 * @param $iterationCounter	Prevent this from recursing indefinitely (does not need to be set),
	 * 							$MAX_RECURSION_COUNT attempts
	 *
	 * @return 					The token that was generated
	 */
	public static function generateToken($userID, $iterationCounter = 0){

		/* Generate a random token of 32 bytes length */
		//     	$token = base64_encode(openssl_random_pseudo_bytes(32, $secure));
		$token = sha1(uniqid("", true)); //TODO user openSSL instead

		/* Recurse if this is unsafe */
		//     	if(!$secure && $iterationCounter < $MAX_RECURSION_COUNT){
		//    		return TokenGenerator::generateToken($userID, $iterationCounter++);
		//     	}
		// 	/* Throw an exception */
		// 			else{
		// 				throw new Exception("Maximum token generator recursion reached");
		// 			}

		/* Open SQL object - handles errors */
		$mysqli = DBConnection::getMySQLConnection();

		/* Escape the input values */
		$userID = intval($userID);
		$token = $mysqli->real_escape_string($token);

		/* Generate a query */
		$query = "SELECT * FROM expired_tokens WHERE token = \"" . $token . "\";";
		$result = $mysqli->query($query);

		/* Generate a query */
		$query = "INSERT INTO connected_clients (token, user_id) VALUES (\"" . $token . "\", \"" . $userID . "\");";

		/* Obtain the result of this */
		if($mysqli->query($query) === true){

			/* End connection */
			$mysqli->close();

			/* Return token */
			return $token;
		}

		/* Recurse, token exists in currently connected clients */
		else{

			/* End connection */
			$mysqli->close();

			/* Do again */
			if($iterationCounter < $MAX_RECURSION_COUNT){
				return TokenGenerator::generateToken($userID, $iterationCounter++);
			}

			/* Throw an exception */
			else{
				throw new Exception("Unfortunately, we could not authenticate your session, please log in to try again. We apologise for the inconvenience.");
			}
		}
	}

}

?>