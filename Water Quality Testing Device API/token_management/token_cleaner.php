<?php

/* Depends on the DBConnection for opening connections to the database */
require_once("/home/a9969020/public_html/database_connection/DBConnection.php");

/**
 * Helper cron job that will clear invalid/expired tokens from the database. Will ideally run every
 * minute.
 *
 * php -f <PATH>/token_management/token_checker.php *\/1 * * * *
 *
 * @author ThreeZeroZero
 *
*/

/* The amount of time a token is valid for */
$MAXIMUM_VALID_TIME = "+3 hours";

/* The name of the database the current client list is being stored on */
$CLIENTS_DATABASE_NAME = "connected_clients";

/* Obtain an SQL instance */
$mysqli = DBConnection::getMySQLConnection();

/* Escape it */
$CLIENTS_DATABASE_NAME = $mysqli->real_escape_string("connected_clients");

/* Establish the query, polling each client */
$query = "SELECT * FROM " . $CLIENTS_DATABASE_NAME;
$result = $mysqli->query($query);
while ($row = mysqli_fetch_array($result, MYSQLI_ASSOC)) {

	/* If the creation time of the token is older than three hours, remove the object */
	if(strtotime($MAXIMUM_VALID_TIME, strtotime($row["created_time"])) < time()){
		$query = "DELETE FROM " . $CLIENTS_DATABASE_NAME . " WHERE token = \"" . $mysqli->real_escape_string($row["token"]) . "\"";
		$mysqli->query($query);
	}
}

/* End connection */
$mysqli->close();


/* End the script */
exit();

?>