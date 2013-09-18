<?php

/**
 * A class that holds all of the database constants so that the entire project can be easily moved about
 * different hosts and servers/DB locations
 *
 * @author ThreeZeroZero
 *
 */
class DBConnection {

	/* Database details */
	public static $HOST_NAME = "mysql12.000webhost.com";
	public static $USER_NAME = "a9969020_scb";
	public static $PASSWORD = "qaz123";
	public static $DATABASE = "a9969020_scb";

	/**
	 * Opens an SQL instance or handles error if one is thrown. The caller must tidy the object up
	 */
	public static function getMySQLConnection(){

		/* Open SQL object */
		$mysqli = new mysqli(
				DBConnection::$HOST_NAME,
				DBConnection::$USER_NAME,
				DBConnection::$PASSWORD,
				DBConnection::$DATABASE
		);

		/* Check connection */
		if (mysqli_connect_error()) {
			ResponseGenerator::generateExceptionNotice(new Exception(
			"Error number: " . mysqli_connect_errno() .
			"\n\nError Description" . mysqli_connect_error(), null)
			);
			exit();
		}

		/* Return the connection */
		else{
			return $mysqli;
		}
	}
}

?>