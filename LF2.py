from opensearchpy import OpenSearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth
import requests
import boto3
import json
from boto3.dynamodb.conditions import Key

def lambda_handler(event, context):
    
    
    sqs = boto3.client('sqs')

    queue_url = 'https://sqs.us-west-2.amazonaws.com/195749205458/DiningSQS'
    
    # Receive message from SQS queue
    response = sqs.receive_message(
        QueueUrl=queue_url,
        AttributeNames=[
            'SentTimestamp'
        ],
        MaxNumberOfMessages=1,
        MessageAttributeNames=[
            'All'
        ],
        VisibilityTimeout=0,
        WaitTimeSeconds=0
    )
    
    message = json.loads(response['Messages'][0]['Body'])
    receipt_handle = response['Messages'][0]['ReceiptHandle']
    
    #print(message)
    
    cuisine = message['cuisine']
    cuisine = cuisine.lower()
    date = message['date']
    time = message['diningTime']
    location = message['location']
    email = message['email']
    noOfPeople = message['noOfPeople']
    
    messageToSend = 'Hello! Here are my {cuisine} restaurant suggestions in {location} for {numPeople} people, for {diningDate} at {diningTime}: '.format(
            cuisine=cuisine,
            location=location,
            numPeople=noOfPeople,
            diningDate=date,
            diningTime=time,
        )
    
    
    # Delete received message from queue
    sqs.delete_message(
        QueueUrl=queue_url,
        ReceiptHandle=receipt_handle
    )
    print('Received and deleted message: %s' % message)
    
    
    
    #https://search-diningconcierge-phgosfnnpcy5wa3enznv2wukha.us-west-2.es.amazonaws.com
    host = 'search-diningconcierge-phgosfnnpcy5wa3enznv2wukha.us-west-2.es.amazonaws.com' # For example, my-test-domain.us-east-1.es.amazonaws.com
    region = 'us-west-2'
    
    service = 'es'
    credentials = boto3.Session().get_credentials()
    awsauth = AWS4Auth(credentials.access_key, credentials.secret_key, region, service, session_token=credentials.token)
    
    search = OpenSearch(
        hosts = [{'host': host, 'port': 443}],
        http_auth = awsauth,
        use_ssl = True,
        verify_certs = True,
        connection_class = RequestsHttpConnection
    )
    
    criteria = {
            "query": { "match": {'cuisine': cuisine} },
        }
    
    res = search.search(index="restaurants", doc_type="Restaurant",body=criteria)
    
    content = res['hits']['hits']
    ids = []
    
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('yelp-restaurants')
    
    i = 1
    
    for entry in content:
        id = entry['_id']
        response = table.query(
        KeyConditionExpression=Key('id').eq(id)
        )
        
        item = response['Items'][0]
        name = item["name"]
        address = item["address"]
        restaurantMsg = '' + str(i) + '. '
        restaurantMsg += name +', located at ' + address +'. '
        messageToSend += restaurantMsg
        
        i = i+1
        
        if(i==4):
            break
        
    print(messageToSend)
    
    
    # Create a new SES resource and specify a region.
    ses = boto3.client('ses',region_name='us-west-2')
    response = ses.send_email(
    Source='sb8019@nyu.edu',
    Destination={
        'ToAddresses': [
            email,
        ],
    },
    Message={
        'Body': {
            'Text': {
                'Charset': 'UTF-8',
                'Data':messageToSend,
            },
        },
        'Subject': {
            'Charset': 'UTF-8',
            'Data': 'Restaurant Suggestions',
        },
    }
    )
        
        
   
        
    
        