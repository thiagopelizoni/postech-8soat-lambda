import boto3
import json
import os

def lambda_handler(event, context):
    client = boto3.client('cognito-idp')
    user_pool_client_id = os.getenv("COGNITO_USER_POOL_CLIENT_ID")

    if event.get("httpMethod") != "POST":
        return {
            "statusCode": 405,
            "body": json.dumps({"error": "Method Not Allowed"})
        }

    body = json.loads(event.get("body", "{}"))
    email = body.get("email")
    senha = body.get("senha")

    if not email or not senha:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "Email e senha são requeridos!"})
        }

    try:
        auth_response = client.initiate_auth(
            AuthFlow='USER_PASSWORD_AUTH',
            AuthParameters={
                'USERNAME': email,
                'PASSWORD': senha
            },
            ClientId=user_pool_client_id
        )
        
        return {
            "statusCode": 200,
            "body": json.dumps({
                "success": True,
                "token": auth_response.get("AuthenticationResult", {}).get("IdToken")
            })
        }
    
    except client.exceptions.NotAuthorizedException:
        return {
            "statusCode": 200,
            "body": json.dumps({"success": False, "message": "Credenciais inválidas."})
        }
    
    except client.exceptions.UserNotFoundException:
        return {
            "statusCode": 200,
            "body": json.dumps({"success": False, "message": "Usuário não encontrado."})
        }
    
    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }
