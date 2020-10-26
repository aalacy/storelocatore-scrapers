from bs4 import BeautifulSoup
import csv
import string,json
import re, time, datetime

from sgrequests import SgRequests

session = SgRequests()
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36',
           'X-NewRelic-ID': 'VQcFV1FVARAJXFNQDgcG',
        'X-Requested-With': 'XMLHttpRequest',
        'Content-Type':'application/json'
           }

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    # Your scraper here
    data = []
    p = 0
    url = 'https://www.agentprovocateur.com/int_en/api/n/bundle'
    formdata = '{"requests":[{"action":"find","type":"store","verbosity":1,"filter":{"verbosity":1,"id":{"$nin":[]}},"children":[{"_reqId":0}]}]}'
    loclist = session.post(url, headers=headers, data=formdata).json()['catalog']
    hourd = {"0":"Mon","1":"Tues","2":"Wed","3":"Thurs","4":"Fri","5":"Sat","6":"Sun"}
    for loc in loclist:
        
        if loc['country_id'] == 'US':            
            title = loc['store_name']
            city = loc['city']
            street = loc['address']
            lat = loc['latitude']
            longt = loc['longitude']
            state = '<MISSING>'#loc['state']
            pcode = loc['postcode']
            phone =loc['phone']
            ltype = loc['type']
            hourlist = str(loc['days'])
            store = loc['id']
            check = 0
            flag =0
            hours = ''
            while True:
                try:
                    hr = hourlist.split("'",1)[1].split("'",1)[0]                    
                    hrt,temp  = hourlist.split(': {',1)[1].split(", 'open_break'",1)                    
                    hrt = '{' + hrt.replace("'",'"')+'}'                    
                    hrt = json.loads(hrt)                    
                                      
                    yr,month,dt = hr.split('-')
                    today = datetime.datetime((int)(yr), (int)(month), (int)(dt))
                    tdat = today.weekday()                    
                    daynow = hourd[str(tdat)]
                    if check == tdat:
                        break
                    if flag == 0:
                        flag = 1
                        check = tdat
                   
                    close= (int)(hrt["close"].split(':')[0])
                    if close > 12:
                        close = close -12
                    opent= (int)(hrt['open'].split(':')[0])
                    if opent > 12:
                        opent = opent -12
                    hours =hours + daynow +' '+ str(opent) + ' AM' + " - " + str(close) + " PM "
                    hourlist = temp.split('},',1)[1]
                except Exception as e:
                    #print(e)
                    break
                
            data.append([
                        'https://www.agentprovocateur.com/int_en/',
                        'https://www.agentprovocateur.com/int_en/store-finder#location='+city ,                   
                        title,
                        street,
                        city,
                        state,
                        pcode,
                        'US',
                        store,
                        phone.replace('+1 ',''),
                        ltype,
                        lat,
                        longt,
                        hours
                    ])
            #print(p,data[p])
            p += 1
                
            

    return data


def scrape():
    print(time.strftime("%H:%M:%S", time.localtime(time.time())))
    data = fetch_data()
    write_output(data)
    print(time.strftime("%H:%M:%S", time.localtime(time.time())))

scrape()
