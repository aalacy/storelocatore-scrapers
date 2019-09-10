import csv
import re
import pdb
import requests
from lxml import etree
import json


base_url = 'https://www.prestigepreschoolacademy.com'


def validate(item):    
    if item == None:
        item = ''
    if type(item) == int or type(item) == float:
        item = str(item)
    if type(item) == list:
        item = ' '.join(item)
    return item.encode('ascii', 'ignore').encode("utf8").strip()

def get_value(item):
    if item == None :
        item = '<MISSING>'
    item = validate(item)
    if item == '':
        item = '<MISSING>'    
    return item

def eliminate_space(items):
    rets = []
    for item in items:
        item = validate(item)
        if item != '':
            rets.append(item)
    return rets

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def fetch_data():
    output_list = []
    url = "https://www.additionelle.com/mobify/proxy/base/s/Additionelle_CA/dw/shop/v18_8/stores?country_code=CA&postal_code=K1P1B1&max_distance=20000&count=200&locale=default"
    session = requests.Session()
    headers = {
        'Accept': 'application/json',
        'authorization': 'Bearer eyJfdiI6IjEiLCJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJfdiI6IjEiLCJleHAiOjE1Njc0NTk5NTksImlhdCI6MTU2NzQ1ODE1NiwiaXNzIjoiYTU4ODA0MTUtOTZjMi00ZmUxLThkMWUtYTcwYTM0M2RmZTY5Iiwic3ViIjoie1wiX3ZcIjpcIjFcIixcImN1c3RvbWVyX2luZm9cIjp7XCJjdXN0b21lcl9pZFwiOlwiYWJlY3hCVmpDcGpIRnV3cUpQNmhiSzhXNWZcIixcImd1ZXN0XCI6dHJ1ZX19In0.dl8XgldAVo8SGRDrrSAdnbD_tnRnfYwIrohjhsPW78JgTif2kukQqnB74RgKHRx6U5CTBee8ktTVwqnmtguRTykAZhEmLhVZpKf1o0rIJVJyf2tY7UPDQeg5eyXwnZx1VWqP8vyEy_dhw5RsnBYiD_meu9rmYKFgg2xLynHGBIRA6oxoUDXSLht0by3DrEGUAVZAOyga6Z4caXTDyWqrsECOggZ8szlIoC2UALRrOmd6Y2NpG_mOX_gOmYm_m7hJzKuY4zU90SGc-GYkbBKfRPK3GthTr0LNXVsknydirpsZDI1hlBjrCxNz689-ogulmrW_-VZpXsf2KNUqszr3w59HR1C0JlkkVgKsvuSBZYG9ppqTAPvXF-nMuRYDd2Hc3-RoGsk4N6kLozoGuuA2m0lWubR6jx43Wgla4vzvqA67jMF25n5rNU7eFzxdV4sJIXstqWaxHHcNBsZceo2RnGuSwPENkksPx8OfaPyapzE',
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36',
        'x-dw-client-id': 'a5880415-96c2-4fe1-8d1e-a70a343dfe69'
    }
    request = session.get(url, headers=headers)
    data = json.loads(request.text)
    if 'data' in data:
        store_list = data['data']
        for store in store_list:
            output = []
            output.append(base_url) # url
            output.append(get_value(store['name'])) #location name
            output.append(get_value(store['address1'])) #address
            output.append(get_value(store['city'])) #city
            output.append(get_value(store['state_code'])) #state
            output.append(get_value(store['postal_code'])) #zipcode
            output.append(get_value(store['country_code'])) #country code
            output.append(get_value(store['id'])) #store_number
            output.append(get_value(store['phone'])) #phone
            output.append('Fashionable & Trendy Plus Size Clothing | Addition Elle') #location type
            output.append(get_value(store['latitude'])) #latitude
            output.append(get_value(store['longitude'])) #longitude            
            store_hours = validate(eliminate_space(etree.HTML(store['store_hours']).xpath('.//span//text()')))
            output.append(get_value(store_hours)) #opening hours
            output_list.append(output)
    return output_list

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
