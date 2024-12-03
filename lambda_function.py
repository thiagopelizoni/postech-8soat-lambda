import os
import psycopg2
import json
import bcrypt

def lambda_handler(event, context):
    db_host = os.getenv("DB_HOST").split(':')[0]
    db_port = os.getenv("DB_HOST").split(':')[1] if ':' in os.getenv("DB_HOST") else '5432'
    db_name = os.getenv("DB_NAME")
    db_user = os.getenv("DB_USERNAME")
    db_password = os.getenv("DB_PASSWORD")
    
    try:
        connection = psycopg2.connect(
            host=db_host,
            port=db_port,
            database=db_name,
            user=db_user,
            password=db_password
        )
        cursor = connection.cursor()
        
        if event.get("httpMethod") != "POST":
            return {
                "statusCode": 405,
                "body": json.dumps({"error": "Method Not Allowed"})
            }
        
        body = json.loads(event.get("body", "{}"))
        cpf = body.get("cpf")
        senha = body.get("senha")
        
        if not cpf or not senha:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "CPF e senha são requeridos!"})
            }
        
        query = "SELECT senha FROM clientes WHERE cpf = %s"
        cursor.execute(query, (cpf,))
        result = cursor.fetchone()
        
        if not result:
            return {
                "statusCode": 200,
                "body": json.dumps({"success": False})
            }
        
        hashed_password = result[0]
        
        if bcrypt.checkpw(senha.encode('utf-8'), hashed_password.encode('utf-8')):
            return {
                "statusCode": 200,
                "body": json.dumps({"success": True})
            }
        else:
            return {
                "statusCode": 200,
                "body": json.dumps({"success": False})
            }
    
    except psycopg2.Error as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }
    
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals():
            connection.close()
