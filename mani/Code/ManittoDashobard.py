# Import packages
from dash import Dash, html, dash_table, dcc, callback, Output, Input, ctx
import pandas as pd
import numpy as np
import warnings
from collections import deque
import smtplib
from email.mime.text import MIMEText
import dash_bootstrap_components as dbc
warnings.filterwarnings('ignore')


##################################################
# functions
def bfs_for_manitto(k, manittodict):
    q = deque([[0, 1]])
    visit = [0 for _ in range(k)]
    while q:
        sample_num, cnt = q.popleft()
        visit[sample_num] = 1
        next_num = manittodict[sample_num]
        if visit[next_num] == 0:
            q.append([next_num, cnt+1])

    return cnt

def manitto_select_complete_shuffle(n):
    num = [c for c in range(n)]
    reset = 0
    while True:
        reset += 1
        sample = np.random.choice(num, size=n, replace = False)
        manittodict = {n:s for n, s in zip(num, sample)}
        k = bfs_for_manitto(n, manittodict)
        if k == n:
            break
            
    return reset, list(manittodict.values())

def manitto_select(n):
    num = [c for c in range(n)]
    reset = 0
    while True:
        reset += 1
        sample = np.random.choice(num, size=n, replace = False)
        if all(s != n for s, n in zip(sample, num)):
            break
            
    manittodict = {n:s for n, s in zip(num, sample)}
    
    return reset, list(manittodict.values())

def manitto_option(names, complete = False):
    n = len(names)
    if complete:
        cnt, angel = manitto_select_complete_shuffle(n)
        
    else:
        cnt, angel = manitto_select(n)
    
    print(cnt, "회 반복하였습니다.")
    
    select_manitto = [names[k] for k in angel]
    
    return select_manitto

def create_dataset(load_data, comp):
    load_data['manitto'] = manitto_option(load_data['name'], complete = comp)
    return load_data

def mail_sending(titles, smtpName, smtpPort, sendEmail, password, host, load_data, price):
    for i in range(len(load_data)):
        # 메일 내용
        title = titles                               
        content = f"""
===============================================
                        스포 방지선
===============================================

#####################################################
host {host}: {load_data['name'][i]}님! 마니또 선물 교환식 참여에
             응해주셔서 감사합니다. 저희 마니또 진행 방식의 규칙은
             다음과 같습니다.

                        ! Rule !

        1. 해당되는 사람에게 없을 것 같은 물건
        2. 가격대는 {str(price)}원 이하로 선정
        3. 만약, 해당되는 사람이 가지고 있는 물건일 경우 벌칙을
           받습니다.

host {host}: {load_data['name'][i]}님은 다음과 같은 사람의 마니또로 
             선정되셨습니다. 심사숙고하셔서 벌칙을 면해봅시다!

        
        ********************************************
               준비해야 하는    상대       
                      {load_data['manitto'][i]}   
        ********************************************


                            
                            ★
                            ''        
                           ****
                          ''''''
                         ********
                        ''''''''''
                       ************
                      ''''''''''''''
                     ****************
                            ||
                            ||
                            ||
                 
                 #   Merry Christmas!   #
#####################################################

"""
        msg = MIMEText(content)
        msg['From'] = sendEmail
        msg['To'] = load_data['email'][i]
        msg['Subject'] = title

        s = smtplib.SMTP(smtpName , smtpPort)
        s.starttls()
        s.login(sendEmail , password)
        s.sendmail(sendEmail, load_data['email'][i], msg.as_string())
        s.close()

###################################################

# Used data
data = pd.DataFrame({'name':[],
                     'email':[]})

###################################################

# need variables
smtpName = "smtp.naver.com"
smtpPort = 587

###################################################

# Dashboard
app = Dash(external_stylesheets=[dbc.themes.LUX])

# App layout
app.layout = dbc.Container([
    html.Br(),

    dbc.Row([
        html.H1(children='마니또 추첨 대시보드')
    ]),

    dbc.Row([
        html.Hr()
    ]),

    dbc.Row([
        html.H3(children='주의사항')
    ]),

    dbc.Row([
        html.Label('Data 폴더에 Sending_players.csv 파일이 존재해야 합니다.')
    ]),

    dbc.Row([
        html.Hr()
    ]),
    
    dbc.Row([
        html.H5(' Sending_players가 있는 디렉토리를 입력하세요')
            ]),

    dbc.Row([
        dcc.Input(value='./mani/Data/', type='text',
                    id = 'directory')
    ]),
    
    dbc.Row([
        html.Button('Submit', id='submit_dir', n_clicks=0)    
    ]),

    dbc.Row([
        html.Div(id='select_dir',
                children='Submit 버튼을 눌러주세요')   
    ]),
    
    dbc.Row([
        html.Hr()
    ]),

    dbc.Row([
        dbc.Col([

            dbc.Row([
                html.Label('네이버 이메일을 입력하세요')
            ]),
            dbc.Row([
                dcc.Input(value='****@naver.com', type='text',
                          id = 'email_address')
            ]),
            html.Br(),

            dbc.Row([
                html.Label('비밀번호를 입력하세요')
            ]),
            dbc.Row([
                dcc.Input(value='*********', type='password',
                          id = 'email_password')
            ]),
            html.Br(),

            dbc.Row([
                html.Label('호스트의 이름을 입력하세요')
            ]),
            dbc.Row([
                dcc.Input(value='1043', type='text',
                          id = 'host_name')
            ]),
            html.Br(),

            dbc.Row([
                html.Label('가격을 설정하세요(원)')
            ]),
            dbc.Row([
                dcc.Input(value='20000', type='text',
                          id  = 'price')
            ]),
            html.Br(),

            dbc.Row([
                html.Label('메일 제목을 입력하세요')
            ]),
            dbc.Row([
                dcc.Input(value='121523 마니도 추첨 초대장',
                           type='text', id = 'mail_title')
            ]),
            html.Br(),

            dbc.Row([
                html.Label('셔플에서 섬이 생기는 것을 금지 할지 선택해주세요 ex) [1, 3], [2, 4, 5] ')
            ]),
            dbc.Row([
                dcc.RadioItems(['False', 'True'],
                           'False', id = 'complete_shuffled')
            ]),
            html.Br(),
        ]),
    ]),


    dbc.Row([
        html.Button('Submit', id='submit_value', n_clicks=0)    
    ]),

    dbc.Row([
        html.Div(id='select_submit',
                    children='submit 버튼을 눌러주세요')   
    ]),

])

# Add controls to build the interaction
@callback(
    Output('select_dir', 'children'),
    Input('submit_dir', 'n_clicks'),
    Input('directory', 'value')
)
def displayClick(clk, dir):
    if "submit_dir" == ctx.triggered_id:
        try:
            d = pd.read_csv(dir+'Sending_players.csv')
            global data
            data = d
            return '데이터 불러오기에 성공하였습니다.'
        
        except:
            return '데이터 불러오기에 실패하였습니다.'

@callback(
    Output('select_submit', 'children'),
    Input('submit_value', 'n_clicks'),
    Input('email_address', 'value'),
    Input('email_password', 'value'),
    Input('host_name', 'value'),
    Input('price', 'value'),
    Input('mail_title', 'value'),
    Input('complete_shuffled', 'value')
)
def send_email_yesno(send, sendEmail,
                      password, host,
                        price, titles, buttons):
    
    if "submit_value" == ctx.triggered_id:
        try:
            mail_sending(titles, smtpName,
                        smtpPort, sendEmail,
                            password, host,
                            create_dataset(data, buttons), price)

            return '메일 전송을 완료하였습니다!'
    
        except:
            return '메일 전송에 실패하였습니다...'

if __name__ == '__main__':
    app.run(debug=True)