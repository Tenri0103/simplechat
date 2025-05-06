import json
import os
import urllib.request
import re
from botocore.exceptions import ClientError

# Lambda コンテキストからリージョンを抽出する関数
def extract_region_from_arn(arn):
    # ARN 形式: arn:aws:lambda:region:account-id:function:function-name
    match = re.search('arn:aws:lambda:([^:]+):', arn)
    if match:
        return match.group(1)
    return "us-east-1"  # デフォルト値

def lambda_handler(event, context):
    try:
        print("Received event:", json.dumps(event))
        
        # Cognitoで認証されたユーザー情報を取得
        user_info = None
        if 'requestContext' in event and 'authorizer' in event['requestContext']:
            user_info = event['requestContext']['authorizer']['claims']
            print(f"Authenticated user: {user_info.get('email') or user_info.get('cognito:username')}")
        
        # リクエストボディの解析
        body = json.loads(event['body'])
        message = body['message']
        conversation_history = body.get('conversationHistory', [])
        
        print("Processing message:", message)
        
        # カスタムAPIのエンドポイントを設定
        # Swagger UIで確認した正しいエンドポイントを使用
        api_url = "https://51f3-34-82-102-252.ngrok-free.app/generate"
        
        # Swagger UIで確認した正しいリクエスト形式を使用
        request_data = {
            "prompt": message,  # "message"ではなく"prompt"を使用
            "max_new_tokens": 512,
            "do_sample": True,
            "temperature": 0.7,
            "top_p": 0.9
        }
        
        # JSONデータのエンコード
        encoded_data = json.dumps(request_data).encode('utf-8')
        
        # HTTPリクエストの作成
        req = urllib.request.Request(
            api_url,
            data=encoded_data,
            headers={'Content-Type': 'application/json'},
            method='POST'
        )
        
        # APIを呼び出し、レスポンスを取得
        try:
            with urllib.request.urlopen(req, timeout=30) as response:
                response_data = response.read()
                api_response = json.loads(response_data)
                
                # APIからの応答を取得
                # 注意: レスポンスの形式はAPIの仕様に合わせて調整
                assistant_response = api_response.get('generated_text', '')
                # レスポンス形式が異なる場合は、適切なキーを使用
                if not assistant_response and 'response' in api_response:
                    assistant_response = api_response.get('response', '')
                
                # 会話履歴の更新（元のコードと同様の形式を維持）
                messages = conversation_history.copy()
                messages.append({
                    "role": "user",
                    "content": message
                })
                messages.append({
                    "role": "assistant",
                    "content": assistant_response
                })
                
                # 成功レスポンスの返却（元のフォーマットを維持）
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
                
        except urllib.error.URLError as e:
            print(f"API request error: {str(e)}")
            raise Exception(f"API request failed: {str(e)}")
        
    except Exception as error:
        print("Error:", str(error))
        
        # エラーレスポンス（元のコードと同様）
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
