from app.core.services import aws_lambda_handlers as awslamb

def main():
    awslamb.google_drive_main()
    
# 실행
if __name__ == "__main__":
    main()
