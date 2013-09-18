<?php

/**
 * This class is responsible for generating well formed and consistent payloads for the application interface. Payload messages are appended to
 * the output stream where required.
 *
 * @author ThreeZeroZero
 *
 */
class ResponseGenerator {

	/**
	 * This has no external instantiation, methods are called statically such as:
	 *
	 * 			-	ResponseGenerator::generateSuccess();
	 */
	private function __construct(){}

	/**
	 * Generates a success payload for the responder, allowing the caller to pass in any extra information about the request.
	 *
	 * Success tags are placed in the highest level of the payload.
	 *
	 * The caller has the option to display immediately and have the result discarded (pass true) or have the result returned
	 * to them for any further processing (pass false).
	 *
	 * While the values are not strictly type-defined, they should be (string, string, string, bool) in general
	 *
	 * @param $message				A display message for a simple response, may be null
	 * @param $payloadToAppend		A set of data that will be included in the return payload under the key "payload", may be null,
	 * 								should be string or array
	 * @param $token				The token that the client has used to access this instance, may be null but really shouldn't be
	 * @param $displayImmediately	A boolean to determine if this should output immediately (most probable behaviour).
	 * 								Passing a value of true will throw this to the output stream and discard the generated
	 * 								objects immediately. Passing false will NOT display the output stream, the caller will
	 * 								receive the output stream and will be responsible for displaying it
	 */
	public static function generateSuccess($message, $payloadToAppend, $token, $displayImmediately = null){

		/* Correct any null values */
		if($message == null){
			$message = "";
		}
		if($payloadToAppend == null){
			$payloadToAppend = "";
		}
		if($token == null || !is_string($token)){
			$token = ""; //TODO write something that validates the token and check its expiry
		}
		if($displayImmediately === null || !is_bool($displayImmediately)){
			$displayImmediately = true;
		}

		/* Generate the successful instance */
		$success_array = array(
				"success" => true,
				"status" => "200",
				"time" => date("r"),
				"token" => $token,
				"message" => $message,
				"payload" => $payloadToAppend
		);

		/* Output the stream now */
		if($displayImmediately){
			echo ResponseGenerator::prettyPrint(json_encode($success_array));
		}

		/* Return to the caller, the caller is now responsible for displaying */
		else{
			return json_encode($success_array);
		}
	}

	/**
	 * Generates and displays a failure message token for this connection. Message and data appendage are optional and may be null
	 *
	 * Failure tags are placed in the highest level of the payload.
	 *
	 * The caller has the option to display immediately and have the result discarded (pass true) or have the result returned
	 * to them for any further processing (pass false)
	 *
	 * While the values are not strictly type-defined, they should be (string, string, string, bool) in general
	 *
	 * @param $message 				A display message for the application to display, may be null
	 * @param $payloadToAppend		A set of data that will be included in the return payload under the key "payload", may be null,
	 * 								should be string or array
	 * @param $token				The token that the client has used to access this instance, may be null but really shouldn't be
	 * @param $errorCode			An optional error code, defaults to 400
	 * @param $displayImmediately	A boolean to determine if this should output immediately (most common behaviour).
	 * 								Passing a value of true will throw this to the output stream and discard the generated
	 * 								objects immediately. Passing false will NOT display the output stream, the caller will
	 * 								receive the output stream and will be responsible for displaying it
	 *
	 * @return						An output stream as a string that will need to be displayed or altered by the caller. Will
	 * 								have no return type if the final boolean value is true
	 */
	public static function generateFailure($message, $payloadToAppend, $token, $errorCode = "400", $displayImmediately = true){

		/* Correct any null value for the boolean */
		if($displayImmediately === null || !is_bool($displayImmediately)){
			$displayImmediately = true;
		}
		if($errorCode === null){
			$errorCode = "400";
		}

		/* Parse the return values (json_decode's true tag converts to associative array) */
		$error_array = json_decode(ResponseGenerator::generateSuccess($message, $payloadToAppend, $token, false), true);

		/* Swap values to the failed instance */
		$error_array["success"] = false;
		$error_array["status"] = $errorCode;

		/* Output the stream now */
		if($displayImmediately){
			echo ResponseGenerator::prettyPrint(json_encode($error_array));
		}

		/* Return to the caller, the caller is now responsible for displaying */
		else{
			return json_encode($error_array);
		}
	}

	/**
	 * Convenience method for default exception notices - the payload will contain the stack trace and exception description
	 *
	 * @param Exception $e 		Exception that was thrown
	 * @param $token			Authentication token for this session
	 */
	public static function generateExceptionNotice(Exception $e, $token){
		ResponseGenerator::generateFailure(
				$e->getMessage(),
				array("exception" => $e->__toString()),
				$token,
				$errorCode = "-1001"
		);
	}

	/**
	 * Makes a data payload pretty printed
	 *
	 * @param $json 	The JSON payload to pretty
	 * @return string	The prettied payload
	 */
	public static function prettyPrint($json) {
		$result = '';
		$level = 0;
		$prev_char = '';
		$in_quotes = false;
		$ends_line_level = NULL;
		$json_length = strlen( $json );

		for( $i = 0; $i < $json_length; $i++ ) {
			$char = $json[$i];
			$new_line_level = NULL;
			$post = "";
			if( $ends_line_level !== NULL ) {
				$new_line_level = $ends_line_level;
				$ends_line_level = NULL;
			}
			if( $char === '"' && $prev_char != '\\' ) {
				$in_quotes = !$in_quotes;
			} else if( ! $in_quotes ) {
				switch( $char ) {
					case '}': case ']':
						$level--;
						$ends_line_level = NULL;
						$new_line_level = $level;
						break;

					case '{': case '[':
						$level++;
					case ',':
						$ends_line_level = $level;
						break;

					case ':':
						$post = " ";
						break;

					case " ": case "\t": case "\n": case "\r":
						$char = "";
						$ends_line_level = $new_line_level;
						$new_line_level = NULL;
						break;
				}
			}
			if( $new_line_level !== NULL ) {
				$result .= "\n".str_repeat( "\t", $new_line_level );
			}
			$result .= $char.$post;
			$prev_char = $char;
		}
		return $result;
	}
}
?>