# 이 페이지는 로그 저장하는 프로세스가 담긴 페이지입니다. 
# 시작종료 로그는 입력되는데 시간 추가할시 아직 웹을 못만들어서 추가로그는 안찍힘
import pymysql
from datetime import datetime


# db 정보
db_url = '101.79.10.48'
db_username= 'object'
db_port = 3308
db_password = 'object12!@'
db_name = 'object'

conn = None

# mysql 연결
def getConnection():
    global conn
    conn = pymysql.connect(host=db_url,user=db_username, port=db_port ,password=db_password, db=db_name, charset='utf8') # mysql 정보
    return conn

# 커서 생성/ 테이블 조회 및 데이터 입력(log 테이블)
def log_save(id):
    now = datetime.now() #현재시간받아서
    timestamp = now.strftime('%Y-%m-%d %H:%M:%S.%f') #타임스탬프형식으로 변환 후 _ 시간을 문자열로(원하는 포맷=> strftime()) # 예시. 2020-01-07 15:40:15(.%f는 물어보기)
    conn = getConnection() # 연결
    cur = conn.cursor() # 커서 생성

    sql = "SELECT * FROM log WHERE id = %s" #쿼리작성 (아이디에 해당하는 값)
    #sql_test = "select l.id id, u.email_id email from log l, user u where u.id= %s"
    cur.execute(sql, (id,)) #Prepared Statement 로 실행
    row = cur.fetchone() #fetchone() : 한 번 호출에 하나 row만 가져옴

    # 데이터 입력 (default는 순번)
    if row is None: #로그가 하나도없을때
        sql = "INSERT INTO log VALUES (DEFAULT, %s, %s, %s, %s)"
        data = (id, '시작', '시작', timestamp) #Prepared Statement 로 실행
        cur.execute(sql, data) # cur 사용하여 정의된 sql 쿼리 실행, data값 placeholder에 저장
        
        conn.commit()
    else: #로그가 있으면 (sql값 = '시작' )
        sql = "select subject from log where num = (select max(num) from log where id = %s and (subject = '시작' or subject = '종료'))"#해당 id에서 로그에서 시작,종료만 해당하는 num 젤큰거 가져와서;
        cur.execute(sql, (id,)) #쿼리실행
        row = cur.fetchone() #객체에 담아서 ,현재는 '시작'
        if(row[0] == '시작'):# subject 가 '시작'이면옴
            sql = "INSERT INTO log VALUES (DEFAULT, %s, %s, %s, %s)"
            data = (id, '종료', '종료', timestamp) #Prepared Statement 로 실행
            cur.execute(sql, data)
            conn.commit()
        elif(row[0] == '종료'):# subject 가 '종료'이면
            sql = "INSERT INTO log VALUES (DEFAULT, %s, %s, %s, %s)"
            data = (id, '시작', '시작', timestamp) #Prepared Statement 로 실행
            cur.execute(sql, data)
            conn.commit()
    conn.close() # 연결 종료
        
    