import json
import os
import urllib.request
import re
from botocore.exceptions import ClientError

def lambda_handler(event, context):
    try:
        print("Received event:", json.dumps(event))
        
        # リクエストボディの解析 - シンプルにmessageだけ取得
        body = json.loads(event['body'])
        message = body['message']
        
        print("Processing message:", message)
        
        # APIエンドポイントの設定
        api_url = "https://51f3-34-82-102-252.ngrok-free.app"
        # リクエストヘッダーにSwagger UIのcurlコマンドと同じものを使用
        req = urllib.request.Request(
            api_url,
            data=encoded_data,
            headers={
                'Content-Type': 'application/json',
                'accept': 'application/json'  # このヘッダーを追加
            },
            method='POST'
        )
        
        # シンプルなリクエスト形式
        request_data = {
            "prompt": message,
            "max_new_tokens": 512,
            "do_sample": True,
            "temperature": 0.7,
            "top_p": 0.9
        }
        
        # デバッグ情報
        print("Sending request to API:", json.dumps(request_data))
        
        # JSONデータのエンコード
        encoded_data = json.dumps(request_data).encode('utf-8')
        
        # HTTPリクエスト
        req = urllib.request.Request(
            api_url,
            data=encoded_data,
            headers={'Content-Type': 'application/json'},
            method='POST'
        )
        
        # APIの呼び出し
        with urllib.request.urlopen(req, timeout=60) as response:
            response_data = response.read()
            api_response = json.loads(response_data)
            
            # レスポンスの取得 - シンプルに必要な情報のみ
            print("API response:", json.dumps(api_response))
            
            # APIのレスポンス形式に合わせて適切なキーを使用
            assistant_response = ""
            if "generated_text" in api_response:
                assistant_response = api_response["generated_text"]
            elif "response" in api_response:
                assistant_response = api_response["response"]
            else:
                # その他のキーがある場合はそれを試す
                assistant_response = str(api_response)
            
            # シンプルなレスポンス形式
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
        
        # エラーレスポンス
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
