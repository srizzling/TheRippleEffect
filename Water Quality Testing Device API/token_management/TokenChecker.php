<?php

/* Depends on the DBConnection for opening connections to the database */
require_once("/home/a9969020/public_html/database_connection/DBConnection.php");

/**
 * Helper class that will fetch check the validity of an access token
 *
 * THIS IS STRICTLY A HELPER CLASS, DO NOT ATTEMPT TO ACCESS METHODS HERE - USE THE TOKENMANAGER.PHP
 * CLASS INSTEAD
 *
 * @author ThreeZeroZero
 *
*/
class TokenChecker {

	/**
	 * This has no external instantiation, methods are called statically such as:
	 *
	 * 			-	TokenGenerator::checkToken();
	 */
	private function __construct(){
	}

	/**
	 * Checks the authentication of a token, returning a boolean
	 *
	 * @param $token The token to check the validity of
	 * @return 		 True if the token is valid
	 */
	public static function checkToken($token){

		/* Open SQL object - handles errors */
		$mysqli = DBConnection::getMySQLConnection();

		/* Escape the input values */
		$token = $mysqli->real_escape_string($token);

		/* Generate a query */
		$query = "SELECT * FROM connected_clients WHERE token = \"" . $token . "\";";
		$result = $mysqli->query($query);

		/* Kill the connection */
		$mysqli->close();

		/* Determine the result */
		return $result -> num_rows >= 1;
	}

	/**
	 * Removes the row for this token from the database
	 *
	 * @param $token The token to remove
	 */
	public static function removeToken($token){

		/* Open SQL object - handles errors */
		$mysqli = DBConnection::getMySQLConnection();

		/* Escape the input values */
		$token = $mysqli->real_escape_string($token);

		/* Generate a query */
		$query = "DELETE FROM connected_clients WHERE token = \"" . $token . "\"";
		$mysqli->query($query);

		/* Kill the connection */
		$mysqli->close();
	}
}

?>