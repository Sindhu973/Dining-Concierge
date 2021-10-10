import math
import dateutil.parser
import datetime
import time
import os
import logging
import boto3
from botocore.exceptions import ClientError
import json
import string

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


def get_slots(intent_request):
    return intent_request['currentIntent']['slots']


def elicit_slot(session_attributes, intent_name, slots, slot_to_elicit, message):
    return {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'ElicitSlot',
            'intentName': intent_name,
            'slots': slots,
            'slotToElicit': slot_to_elicit,
            'message': message
        }
    }


def close(session_attributes, fulfillment_state, message):
    response = {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'Close',
            'fulfillmentState': fulfillment_state,
            'message': message
        }
    }

    return response


def delegate(session_attributes, slots):
    return {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'Delegate',
            'slots': slots
        }
    }

def parse_int(n):
    try:
        return int(n)
    except ValueError:
        return float('nan')


def build_validation_result(is_valid, violated_slot, message_content):
    if message_content is None:
        return {
            "isValid": is_valid,
            "violatedSlot": violated_slot,
        }

    return {
        'isValid': is_valid,
        'violatedSlot': violated_slot,
        'message': {'contentType': 'PlainText', 'content': message_content}
    }


def isvalid_date(date):
    try:
        dateutil.parser.parse(date)
        return True
    except ValueError:
        return False
        
def validate_loc(loc):
    return loc.lower() == "manhattan"


def validate_dining(cuisine, date,diningTime,location,noOfPeople,phoneNumber):
    print("VALIDATE DINING")
    cuisines = ['chinese', 'american', 'mexican','korean','japanese','italian','french']
    if cuisine is not None and cuisine.lower() not in cuisines:
        print("INSIDE CUISINE")
        return build_validation_result(False,'cuisine', 'We do not have {}, would you like a different type of cusine? Our most popular cusine is chinese'.format(cuisine))

    if date is not None:
        if not isvalid_date(date):
            return build_validation_result(False, 'date', 'I did not understand that, what date would you like to reserve the restaurant?')
        elif datetime.datetime.strptime(date, '%Y-%m-%d').date() <= datetime.date.today():
            return build_validation_result(False, 'date', 'You can reserve the restaurant from tomorrow onwards.  What day would you like to reserve?')

    if diningTime is not None:
        if len(diningTime) != 5:
            # Not a valid time; use a prompt defined on the build-time model.
            return build_validation_result(False, 'reserve_time', None)

        hour, minute = diningTime.split(':')
        hour = parse_int(hour)
        minute = parse_int(minute)
        if math.isnan(hour) or math.isnan(minute):
            # Not a valid time; use a prompt defined on the build-time model.
            return build_validation_result(False, 'reserve_time', None)

        if hour < 10 or hour > 16:
            # Outside of business hours
            return build_validation_result(False, 'Time', 'Our business hours are from ten a m. to five p m. Can you specify a time during this range?')
    if location is not None:
        if not validate_loc(location):
            return build_validation_result(False,'Location','You can only reserve restaurants in Manhattan now')

    return build_validation_result(True, None, None)


def diningsuggestionslf1(intent_request):
    cuisine = get_slots(intent_request)["cuisine"]
    date = get_slots(intent_request)["date"]
    diningTime = get_slots(intent_request)["diningTime"]
    location = get_slots(intent_request)["location"]
    noOfPeople = get_slots(intent_request)["noOfPeople"]
    email = get_slots(intent_request)["email"]
    source = intent_request['invocationSource']
    if source == 'DialogCodeHook':
        print("INSIDE CODE ")
        slots = get_slots(intent_request)
        valid_thing = validate_dining(cuisine, date,diningTime,location,noOfPeople,phoneNumber)
        if not valid_thing['isValid']:
            slots[valid_thing['violatedSlot']] = None
            return elicit_slot(intent_request['sessionAttributes'],
                              intent_request['currentIntent']['name'],
                              slots,
                              valid_thing['violatedSlot'],
                              valid_thing['message'])

        output_session_attributes = intent_request['sessionAttributes'] if intent_request['sessionAttributes'] is not None else {}
        return delegate(output_session_attributes, get_slots(intent_request))
    
    sqs_client = boto3.client('sqs')
    sqs_url = 'https://sqs.us-west-2.amazonaws.com/195749205458/DiningSQS'
    msg_info = {"cuisine": cuisine, "date": date, "diningTime": diningTime, "location":location,"noOfPeople":noOfPeople,"email":email}
    print("message to sent is {}".format(msg_info))
    try:
        response = sqs_client.send_message(QueueUrl=sqs_url,
                                      MessageBody=json.dumps(msg_info))
        print(response)
    except ClientError as e:
        logging.error(e)
        return None
    return close(intent_request['sessionAttributes'],
                 'Fulfilled',
                 {'contentType': 'PlainText',
                  'content': "You’re all set. Expect my suggestions shortly! Have a good day."})
                  
                  
def thankyoulf1(intent_request):
    output_session_attributes = intent_request['sessionAttributes'] if intent_request['sessionAttributes'] is not None else {}
    return close(output_session_attributes,'Fulfilled',{'contentType': 'PlainText','content': "You're welcome!"})
    
def greetinglf1(intent_request):
    response = {
        "dialogAction": {
            "type": "Close",
            "fulfillmentState": "Fulfilled",
            "message": {
                "contentType": "PlainText",
                "content": "Hi there, how can I help?"
            }
        }
    }
    return response
    
    
def dispatch(intent_request):
    logger.debug('dispatch userId={}, intentName={}'.format(intent_request['userId'], intent_request['currentIntent']['name']))

    intent = intent_request['currentIntent']['name']
    if intent == 'DiningSuggestionsIntent':
        return diningsuggestionslf1(intent_request)
    elif intent == 'ThankYouIntent':
        return thankyoulf1(intent_request)
    elif intent == 'GreetingIntent':
        return greetinglf1(intent_request)
        
        
    
def lambda_handler(event, context):
    print(event)
    print(context)
    os.environ['TZ'] = 'America/New_York'
    time.tzset()
    logger.debug('event.bot.name={}'.format(event['bot']['name']))
    
    return dispatch(event)
