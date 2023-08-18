# 이 페이지는 사용가능한 시간 업데이트 페이지입니다.
import pymysql
import datetime 
from datetime import timedelta
from PyQt5.QtCore import QTimer,QDateTime


# db 정보
db_url = '101.79.10.48'
db_username= 'object'
db_port = 3308
db_password = 'object12!@'
db_name = 'object'


conn = None

time=QDateTime.currentDateTime() #현재 시간 가져오기
now =datetime.datetime.now()   #현재 시간 가져오기
# print(now + datetime.timedelta(hours=8)) #현재 시간에서 8시간 뒤
# print(now - datetime.timedelta(minutes=23)) #현재 시간 23분 
print(now+datetime.timedelta(hours=208))


def getConnection():
    global conn
    conn = pymysql.connect(host=db_url,user=db_username, port=db_port ,password=db_password, db=db_name, charset='utf8') # mysql 정보
    return conn

def usable_time_update(id):
    conn = getConnection() #디비연결하고
    cur = conn.cursor() #커서옮기고
    
    
    # 데이터베이스에서 현재 사용 시간 가져오기(int 형태로 변환)
    sql = "SELECT used_time FROM time WHERE id = %s"
    
    cur.execute(sql, (id,))
    row = cur.fetchone()
    
    db_used_time_str = str(row[0])
    db_used_hours, db_used_minutes, db_used_seconds = map(int, db_used_time_str.split(':'))
    
    # 맥스시간정의
    db_max_hours = 208
    db_max_minutes = 0
    db_max_seconds = 0
    
    if db_used_hours >= db_max_hours: #현재까지 사용한시간이 맥스보다 크거나 같을때
        cur = conn.cursor() #커서옮기고
        sql = "UPDATE time JOIN user ON time.id = user.id SET usable_time = 000000 WHERE id = %s"
        cur.execute(sql, (id,))
        conn.commit()
        conn.close()
        return
    else: #사용가능한시간이 남았을때
        db_max_hours = db_max_hours-1
        db_max_minutes = 59
        db_max_seconds = 60
        used_hour = db_max_hours-db_used_hours
        used_minute = db_max_minutes-db_used_minutes
        used_second = db_max_seconds-db_used_seconds
        
        if used_hour>=9: #사용가능한 시간이 9시간 이상일때,
            cur = conn.cursor() #커서옮기고
            sql = "UPDATE time JOIN user on time.id = user.id SET usable_time = 090000 WHERE user.id = %s" #사용가능한시간을 9시간으로 업뎃
            cur.execute(sql, (id,))
            conn.commit()
            conn.close()
            return
        else:#9시간이 안남았을때
            total_usable_time_str = "{:02d}:{:02d}:{:02d}".format(used_hour, used_minute, used_second)
            # 데이터베이스에서 총 사용가능한 시간 업데이트
            cur = conn.cursor() #커서옮기고
            sql = "UPDATE time JOIN user on time.id = user.id SET usable_time = %s WHERE id = %s"
            cur.execute(sql, (total_usable_time_str,id))
            conn.commit()
            conn.close()
            return
    
    
    
    
    
    
    
    
    