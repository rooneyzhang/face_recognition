import redis
import json

r = redis.Redis(host='111.1.13.42', port=6379, db=0, password='3L3ygScS')
i=0
while i<10:
    msg='''{
        "code": 0,
        "persons": [{
            "type": 0,
            "name": "张三%s",
            "department": "技术部",
            "position": "员工",
            "employeeID":%s,
            "image": "./static/face/%s.jpg"
        }],
        "camera": [{
            "id": "1",
            "position": "position"
        }]
    }
    '''  %(str(i),str(1000+i),str(1000+i))
    r.lpush("face",msg)
    i=i+1


msg= r.rpop("face")
if msg:
    data=json.loads(str(msg.decode()))
    if type(data) is dict:
        print(str(data["persons"]))
        person = data["persons"][0]
        #person = json.loads(str(data["persons"]))
        print(person["type"])
        print(person["name"])
        print(person["department"])
        print(person["position"])
        print(person["employeeID"])
        print(person["image"])
else :
    print("nothing")