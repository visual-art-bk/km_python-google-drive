import os
import pandas as pd
from datetime import datetime
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from app.core.utils.Logger import Logger

logger = Logger(name="main", log_file="main.log").get_logger()


# 1. 서비스 계정 인증 및 API 클라이언트 생성 함수
def authenticate_google_services(service_account_file, scopes):
    """
    서비스 계정 인증 및 API 클라이언트 생성
    """
    try:
        # 서비스 계정 인증 설정
        credentials = Credentials.from_service_account_file(
            service_account_file, scopes=scopes
        )
        # Google Sheets 및 Drive API 클라이언트 생성
        sheets_service = build("sheets", "v4", credentials=credentials)
        drive_service = build("drive", "v3", credentials=credentials)
        print("Google API 인증 성공!")
        return sheets_service, drive_service
    except Exception as e:
        logger.exception(f"Google API 인증 실패: {e}")


# 2. Google Drive 파일 목록 테스트 함수
def test_google_drive_authentication(drive_service):
    """
    Google Drive API 인증 테스트: 파일 목록 가져오기
    """
    try:
        results = (
            drive_service.files().list(pageSize=5, fields="files(id, name)").execute()
        )
        items = results.get("files", [])
        print("Google Drive 인증 테스트 성공! 파일 목록:")
        for item in items:
            print(f"- 파일 이름: {item['name']}, 파일 ID: {item['id']}")
        return True
    except Exception as e:
        logger.exception(f"Google Drive 인증 테스트 실패: {e}")


# 3. Google Sheets 스프레드시트 생성 함수
def create_google_sheet(sheets_service, title):
    """
    Google Sheets 생성
    """
    try:
        sheet_metadata = {"properties": {"title": title}}
        sheet = (
            sheets_service.spreadsheets()
            .create(body=sheet_metadata, fields="spreadsheetId")
            .execute()
        )
        spreadsheet_id = sheet.get("spreadsheetId")
        print(f"Google Sheets 생성 성공! ID: {spreadsheet_id}")
        return spreadsheet_id
    except Exception as e:
        logger.exception(f"Google Sheets 생성 실패: {e}")


# 4. Google Sheets 데이터 업로드 함수
def upload_data_to_google_sheet(sheets_service, spreadsheet_id, data, start_range="A1"):
    """
    Google Sheets에 데이터 업로드
    """
    try:
        sheet_data = [
            data.columns.tolist()
        ] + data.values.tolist()  # 데이터프레임을 리스트로 변환
        update_body = {"values": sheet_data}
        sheets_service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range=start_range,
            valueInputOption="RAW",
            body=update_body,
        ).execute()
        print("Google Sheets에 데이터 업로드 성공!")
    except Exception as e:
        logger.exception(f"Google Sheets 데이터 업로드 실패: {e}")


# 5. Google Drive 파일 속성 업데이트 함수
def update_google_drive_file_metadata(drive_service, file_id, folder_id):
    """
    Google Drive에서 파일을 특정 폴더로 이동
    """
    try:
        drive_service.files().update(
            fileId=file_id,
            addParents=folder_id,
            removeParents="root",
            fields="id, parents",
        ).execute()
        print("Google Drive 파일 이동 성공!")
    except Exception as e:
        logger.exception(f"Google Drive 파일 이동 실패: {e}")


# 6. 메인 실행 함수
def google_drive_main():
    # 설정
    SERVICE_ACCOUNT_FILE = (
        "semiotic-summer-445422-v6-7ef1e0b52af1.json"  # 서비스 계정 JSON 파일 경로
    )
    SCOPES = [
        "https://www.googleapis.com/auth/drive",
        "https://www.googleapis.com/auth/spreadsheets",
    ]
    CSV_FILE_NAME = "example.csv"

    # 동적으로 구글 시트 이름 생성
    current_datetime = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    SHEET_TITLE = f"크몽_예약테스트_{current_datetime}"
    TARGET_FOLDER_ID = "1a9oIT2mTHhqQWe7bMT5a-P4dGf0CkE4X"  # 구글 드라이브 폴더 ID

    try:
        # Google API 인증
        sheets_service, drive_service = authenticate_google_services(
            SERVICE_ACCOUNT_FILE, SCOPES
        )

        # Google Drive 인증 테스트
        test_google_drive_authentication(drive_service)

        # 로컬 데이터프레임 생성 및 저장
        data = {
            "이름": ["홍길동", "김철수", "이영희"],
            "나이": [25, 30, 28],
            "직업": ["개발자", "디자이너", "기획자"],
        }
        df = pd.DataFrame(data)
        df.to_csv(CSV_FILE_NAME, index=False, encoding="utf-8-sig")
        print(f"로컬 CSV 파일 생성 완료: {CSV_FILE_NAME}")

        # Google Sheets 생성 및 데이터 업로드
        spreadsheet_id = create_google_sheet(sheets_service, SHEET_TITLE)
        upload_data_to_google_sheet(sheets_service, spreadsheet_id, df)

        # Google Drive에서 파일 폴더 이동
        update_google_drive_file_metadata(
            drive_service, spreadsheet_id, TARGET_FOLDER_ID
        )

        print("작업이 모두 성공적으로 완료되었습니다!")
    except Exception as e:
        logger.exception(f"작업 중 오류 발생: {e}")
