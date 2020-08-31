from bs4 import BeautifulSoup
import csv
import string
import re, time

from sgrequests import SgRequests

session = SgRequests()
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'
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
    data = []
    p = 0
    
    url = 'https://momentfeed-prod.apigee.net/api/llp.json?auth_token=ZLHQWBGKROQFVIUG&pageSize=30'
    sitemap = 'https://momentfeed-prod.apigee.net/api/v2/llp/sitemap?auth_token=ZLHQWBGKROQFVIUG&country=US'
    maplist = session.get(sitemap, headers=headers, verify=False).json()['locations']
    loclist = session.get(url, headers=headers, verify=False).json()
    #print(maplist)
    hourd = {"1":"Mon","2":"Tues","3":"Wed","4":"Thurs","5":"Fri","6":"Sat","7":"Sun"}
    for loc in loclist:
        loc = loc['store_info']
        title = loc['name']
        store = loc['corporate_id']
        street = loc['address']
        try:
            street = street+' '+ loc['address_extended']
        except:
            pass
        city = loc['locality']
        state = loc['region']
        pcode = loc['postcode']
        ccode = loc['country']
        phone = loc['phone']
        lat = loc['latitude']
        longt = loc['longitude']
        link = loc['website']
        hourlist =loc['store_hours'].split(';')
        hours =''
        for hr in hourlist:
            try:
                day,start,end= hr.split(',')
                day = hourd[str(day)]
                start = str(start).replace('00',':00 AM ')
                end = (int)(str(end).replace("00",''))
                if end > 12 :
                    end = end -12
                hours = hours + day +' '+ start + '- '+ str(end) +":00 PM "
            except:
                pass

        status = 0
        #print(street)
        #print(len(maplist))
        for t in maplist:
            #print(t['store_info']['address'])
            #input()
            if street.find(t['store_info']['address']) > -1:
                #print("YES")
                link = 'https://locations.smoothiefactory.com' +t["llp_url"]
                if t['open_or_closed'].find('coming soon') > -1:
                    status = 1
                if t['open_or_closed'].find('temp closed') > -1:
                    hours = t['open_or_closed']
                break
                    
        if status == 1:
            continue
        data.append([
                        'https://smoothiefactory.com/',
                        link,                   
                        title,
                        street,
                        city,
                        state,
                        pcode,
                        'US',
                        store,
                        phone,
                        '<MISSING>',
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
