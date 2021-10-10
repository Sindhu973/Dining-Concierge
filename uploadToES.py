from opensearchpy import OpenSearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth
import boto3
import json
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

with open('ES.json') as f:
    data = json.load(f)
    
for row in data:
    index_data = {
        'id' : row['id'],
        'cuisine' : row['cuisine']
    }

    search.index(index="restaurants", doc_type="Restaurant", id=row['id'], body=index_data )


#search.index(index="restaurants", type="Restaurant" )

#print(search.get(index="movies", doc_type="_doc", id="5"))


