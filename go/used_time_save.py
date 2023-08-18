# 이 페이지는 사용한 시간을 계산해서 업데이트 하는 페이지입니다. 정상적으로 9시간후에 종료되었을때 used_time 제대로 계산됨 컴퓨터 강제종료했을때는 계산안됨..

import pymysql
from datetime import datetime, timedelta

# db 정보
db_url = '101.79.10.48'
db_username= 'object'
db_port = 3308 
db_password = 'object12!@'
db_name = 'object'





conn = None 



def getConnection():
    global conn
    conn = pymysql.connect(host=db_url,user=db_username, port=db_port ,password=db_password, db=db_name, charset='utf8') # mysql 정보
    return conn

def used_time_save(id):#사용한 시간 계산하기
    # 한달마다 업뎃해줘야하기 때문에 여기서 if로 한번해줘야함
    # 어제날짜 월이랑 오늘날짜 월이랑 비교했을때 다르면 한달 지났다는 뜻
    # 다르면 총 사용 시간을 00:00:00 으로 업뎃한다음  아래 코드 실행할 것
    
    conn = getConnection() #디비연결하고
    cur = conn.cursor()

    # 시작 시간 가져오기
    sql = "SELECT * FROM log WHERE id = %s AND subject = '시작' ORDER BY num DESC LIMIT 1" #로그에서 시작만 해당하는 num 젤큰거 가져와서
    cur.execute(sql, (id,)) # 쿼리실행
    row = cur.fetchone() #변수에 담아서 ,현재는 '시작'의 시간
    start_time = row[0] # 따로담고
    
    # 종료 시간 가져오기
    sql = "SELECT * FROM log WHERE id = %s AND subject = '종료' ORDER BY num DESC LIMIT 1" #로그에서 종료만 해당하는 num 젤큰거 가져와서
    cur.execute(sql, (id,))
    row = cur.fetchone() #변수에 담아서 ,현재는 '종료'의 시간
    end_time = row[0]



    # 데이터베이스에서 현재 사용 시간 가져오기(int 형태로 변환)
    sql = "SELECT used_time FROM time WHERE id = %s"
    cur.execute(sql, (id,))
    row = cur.fetchone()
    #db_used_time_str = str(row[0])
    db_used_time_str = row[0]
    db_hours, db_minutes, db_seconds = map(int, db_used_time_str.split(':'))
    
    
    # 총 사용 시간 계산
    total_hours = db_hours + used_time_hours
    total_minutes = db_minutes + used_time_minutes
    total_seconds = db_seconds + used_time_seconds

    # 사용 시간 계산 (시간 계산 다시!! 해야함!)
    used_time_timedelta = end_time - start_time
    #used_time_seconds = used_time_timedelta.total_seconds()
    used_time_seconds = used_time_timedelta-datetime.timedelta(minutes=23)    
    used_time_hours = int(used_time_seconds // 3600)
    used_time_minutes = int((used_time_seconds % 3600) // 60)
    used_time_seconds = int(used_time_seconds % 60)


    
    # 분과 초가 60 이상인 경우 시간으로 환산
    if total_seconds >= 60:
        total_minutes += int(total_seconds // 60)
        total_seconds = total_seconds % 60

    if total_minutes >= 60:
        total_hours += int(total_minutes // 60)
        total_minutes = total_minutes % 60
        
    total_used_time_str = "{:02d}:{:02d}:{:02d}".format(total_hours, total_minutes, total_seconds)

    # 데이터베이스에서 총 사용 시간 업데이트
    sql = "UPDATE time SET used_time = %s WHERE id = %s"
    cur.execute(sql, (total_used_time_str, id))
    conn.commit()
    conn.close()