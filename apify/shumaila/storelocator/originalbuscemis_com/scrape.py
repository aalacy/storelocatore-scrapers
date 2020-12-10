from bs4 import BeautifulSoup
import csv
import string
import re, time


from sgrequests import SgRequests

session = SgRequests()
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36',
           'x-requested-with': 'XMLHttpRequest'
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
    p = 0
    data = []
    pattern = re.compile(r'\s\s+')
    cleanr = re.compile(r'<[^>]+>')
    streetlist = []
    latlist= ['44.3148443,-85.60236429999999','42.565576,-83.127351','41.565576,-85.127351','48.3056044,-82.1229766','11.696118,-110.4181358']
    url = "https://originalbuscemis.com/wp-admin/admin-ajax.php"
    for i in range(0,len(latlist)):
        latnow = latlist[i].split(',')[0]
        longnow = latlist[i].split(',')[1]
        mydata = {"nonce":"58789e415c","apikey":"71da911620ac133b0d303507b926ef6a",
            'action': 'csl_ajax_search','lat':latnow,'lng':longnow,'address':''}
   
        loclist = session.post(url,data=mydata, headers=headers, verify=False).json()#['response']
        #print(loclist)
        #input()
        loclist = loclist['response']       
        for loc in loclist:           
            title = loc['name']
            street = loc['address']
            city = loc['city']
            state = loc['state']
            pcode = loc['zip']
            phone= loc['phone']
            store = loc['id']
            lat = loc['lat']
            longt = loc['lng']
            if street in streetlist or len(pcode) < 3:
                continue
            streetlist.append(street)
            if len(phone) < 2:
                phone = '<MISSING>'
            data.append([
                        'https://originalbuscemis.com/',
                        'https://originalbuscemis.com/locations/',                   
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
                        '<MISSING>'
                    ])
            #print(p,data[p])
            p += 1
  
        
    return data


def scrape():
  
    data = fetch_data()
    write_output(data)
   
scrape()
