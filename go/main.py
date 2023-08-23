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
    os.system('shutdown -s -t 0')
    print('종료')
    
def getConnection():
    conn = pymysql.connect(host=db_url,user=db_username, port=db_port ,password=db_password, db=db_name, charset='utf8') # mysql 정보
    return conn

    
if __name__ == '__main__':
    
   class WinForm(QWidget):
    def __init__(self):
        super().__init__()
        self.label = QLabel()
        self.setGeometry(100, 100, 300, 200)
        self.setWindowTitle('이메일 입력')
        self.email_label = QLabel('Email:', self)
        self.email_label.move(20, 30)


        self.email_input = QLineEdit(self)
        self.email_input.move(80,30)
        self.email_input.resize(200,25)

        


        self.listFile=QListWidget()
        self.label=QLabel('현재시간 확인')
        self.label.move(100,40)
        self.startBtn=QPushButton('Start')
        self.endBtn=QPushButton('Stop')
        self.submitBtn = QPushButton('확인',self)
        self.submitBtn.move(110,120)
        self.manageBtn = QPushButton('관리자용')
       

        layout=QGridLayout()

        self.timer=QTimer(self)
        self.timer.timeout.connect(self.showTime)

        layout.addWidget(self.submitBtn,0,1,2,1)
        layout.addWidget(self.startBtn,1,0)
        layout.addWidget(self.endBtn,1,1)
        layout.addWidget(self.manageBtn,1,2)

        self.startBtn.clicked.connect(self.startTimer)
        self.endBtn.clicked.connect(self.endTimer)
        self.submitBtn.clicked.connect(self.on_submit)
        self.manageBtn.clicked.connect(self.manageTimer)

        self.setLayout(layout)

    def showTime(self): # 시간이 왜 창에 안나올까...
        time=QDateTime.currentDateTime() #현재 시간 가져오기
        now = datetime.now()
        timeDisplay=time.toString('yyyy-MM-dd hh:mm:ss dddd')
        print(now)
        self.label.setText(timeDisplay)  # 창에 시간 보여주기

    def startTimer(self):
        self.timer.start(1000)
        self.startBtn.setEnabled(False)
        self.endBtn.setEnabled(True)

    def endTimer(self):
        self.timer.stop()
        self.startBtn.setEnabled(True)
        self.endBtn.setEnabled(False)

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
                #    os.system('shutdown -r -t 0') # 아이디 맞으면 종료됨.
                    self.timer_running = True  # 플래그를 True로 설정하여 타이머가 실행 중임을 나타냄
                    self.id = row[0] #이건 혹시나 쓰일까봐 넣어둔것 왜죠...?
                    # self.check_admin(self.id) : 되는지 확인,,
                      
                    #@@@@@@@여기부터 
                    sql = "select subject from log where num = (select max(num) from log where id = %s and (subject = '시작' or subject = '종료'))"#로그에서 시작,종료만 해당하는 num 젤큰거 가져와서;
                    cur.execute(sql, (self.id,)) #쿼리실행
                    row1 = cur.fetchone() #객체에 담아서 ex row1 = ('종료',) ('시작',)
                  

                    # 해당 id 의 시작값 없으면 시작 값 저장.
                    if (row1 is None or row1[0]=='종료'):  
                        log_save.log_save(row[0])
                        used_time_save.used(row[0])
                    else: # '시작' 값이 있으면 종료시간 강제로 넣기
                        if(row1[0] == '시작'): # 자 여기서 서버의 로그에서 시작
                            push_end_log.push_end_log(row[0]) #종료시간 강제로 넣기
                            

                    # if(row[5] == '관리자'): #관리자여부확인부
                    #     self.admin_button.setEnabled(True) #관리자페이지버튼 활성화
                    #     self.submit_button.setEnabled(False) #확인버튼 비활성화
                    
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

                        else:
                            self.timer.stop()
                            self.timer_running = False  # 플래그를 False로 설정하여 타이머가 종료되었음을 나타냄
                            log_save.log_save(row[0])
                            used_time_save.used_time_save(row[0])
                            log_save.log_save(self.id)
                            used_time_save.used_time_save(self.id)
                            conn.close()
                            QMessageBox.warning(self, '종료', '타이머가 종료됩니다.') #메세지 띄워주고
                            return
                atexit.register(system_end())                            
        else: #안적었을때
            QMessageBox.warning(self, '경고', '이메일을 입력하세요.')
    def check_admin(self, user_id):
        conn = getConnection()
        cur = conn.cursor()
        sql = "SELECT user_type FROM user WHERE id = %s"
        cur.execute(sql, (user_id,))
        user_type = cur.fetchone()[0]
        if user_type == '관리자':
            QMessageBox.information(self, '알림', f'{user_id} 관리자님 안녕하세요.')

    def manageTimer(self):
        self.check_admin(self.id)  # 관리자 여부 확인 및 메시지 출력
        webbrowser.open('admin.html')



if __name__ == '__main__':
    app=QApplication(sys.argv)
    form=WinForm()
    form.show()
    sys.exit(app.exec_())
