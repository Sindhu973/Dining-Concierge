import requests
import json
import sys
import time

# API_KEY = '6-dnnwPsU_ZD3n5riURfLONj1TaVix1VkiDbqal4bxiT19jaogqMinVBUkFHhEJ16Gh3DxNxfuqxCHLeSr838SU8Um-4UcQnIfZB-heGn3G7_d5OqvELsj8Y1ZdJXnYx'
API_KEY='dvAPWyaYPLubBZamw90rzQWVNllN7QUbwPX_9biXqS16UU5tAK-dznUF47vLjaBa3xuY2QH5P6t5-D8v6U-qzycf0haecy_dhDA0g_IlmsMxpYVQZpyuGuAZFURaYXYx'
cuisines = ['vietnamese', 'thai', 'cuban','greek','swedish','british','middle eastern']#'chinese', 'japanese', 'italian', 'korean', 'french', 'american', 'mexican', 'indian']
# cuisines = ['french']
    

def request(api_key, term, location = "New York", limit = 50):
    url = 'https://api.yelp.com/v3/businesses/search'
    headers = {'Authorization': 'Bearer %s' % api_key}
    response = []
    id_set = set()
 
    offset = 0
    json_map = {}
    #TODO: change to 20
    for i in range(20):
        offset += 50
        params = {'term':term,'location': location, 'limit': limit, 'offset': offset}
        req = requests.get(url, params = params, headers = headers)
        print(req.status_code)
        json_map[i] = req.json()
        # print(parsed)

    file_name = term + '.json'
    with open(file_name, 'w') as openfile:
        json.dump(json_map, openfile, indent = 4)
    
# fields: id, name, review_count, category (new) , display_phone, 
# display_address (join list), rating, price, open hours, coordinates, zip code
def main():      
    for cuisine in cuisines:
        request(API_KEY, cuisine)
        # to avoid request too often
        time.sleep(150)


if __name__ == '__main__':
    main()