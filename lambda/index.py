import json
import urllib.request
from botocore.exceptions import ClientError

def lambda_handler(event, context):
    try:
        print("Received event:", json.dumps(event))
        
        # リクエストボディの解析
        body = json.loads(event['body'])
        message = body['message']
        print("Processing message:", message)
        
        # APIエンドポイント
        api_url = "https://51f3-34-82-102-252.ngrok-free.app/generate"

        # リクエストデータの構築
        request_data = {
            "prompt": message,
            "max_new_tokens": 512,
            "do_sample": True,
            "temperature": 0.7,
            "top_p": 0.9
        }
        print("Sending request to API:", json.dumps(request_data))

        # JSONデータをエンコード
        encoded_data = json.dumps(request_data).encode('utf-8')

        # HTTPリクエストの構築
        req = urllib.request.Request(
            api_url,
            data=encoded_data,
            headers={
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            method='POST'
        )

        # API呼び出しとレスポンス取得
        with urllib.request.urlopen(req, timeout=60) as response:
            response_data = response.read()
            api_response = json.loads(response_data)
            print("API response:", json.dumps(api_response))

        # レスポンスの整形
        if "generated_text" in api_response:
            assistant_response = api_response["generated_text"]
        elif "response" in api_response:
            assistant_response = api_response["response"]
        else:
            assistant_response = str(api_response)

        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*"
            },
            "body": json.dumps({
                "success": True,
                "response": assistant_response
            })
        }

    except Exception as error:
        print("Error:", str(error))
        return {
            "statusCode": 500,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*"
            },
            "body": json.dumps({
                "success": False,
                "error": str(error)
            })
        }

