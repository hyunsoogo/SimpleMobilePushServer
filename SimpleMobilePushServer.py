from urllib.request import urlopen
from urllib.request import Request
import json, time, random, ssl, socket, struct

# For Android only...
URL_GCM = "https://android.googleapis.com/gcm/send"
GCM_SERVER_KEY = "PASTE_YOUR_GCM_KEY"
GCM_HEADERS = {'Content-Type': 'application/json', 'Authorization': 'key=%s' % GCM_SERVER_KEY}

# For IOS only...
CERT_FILE = "PASTE_YOUR_APNS_PEM_FILE"  # ex) "apns.pem"
URL_APNS = ('gateway.sandbox.push.apple.com', 2195)
# use 'gateway.push.apple.com' instead after releasing your ios app

MAX_RETRIES = 10 # edit as you want

def sendPushForAndroid(ids, data):
    # if ids is empty, stop sending
    if len(ids) == 0:
        return

    # this is for random collapse key. Delete this code if you don't want
    collapse_key = random.choice('abcdefghijklmnopqrstuvwxyz') \
                   + str(random.randrange(1,10000))

    # split ids if the number of ids is more than 1000
    splitedRegidIds = chunks(ids,1000)

    for ids in splitedRegidIds:
        msg = {
                "collapse_key" : collapse_key, 
                "data" : data,
                "delay_while_idle" : False, 
                "time_to_live" : 3600, 
                "registration_ids": regidIds
        }
        data = json.dumps(msg).encode('utf-8')
        req = Request(URL_GCM, data, GCM_HEADERS)
        f = urlopen(req)
        response = json.loads(f.read().decode('utf-8'))
        print(response)            

def chunks(l, n):
    n = max(1, n)
    return [l[i:i + n] for i in range(0, len(l), n)]

def sendPushForIOS(tokens, data):
    # if ids is empty, stop sending
    if len(tokens) == 0:
        return
    
    msg = json.dumps(
        {
            'aps': {
                'alert': data,
                'badge': 0,
                'sound': 'default'
                }
            })

    for token in tokens:
        byteToken = bytes.fromhex(token)
        length = len(msg)
        fmt = "!BH32sH%ds" % len(msg)
        notification = struct.pack(fmt, 0, 32, byteToken, len(msg), msg.encode())
        try:
            sock.write(notification)
            savePushToServer(token,dc)
        except:
            reconnectAPNS()
            sock.write(notification)
                
def reconnectAPNS():
    global sock
    sock.close()
    for _ in range(MAX_RETRIES):
        try:
            s = socket.socket()
            sock = ssl.wrap_socket(s, ssl_version=ssl.PROTOCOL_TLSv1, certfile=CERT_FILE)
            sock.connect(URL_APNS)
            break
        except Exception as e:
            print("Error at reconnectAPNS: " + str(e))
            time.sleep(1)
     
if __name__ == "__main__":
    
    # Use a socket to connect to APNS over SSL
    s = socket.socket()
    sock = ssl.wrap_socket(s, ssl_version=ssl.PROTOCOL_TLSv1, certfile=CERT_FILE)
    sock.connect(URL_APNS)

    # prepare data (edit key & value as you want)
    data = { 
            "key_1": "value_1", 
            "key_2": "value_2",
            "key_3": "value_3",
    }

    # you should get proper tokens(ios) or registration ids(android) from database
    ids_ios = ["USER_TOKEN_1","USER_TOKEN_2", ... ]
    ids_android = ["USER_REGISTRATION_ID_1","USER_REGISTRATION_ID_2", ... ] 

    # send push
    sendPushForIOS(ids_ios, data)
    sendPushForAndroid(ids_android, data)
