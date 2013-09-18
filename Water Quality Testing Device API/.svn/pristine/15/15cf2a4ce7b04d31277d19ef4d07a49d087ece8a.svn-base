#from django.http import HttpRequest, HttpResponse
from datetime import datetime
import json
import traceback

"""
This class is responsible for generating well formed and consistent payloads for the application interface. Payload messages are appended to
the output stream where required.

@author Waterloop
"""
class ResponseGenerator:

    """
    Generates a success payload for the responder, allowing the caller to pass in any extra information about the request.

    Success tags are placed in the highest level of the payload.

    The caller has the option to display immediately and have the result discarded (pass true) or have the result returned
    to them for any further processing (pass false).

    While the values are not strictly type-defined, they should be (string, string, string, bool) in general

    @param message              A display message for a simple response, may be null
    @param payloadToAppend      A set of data that will be included in the return payload under the key "payload", may be null,
                                 should be string or array
    @param token                The token that the client has used to access this instance, may be null but really shouldn't be
    @param displayImmediately   A boolean to determine if this should output immediately (most probable behaviour).
                                 Passing a value of true will throw this to the output stream and discard the generated
                                 objects immediately. Passing false will NOT display the output stream, the caller will
                                 receive the output stream and will be responsible for displaying it
    """
    @staticmethod
    def generateSuccess(message, payloadToAppend, token, displayImmediately = True):

        # Correct any null values
        if message == None:
            message = ""
        if payloadToAppend == None:
            payloadToAppend = ""
        if token == None:
            token = ""

        # Generate the successful instance
        success_array = {
                "success": 1,
                "status": "200",
                "time": datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
                "token": token,
                "message": message,
                "payload": payloadToAppend
        }

        # Output the stream now
        if displayImmediately:
            print(json.dumps(success_array, sort_keys = True, indent = 4, separators = (',', ': ')))

        # Return to the caller, the caller is now responsible for displaying
        else:
            return json.dumps(success_array, sort_keys = True, indent = 4, separators = (',', ': '))

    """
    Generates and displays a failure message token for this connection. Message and data appendage are optional and may be null

    Failure tags are placed in the highest level of the payload.

    The caller has the option to display immediately and have the result discarded (pass true) or have the result returned
    to them for any further processing (pass false)

    While the values are not strictly type-defined, they should be (string, string, string, string, bool) in general

    @param message              A display message for the application to display, may be null
    @param payloadToAppend      A set of data that will be included in the return payload under the key "payload", may be null,
                                should be string or array
    @param token                The token that the client has used to access this instance, may be null but really shouldn't be
    @param errorCode            An optional error code, will default to 400
    @param displayImmediately   A boolean to determine if this should output immediately (most common behaviour).
                                Passing a value of true will throw this to the output stream and discard the generated
                                objects immediately. Passing false will NOT display the output stream, the caller will
                                receive the output stream and will be responsible for displaying it

    @return                     An output stream as a string that will need to be displayed or altered by the caller. Will
                                have no return type if the final boolean value is true
    """
    @staticmethod
    def generateFailure(message, payloadToAppend, token, errorCode = "400", displayImmediately = True):

        # Parse the return values
        error_array = json.loads(ResponseGenerator.generateSuccess(message, payloadToAppend, token, False))

        # Swap values to the failed instance
        error_array["success"] = 0
        error_array["status"] = errorCode

        # Output the stream now
        if displayImmediately:
            print(json.dumps(error_array, sort_keys = True, indent = 4, separators = (',', ': ')))

        # Return to the caller, the caller is now responsible for displaying
        else:
            return json.dumps(error_array, sort_keys = True, indent = 4, separators = (',', ': '))

    """
    Convenience method for default exception notices - the payload will contain the stack trace and exception description

    @param e        Exception that was thrown
    @param token    Authentication token for this session
    """
    @staticmethod
    def generateExceptionNotice(e, token):
        ResponseGenerator.generateFailure(
                "Something has gone wrong with the server." +
                "\n\nWe are attempting to have the issue resolved as soon as possible." +
                "\n\nPlease try again later. Or get in contact if you are still experiencing difficulties.",
                {"exception": {
                               "message": str(e), "stack_trace": {
                                                     "file": traceback.extract_stack()[0][0], "line_number": traceback.extract_stack()[0][1], "issue": traceback.extract_stack()[0][3]
                                                     }
                  }
                 },
                token,
                "-1001")