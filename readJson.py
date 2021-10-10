import json
import boto3
import datetime
from decimal import Decimal

dynamodb = boto3.resource('dynamodb', region_name='us-west-2')
table = dynamodb.Table('yelp-restaurants')

list = [];

filenames = ['vietnamese0.json', 'thai0.json', 'cuban0.json','greek0.json','swedish0.json','british0.json','middle eastern0.json']#['american0.json','mexican0.json', 'italian0.json', 'chinese0.json', 'french0.json', 'indian0.json', 'japanese0.json', 'korean0.json']

for filename in filenames:
    with open(filename) as f:
        data = json.load(f)
    for row in data:
        row['insertedAtTimestamp'] = str(datetime.datetime.now())
        row['rating'] = Decimal(str(row['rating']))
        row['review_count'] = int(row['review_count'])
        row['coordinates']['latitude'] = Decimal(str(row['coordinates']['latitude']))
        row['coordinates']['longitude'] = Decimal(str(row['coordinates']['longitude']))

        table.put_item(  Item=row )
            #print(row)

            
            

            





