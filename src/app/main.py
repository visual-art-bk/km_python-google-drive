from app.core.services import aws_lambda_handlers as awslamb

def main():
    awslamb.lambda_handler()
    
# 실행
if __name__ == "__main__":
    main()
