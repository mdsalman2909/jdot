import os
import json
import requests

from slackeventsapi import SlackEventAdapter
from slackclient import SlackClient

# Our app's Slack Event Adapter for receiving actions via the Events API
slack_signing_secret = os.environ["SLACK_SIGNING_SECRET"]
slack_events_adapter = SlackEventAdapter(slack_signing_secret, "/slack/events")

# Create a SlackClient for your bot to use for Web API requests
slack_bot_token = os.environ["SLACK_BOT_TOKEN"]
slack_client = SlackClient(slack_bot_token)

#REST call constants
JARVIS_URL = "https://jarvis.eng.nutanix.com"

def create_fvm_request_body(jarvis_reponse):
  """
  Creates fvm request body from jarvis response
  """
  request_body = {}
  request_body['cvm_gateway'] = jarvis_reponse['network']['default_gw']
  request_body['ipmi_user'] = jarvis_reponse['power_mgmt']['ipmi']['user']
  request_body['blocks'] = jarvis_reponse['']
  request_body['hypervisor_gateway'] = jarvis_reponse['network']['default_gw']
  request_body['ipmi_netmask'] = jarvis_reponse.get(jarvis_reponse['ipmi']['netmask'], jarvis_reponse['network']['svm_subnet_mask'])
  request_body['hypervisor_netmask'] = jarvis_reponse['']
  request_body['cvm_netmask'] = jarvis_reponse['']
  request_body['nos_package'] = jarvis_reponse['']
  request_body['hypervisor_iso'] = jarvis_reponse['']
  request_body['ipmi_password'] = jarvis_reponse['']
  request_body['clusters'] = jarvis_reponse['']
  request_body['hypervisor_ntp_servers'] = jarvis_reponse['']
  request_body['ipmi_gateway'] = jarvis_reponse['']
  request_body['hypervisor_nameserver'] = jarvis_reponse['']
  

# Example responder to greetings
@slack_events_adapter.on("message")
def handle_message(event_data):
    message = event_data["event"]
    # If the incoming message contains "hi", then respond with a "Hello" message
    message_text = message.get('text')
    print "message_text:", message_text
    if message.get("subtype") is None and 'get cluster' in message_text:
          channel = message["channel"]
          cluster_name = message_text.split()[3]
          request_url = JARVIS_URL + '/api/v1/nodes/' + cluster_name
          resp = requests.get(request_url, verify=False).json()
          #response = "SVM_IP: " + resp['data']['svm_ip'] +"\n" + "SVM_VERSION: " + resp['data']['svm_version']
          slack_client.api_call("chat.postMessage", channel=channel, text=resp)

    elif message.get("subtype") is None and 'image nodes' in message_text and '--help' in message_text:
              print "message_text:", message_text
              print len(message_text)
              channel = message["channel"]
              command = "image nodes <node1> <node2> AOS=<AOS_VERSION> AOS_URL=<AOS_URL> HYP_TYPE=<TYPE> HYP_URL=<URL>\n"
              example = 'Example:\n\t image nodes catania6-1 AOS="master" AOS_URL="http://10.40.64.33/builds/nos-builds/master/0cf155f7f53c23057bed1fa54a5c2c4ddd3febb1/release/tar/nutanix_installer_package-release-master-0cf155f7f53c23057bed1fa54a5c2c4ddd3febb1.tar.gz" HYP_TYPE="AHV"'
              response = command + example 
              slack_client.api_call("chat.postMessage", channel=channel, text=response)

    elif message.get("subtype") is None and 'image nodes' in message_text and '--help' not in message_text:
              channel = message["channel"]
              arguments = message_text.split()[3:]
              args_list = []
              kwargs_dict = {}
              for arg in arguments:
                  if '=' not in arg:
                       args_list.append(arg)
                  else:
                       kwargs_dict[arg.split('=')[0]] = arg.split('=')[1]
              print args_list, kwargs_dict
              response = 'Command executed on: ' + message_text.split()[3]
              result = slack_client.api_call("chat.postMessage", channel=channel, text=response)
              if result['ok']:
                print ''
                
"""
    elif message.get("subtype") is None and 'create cluster' not in message_text:
              print "message_text:", message_text
              print len(message_text)
              channel = message["channel"]
              cluster_name = message_text.split()[3]
              jarvis_request_url = JARVIS_URL + '/api/v1/nodes/' + cluster_name
              print jarvis_request_url
              jarvis_response = requests.get(jarvis_request_url, verify=False)
              jarvis_response = jarvis_response.json()
              request_body = create_fvm_request_body(jarvis_response['data'])
              fvm_request_url = requests.post()
              slack_client.api_call("chat.postMessage", channel=channel, text=message)
"""

# Example reaction emoji echo
@slack_events_adapter.on("reaction_added")
def reaction_added(event_data):
    event = event_data["event"]
    emoji = event["reaction"]
    channel = event["item"]["channel"]
    text = ":%s:" % emoji
    slack_client.api_call("chat.postMessage", channel=channel, text=text)

# Error events
@slack_events_adapter.on("error")
def error_handler(err):
    print("ERROR: " + str(err))

# Once we have our event listeners configured, we can start the
# Flask server with the default `/events` endpoint on port 3000
slack_events_adapter.start(port=3004)
