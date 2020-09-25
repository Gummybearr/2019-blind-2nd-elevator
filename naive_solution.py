import requests
import json

url = "http://34.121.119.42:8000/"

MAX_FLOOR = 25
MIN_FLOOR = 1
MAX_CAPACITY = 8
MAX_CALL = 200

PROBLEM = 1
ELEVATORS = 4

def start(user_key, problem_id, number_of_elevators):
    uri = url+'start/'+user_key+'/'+str(problem_id)+'/'+str(number_of_elevators)
    return requests.post(uri).json()

def oncalls(token):
    uri = url+'oncalls'
    headers = {'X-Auth-Token': token}
    return requests.get(uri, headers = headers).json()

def action(token, command):
    uri = url+'action'
    headers = {'X-Auth-Token': token}
    return requests.post(uri, headers = headers, json={'commands': command}).json()

class elevator:
    def __init__(self, eid=-1, status="STOPPED"):
        self.eid = eid
        self.status = status
        
def passenger_check(ret, idx):
    flag = 0
    for i in ret['elevators'][idx]['passengers']:
        if i['end']==ret['elevators'][idx]['floor']:
            flag = 1
    return flag

def passenger_include(ret, idx):
    plist = []
    for i in ret['elevators'][idx]['passengers']:
        if i['end']==ret['elevators'][idx]['floor']:
            plist.append(i['id'])
    return plist

def calls_check(ret, idx, dirs):
    flag = 0
    for ii in range(0, len(ret['calls'])):
        i = ret['calls'][ii]
        if visit[ii]==1:
            continue
        if i['start']==ret['elevators'][idx]['floor']:
            if dirs=='UP' and i['start']<=i['end']:
                flag = 1
            elif dirs=='DOWN' and i['start']>=i['end']:
                flag = 1
    return flag

def calls_include(ret, idx, dirs, MAX_CAPACITY):
    plist = []
    for ii in range(0, len(ret['calls'])):
        i = ret['calls'][ii]
        if len(plist)+len(ret['elevators'][idx]['passengers'])>=MAX_CAPACITY:
            continue
        if visit[ii]==1:
            continue
        if i['start']==ret['elevators'][idx]['floor']:
            if dirs=='UP' and i['start']<=i['end']:
                visit[ii]=1
                plist.append(i['id'])
            elif dirs=='DOWN' and i['start']>=i['end']:
                visit[ii]=1
                plist.append(i['id'])
    return plist

def patrol(ret, idx, MIN_FLOOR, MAX_FLOOR, MAX_CAPACITY):
    #최고층 케이스
    if ret['elevators'][idx]['floor']==MAX_FLOOR:
        status = ret['elevators'][idx]['status']
        #print("on the top")
        #멈추어야 함
        if status=="UPWARD":
            return {'elevator_id': idx, "command": "STOP"}
        #멈추었을 경우
        elif status=="STOPPED":
            #문 열어줘야 함
            if passenger_check(ret, idx)==1: 
                return {'elevator_id':idx, 'command': "OPEN"}
            elif len(ret['elevators'][idx]['passengers'])==MAX_CAPACITY:
                elevators[idx].status = "DOWN"
                return {'elevator_id': idx, "command": "DOWN"}
            elif calls_check(ret, idx, "DOWN")==1:
                return {'elevator_id':idx, 'command': "OPEN"}
            #내려가야 함
            else:
                elevators[idx].status = "DOWN"
                return {'elevator_id': idx, "command": "DOWN"}
        #문이 열렸을 경우
        else:#opened case
            #내려줘야 함
            if passenger_check(ret, idx)==1:
                return {'elevator_id': idx, "command": "EXIT", 'call_ids': passenger_include(ret, idx)}
            #태워줘야 함
            if len(ret['elevators'][idx]['passengers'])==MAX_CAPACITY:
                return {'elevator_id': idx, "command": "CLOSE"}
            if calls_check(ret, idx, "DOWN")==1:
                return {'elevator_id': idx, "command": "ENTER", "call_ids": calls_include(ret, idx, "DOWN", MAX_CAPACITY)}
            #문 닫아야 함
            else:
                return {'elevator_id': idx, "command": "CLOSE"}
    #최저층 케이스
    elif ret['elevators'][idx]['floor']==MIN_FLOOR:
        status = ret['elevators'][idx]['status']
        #print("at the bottom")
        #멈추어야 함
        if status=='DOWNWARD':
            return {'elevator_id': idx, "command": "STOP"}
        #멈추었을 경우
        elif status=="STOPPED":
            if passenger_check(ret, idx)==1: 
                return {'elevator_id':idx, 'command': "OPEN"}
            elif len(ret['elevators'][idx]['passengers'])==MAX_CAPACITY:
                elevators[idx].status = "UP"
                return {'elevator_id': idx, "command": "UP"}
            elif calls_check(ret, idx, "UP")==1:
                return {'elevator_id':idx, 'command': "OPEN"}
            #올라가야 함
            else:
                elevators[idx].status = "UP"
                return {'elevator_id': idx, "command": "UP"}
        #문이 열렸을 경우
        else: #if status=="OPENED":
            #내려줘야 함
            if passenger_check(ret, idx)==1:
                return {'elevator_id': idx, "command": "EXIT", 'call_ids': passenger_include(ret, idx)}
            if len(ret['elevators'][idx]['passengers'])==MAX_CAPACITY:
                return {'elevator_id': idx, "command": "CLOSE"}
            #태워줘야 함
            if calls_check(ret, idx, "UP")==1:
                return {'elevator_id': idx, "command": "ENTER", "call_ids": calls_include(ret, idx, "UP", MAX_CAPACITY)}
            #문 닫아야 함
            else:
                return {'elevator_id': idx, "command": "CLOSE"}
    else:
        #올라가는 케이스
        if elevators[idx].status=="UP":
            #print("going up")
            #올라가는 경우
            status = ret['elevators'][idx]['status']
            if status=="UPWARD":
                #세워야 됨
                if (passenger_check(ret, idx)==1):
                    return {'elevator_id': idx, "command": "STOP"}
                elif len(ret['elevators'][idx]['passengers'])==MAX_CAPACITY:
                    print("full capacity")
                    return {'elevator_id': idx, "command": "UP"}
                elif  (calls_check(ret, idx, "UP")==1):
                    return {'elevator_id': idx, "command": "STOP"}
                #그냥 가도 됨
                else:
                    return {'elevator_id': idx, "command": "UP"}
            #멈춘 경후
            elif status=="STOPPED":
                if passenger_check(ret, idx)==1: 
                    return {'elevator_id':idx, 'command': "OPEN"}
                elif len(ret['elevators'][idx]['passengers'])==MAX_CAPACITY:
                    elevators[idx].status = "UP"
                    return {'elevator_id': idx, "command": "UP"}
                elif calls_check(ret, idx, "UP")==1:
                    return {'elevator_id':idx, 'command': "OPEN"}
                #올라가야 함
                else:
                    return {'elevator_id': idx, "command": "UP"}
            #열린 경우
            else: #if status=="OPENED":
                #내려야 됨
                if passenger_check(ret, idx)==1:
                    return {'elevator_id': idx, "command": "EXIT", 'call_ids': passenger_include(ret, idx)}
                if len(ret['elevators'][idx]['passengers'])==MAX_CAPACITY:
                    return {'elevator_id': idx, "command": "CLOSE"}
                #태워줘야 함
                if calls_check(ret, idx, "UP")==1:
                    return {'elevator_id': idx, "command": "ENTER", "call_ids": calls_include(ret, idx, "UP", MAX_CAPACITY)}
                #문 닫아야 함
                else:
                    return {'elevator_id': idx, "command": "CLOSE"}      
        #내려가는 케이스
        else:
            #print("going down")
            #내려가는 경우
            status = ret['elevators'][idx]['status']
            if status=="DOWNWARD":
                #세워야 됨
                if (passenger_check(ret, idx)==1):
                    return {'elevator_id': idx, "command": "STOP"}
                if len(ret['elevators'][idx]['passengers'])==MAX_CAPACITY:
                    return {'elevator_id': idx, "command": "DOWN"}
                if  (calls_check(ret, idx, "DOWN")==1):
                    #print("should hot on board")
                    return {'elevator_id': idx, "command": "STOP"}
                else:
                    return {'elevator_id': idx, "command": "DOWN"}
            #멈춘 경후
            elif status=="STOPPED":
                #열어야 됨
                if (passenger_check(ret, idx)==1):
                    return {'elevator_id': idx, "command": "OPEN"}
                if len(ret['elevators'][idx]['passengers'])==MAX_CAPACITY:
                    return {'elevator_id': idx, "command": "DOWN"}
                if (calls_check(ret, idx, "DOWN")==1):
                    #print("calls exists")
                    return {'elevator_id': idx, "command": "OPEN"}
                #그냥 가도 됨
                else:
                    #print("no one calls and no one gettin on board")
                    return {'elevator_id': idx, "command": "DOWN"}
            #열린 경우
            else: #if status=="OPENED":
                #내려야 됨
                if passenger_check(ret, idx)==1:
                    return {'elevator_id': idx, "command": "EXIT", 'call_ids': passenger_include(ret, idx)}
                if len(ret['elevators'][idx]['passengers'])==MAX_CAPACITY:
                    return {'elevator_id': idx, "command": "CLOSE"}
                #태워줘야 함
                if calls_check(ret, idx, "DOWN")==1:
                    return {'elevator_id': idx, "command": "ENTER", "call_ids": calls_include(ret, idx, "DOWN", MAX_CAPACITY)}
                #문 닫아야 함
                else:
                    return {'elevator_id': idx, "command": "CLOSE"}      
                
user = 'tester'
problem = PROBLEM
count = ELEVATORS

ret = start(user, problem, count)
#print(ret)
token = ret['token']
#print(token)

elevators = []
for i in ret['elevators']:
    elevators.append(elevator(i['id'], "DOWN"))
    
ret = oncalls(token)
#print(ret)

ret = oncalls(token)
print(ret)

visit = []
while ret['is_end']==False:
    command = []
    visit = [0]*len(ret['calls'])
    for j in range(0, len(elevators)):
        command.append(patrol(ret, j, MIN_FLOOR, MAX_FLOOR, MAX_CAPACITY))
    #print(command)
    #print()
    action(token, command)
    ret = oncalls(token)
    print(ret['timestamp'])
