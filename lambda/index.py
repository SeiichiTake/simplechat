import json
import os
import urllib.request
import urllib.error

# FastAPI サーバーのベース URL
FASTAPI_BASE_URL = os.environ.get("FASTAPI_BASE_URL", "https://de8a-34-16-134-53.ngrok-free.app/")

def lambda_handler(event, context):
    try:
        print("Received event:", json.dumps(event))
        
        # Cognito 認証情報
        user_info = None
        if 'requestContext' in event and 'authorizer' in event['requestContext']:
            user_info = event['requestContext']['authorizer']['claims']
            print(f"Authenticated user: {user_info.get('email') or user_info.get('cognito:username')}")
        
        # parse request body
        body = json.loads(event.get('body') or "{}")
        message = body.get('message', '')
        conversation_history = body.get('conversationHistory', [])
        
        print("Processing message:", message)
        
        # build payload for FastAPI /generate endpoint
        payload = {
            "prompt": message,
            "max_new_tokens": 512,
            "do_sample": True,
            "temperature": 0.7,
            "top_p": 0.9
        }
        data = json.dumps(payload).encode("utf-8")  # encode JSON to bytes
        
        url = f"{FASTAPI_BASE_URL.rstrip('/')}/generate"
        print("Calling FastAPI generate endpoint:", url, "with payload:", payload)
        
        # create HTTP POST request
        req = urllib.request.Request(
            url,
            data=data,
            method="POST",
            headers={"Content-Type": "application/json"}
        )
        
        # send request
        with urllib.request.urlopen(req, timeout=30) as resp:
            resp_body = resp.read().decode("utf-8")
            result = json.loads(resp_body)
        print("FastAPI response:", result)
        
        # extract generated text
        assistant_response = result.get("generated_text") or result.get("generatedText") or ""
        if not assistant_response:
            raise Exception("No generated_text in FastAPI response")
        
        # update conversation history
        messages = conversation_history.copy()
        messages.append({"role": "user", "content": message})
        messages.append({"role": "assistant", "content": assistant_response})
        
        # return successful response
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token",
                "Access-Control-Allow-Methods": "OPTIONS,POST"
            },
            "body": json.dumps({
                "success": True,
                "response": assistant_response,
                "conversationHistory": messages
            })
        }
    
    except urllib.error.HTTPError as http_err:
        # HTTP error from FastAPI server
        error_message = f"HTTP error: {http_err.code} {http_err.reason}"
        print("Error:", error_message)
        return {
            "statusCode": http_err.code,
            "headers": {"Content-Type": "application/json", "Access-Control-Allow-Origin": "*"},
            "body": json.dumps({"success": False, "error": error_message})
        }
    except Exception as error:
        # general exception
        print("Error:", str(error))
        return {
            "statusCode": 500,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token",
                "Access-Control-Allow-Methods": "OPTIONS,POST"
            },
            "body": json.dumps({
                "success": False,
                "error": str(error)
            })
        }
