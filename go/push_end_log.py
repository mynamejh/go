# 이 페이지는 로그에 종료가 없을때 가장 마지막에 종료한 시점을 기준으로 서버 로그 테이블에 강제 종료로그 강제주입페이지입니다.
# 임시 저장(content = '종료') 로 되게?

import subprocess
import re
from datetime import datetime
import pymysql
from PyQt5.QtCore import QTimer,QDateTime

# db 정보
db_url = '101.79.10.48'
db_username= 'object'
db_port = 3308 
db_password = 'object12!@'
db_name = 'object'

conn = None
time=QDateTime.currentDateTime() #현재 시간 가져오기
now = datetime.now()
timeDisplay=time.toString('yyyy-MM-dd hh:mm:ss')


def getConnection():
    global conn
    conn = pymysql.connect(host=db_url,user=db_username, port=db_port ,password=db_password, db=db_name, charset='utf8') # mysql 정보
    return conn

def push_end_log(id):
    #window command 명령어 확인!! 띄어쓰기 단위로! (wevtutil)_이벤트 로그 분석(이벤트 관리도구)
    command = 'wevtutil qe System /rd:true /c:1 /f:text /q:"*[System[(EventID=6006)]]"'
    result = subprocess.check_output(command, shell=True, text=True)
    
    datetime_pattern = r"Date: (\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d)"  # 정규식임
    match = re.search(datetime_pattern, result)
    datetime_str = match.group(1)  # 날짜시간추출함
    datetime_format = "%Y-%m-%dT%H:%M:%S.%f"
    timestamp = datetime.strptime(datetime_str, datetime_format)  # 타임스탬프형식 변환
    
    

    conn = getConnection() #디비연결하고
    cur = conn.cursor()
    sql = "INSERT INTO log VALUES (DEFAULT, %s, %s, %s, %s)"
    data = (id, '종료', '임시중지', timeDisplay) #Prepared Statement 로 실행
    cur.execute(sql, data)
    conn.commit()
    conn.close()