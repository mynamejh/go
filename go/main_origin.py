# 이페이지가 제일먼저 보일 페이지입니다.   앱 강제종료 했을때 현재 시스템강제종료안됨. 시간 다썼을때 강제종료는 가능
import sys
import time
import atexit
import os
import log_save
import used_time_save
import usable_time_update
import push_end_log
from PyQt5.QtWidgets import *
from PyQt5 import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtCore import QTimer,QDateTime
import pymysql
import webbrowser
from datetime import datetime

# db 정보
db_url = '101.79.10.48'
db_username= 'object'
db_port = 3308 # 
db_password = 'object12!@'
db_name = 'object'


conn = None
now = datetime.now()
def system_end():
    #os.system('shutdown -s -t 0')
    print('종료')
    
def getConnection():
    conn = pymysql.connect(host=db_url,user=db_username, port=db_port ,password=db_password, db=db_name, charset='utf8') # mysql 정보
    return conn

    
if __name__ == '__main__':
    
    class UserEmailApp(QWidget): #꾸미는창
        def __init__(self):
            super().__init__()
            # self.setWindowFlags(Qt.WindowTitleHint | Qt.WindowMaximizeButtonHint) # 창의 닫기와 최소화 비활성화
            self.date = QDate.currentDate()
            self.initUI()
            self.label = QLabel('지금 시간')
                       
            
        def initUI(self):
            self.timer_running = False # 타이머가 실행 중인지를 나타내는 플래그
            self.setGeometry(100, 100, 300, 200)
            self.setWindowTitle('이메일 입력(@포함)')
            self.email_label = QLabel('Email:', self)
            self.email_label.move(20, 30)

            self.email_input = QLineEdit(self)
            self.email_input.move(80, 30)
            self.email_input.resize(200, 25)

            self.submit_button = QPushButton('확인', self)
            self.submit_button.move(110, 80)
            self.submit_button.clicked.connect(self.on_submit)

            self.timer = QTimer(self)
            
            self.admin_button = QPushButton('관리자페이지', self)
            self.admin_button.move(110, 120)
            self.admin_button.clicked.connect(self.on_admin_submit)
            self.admin_button.setEnabled(True) #관리자페이지버튼 비활성화

            self.submit_button2 = QPushButton('연장신청',self)
            self.submit_button2.move(110, 100)
            self.submit_button2.clicked.connect(self.on_time_submit)
            

            # 테스트,,,
            

            
            self.timer_label = QLabel('남은시간:', self) 
            
            self.timer_label.move(50, 160)
            self.timer_label.setFixedWidth(200) 

        
        def showTime(self):
            time=QDateTime.currentDateTime() #현재 시간 가져오기
            timeDisplay=time.toString('yyyy-MM-dd hh:mm:ss dddd')
            self.label.setText(timeDisplay)  # 창에 시간 보여주기





        def on_submit(self):
            email = self.email_input.text()
            if email: #이메일있을때
                conn = getConnection() #디비연결해서
                cur = conn.cursor() #커서옮기고
                sql = "select * from user where email_id='"+email+"'" #입력한이메일 select SQL문 //모든 정보 찾고 커서 옮기기
                cur.execute(sql) #실행했을때
                row = cur.fetchone() # 한 줄씩 읽기
                    
                if row == None: #이메일이 없으면
                    QMessageBox.warning(self, '경고', '이메일아이디가 맞지않습니다.') #메세지 띄워주고
                else: #이메일이 있으면    
                    QMessageBox.warning(self, '성공', '타이머가 시작됩니다.') #메세지 띄워주고
                    self.timer_running = True  # 플래그를 True로 설정하여 타이머가 실행 중임을 나타냄
                    self.id = row[0] #이건 혹시나 쓰일까봐 넣어둔것
                    
                    #@@@@@@@여기부터 
                    sql = "select subject from log where num = (select max(num) from log where id = %s and (subject = '시작' or subject = '종료'))"#로그에서 시작,종료만 해당하는 num 젤큰거 가져와서;
                    cur.execute(sql, (self.id,)) #쿼리실행

                    row1 = cur.fetchone() #객체에 담아서 ex row1 = ('종료',) ('시작',)
                    print(row1)

                    if(row1[0] == '시작'): # 자 여기서 서버의 로그에서 시작또는 종료를 불러왔을때 마지막이 시작이면,
                        push_end_log.push_end_log(row[0]) #종료시간 강제로 넣기
                    #@@@@@@@@여기까지는 서버에 로그가 마지막이 종료가 아니면 강제로 종료집어넣을라고 운영체제의 종료시간을 불러온거임
                    
                    log_save.log_save(row[0]) #id
                    
                    if(row[5] == '관리자'): #관리자여부확인부
                        self.admin_button.setEnabled(True) #관리자페이지버튼 활성화
                    self.submit_button.setEnabled(False) #확인버튼 비활성화
                    
                    #사용가능한시간 업뎃하기
                    usable_time_update.usable_time_update(row[0])
                    
                    cur = conn.cursor() #커서옮기고
                    sql = "select usable_time from time join user on time.id = user.id where email_id ='"+email+"'"
                    cur.execute(sql) #실행했을때
                    result = cur.fetchone() #결과레코드저장
                    self.usable_time = result[0] #첫번째 값저장
                    usable_time = self.usable_time

                    # 데이터베이스에서 가져온 usable_time을 초로 변환
                    usable_time_seconds = int(usable_time.total_seconds())#이게1초인데
                    usable_time_milliseconds = int(usable_time_seconds * 1000)#왜밀리초로 다시바꾸는지 이해안됨 그래도일단해봄;
                    # 타이머 시작
                    
                    while True:
                        if usable_time_milliseconds > 0:
                            self.timer.setInterval(1000) #1초임
                            self.timer.start()
                            usable_time_milliseconds -= 1000 #1초임
                            self.usable_time_milliseconds=usable_time_milliseconds
                            self.display_time()
                            time.sleep(1)# sleep(1) => 입력한 초만큼 일시 정지 가능. (일정시간 정지하기)
                        else:
                            self.timer.stop()
                            self.timer_running = False  # 플래그를 False로 설정하여 타이머가 종료되었음을 나타냄
                            # log_save.log_save(row[0])
                            # used_time_save.used_time_save(row[0])
                            log_save.log_save(self.id)
                            used_time_save.used_time_save(self.id)
                            conn.close()
                            QMessageBox.warning(self, '종료', '타이머가 종료됩니다.') #메세지 띄워주고
                            return
                atexit.register(system_end())                            
            else: #안적었을때
                QMessageBox.warning(self, '경고', '이메일을 입력하세요.')

        def display_time(self):#사용은 하고싶으나 종료되었을때 시간만 뜨고 시간흐르는건 안뜸; 
            usable_time_milliseconds = self.usable_time_milliseconds

            # usable_time_milliseconds를 시간, 분, 초 단위로 분리
            seconds, milliseconds = divmod(usable_time_milliseconds, 1000)
            minutes, seconds = divmod(seconds, 60)
            hours, minutes = divmod(minutes, 60)

            # 시간, 분, 초 값이 0일 때는 '00'으로 표시하도록 포맷 지정자 수정
            self.timer_label.setText(now)
            # self.timer_label.setText(f'남은 시간: {hours:02d}:{minutes:02d}:{seconds:02d}')#여긴왜 안찍히지..


        def on_admin_submit(self):
            webbrowser.open('admin.html')

        def on_time_submit(self):
            webbrowser.open('admin.html') # test 용!
            
    #여기서부터 실행됨
    app = QApplication(sys.argv)
    window = UserEmailApp()
    window.setWindowModality(2)  # 모달 창 설정 (2: Qt.ApplicationModal)
    window.show()
    sys.exit(app.exec_())
    