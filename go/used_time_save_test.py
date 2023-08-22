
import pymysql
import datetime

def getConnection():
    global conn
    conn = pymysql.connect(host=db_url, user=db_username, port=db_port, password=db_password, db=db_name, charset='utf8')
    return conn

def update_used_time(id):
    conn = getConnection()
    cur = conn.cursor()

    # 시작 시간 가져오기
    sql = "SELECT * FROM log WHERE id = %s AND subject = '시작' ORDER BY num DESC LIMIT 1"
    cur.execute(sql, (id,))
    start_row = cur.fetchone()
    start_time = start_row[0]

    # 종료 시간 가져오기
    sql = "SELECT * FROM log WHERE id = %s AND subject = '종료' ORDER BY num DESC LIMIT 1"
    cur.execute(sql, (id,))
    end_row = cur.fetchone()
    end_time = end_row[0]

    # 사용 시간 계산
    used_time_timedelta = end_time - start_time
    used_time_seconds = used_time_timedelta.total_seconds()
    used_time_hours = int(used_time_seconds // 3600)
    used_time_minutes = int((used_time_seconds % 3600) // 60)
    used_time_seconds = int(used_time_seconds % 60)

    # 데이터베이스에서 현재 사용 시간 가져오기
    sql = "SELECT used_time FROM time WHERE id = %s"
    cur.execute(sql, (id,))
    db_used_time_str = cur.fetchone()[0]
    db_hours, db_minutes, db_seconds = map(int, db_used_time_str.split(':'))

    # 총 사용 시간 계산
    total_hours = db_hours + used_time_hours
    total_minutes = db_minutes + used_time_minutes
    total_seconds = db_seconds + used_time_seconds

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

    # 한 달이 지난 경우 사용 시간 리셋
    now = datetime.datetime.now()
    if now.day == 1 and now.hour >= 16:  # 16시 이후에 1일인 경우 한 달 사용 시간 체크
        if total_hours >= 208:
            total_used_time_str = "00:00:00"  # 사용 시간 리셋
            sql = "UPDATE time SET used_time = %s WHERE id = %s"
            cur.execute(sql, (total_used_time_str, id))

    # 로그 저장
    sql = "INSERT INTO log (time, id, subject) VALUES (%s, %s, %s)"
    cur.execute(sql, (end_time, id, '종료'))

    conn.commit()
    conn.close()


user_id = 123  # 사용자 ID 입력
update_used_time(user_id)
