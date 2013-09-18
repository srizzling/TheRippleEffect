from ResponseGenerator import ResponseGenerator

test_token = "1234567890"

print("An example success payload:")
ResponseGenerator.generateSuccess("Test", {"test": "An embedded dictionary"}, test_token)

print("\n\nAn example failure payload:")
ResponseGenerator.generateFailure("Test", {"error": {"password": "An example error would have a tag like this"}}, test_token)

print("\n\nAn example failure payload, note the different error code options:")
ResponseGenerator.generateFailure("Test", {"error": {"token": "Your session has expired, please log back in"}}, test_token, errorCode = "403")

print("\n\nAn example exception payload:")
try:
    raise Exception("An exception has been raised - all scripts should execute in try-except blocks")
except Exception as e:
    ResponseGenerator.generateExceptionNotice(e, test_token)