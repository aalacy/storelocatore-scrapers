from bs4 import BeautifulSoup
import csv
import string
import re, time

from sgrequests import SgRequests

session = SgRequests()
headers1 = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'}
     
headers = {
           'accept': 'application/json, text/javascript, */*; q=0.01',
'accept-encoding': 'gzip, deflate, br',
'accept-language': 'en-US,en;q=0.9',
'cookie': '_gcl_au=1.1.2072273244.1605808074; _ga=GA1.2.702661256.1605808077; _gaexp=GAX1.2.N3Rhc0LARAK4-5UEZkNxpw.18676.1; _hjid=ddcfa9dc-00b5-46b4-8294-2d03686ceda3; _fbp=fb.1.1605808081416.924457425; rskxRunCookie=0; rCookie=7b0tyf4u9yqfx4a83ng7ytkhp4o5rc; BCSessionID=506e0408-5560-4e9b-b6ca-11393e9715f3; _sp_id.39b0=b0ed443e87e1d448.1605952896.1.1605952916.1605952896; _gid=GA1.2.1226965084.1606064855; _hjShownFeedbackMessage=true; outlet_ndc=3280a99442d166c6602c-1606128697618; customer_zip=82001; closestStoreInfo={%22libertyTaxFlag%22:0%2C%22url%22:%22/br/store/co/westminster/7541%22%2C%22storeUnitType%22:4%2C%22storePageId%22:3%2C%22storePageDesc%22:%22Appliance%2C%20Furniture%20&%20Mattress%22%2C%22streetAddr%22:%227647%20W%2088th%20Avenue%22%2C%22phone%22:%22(303)%20940-2739%22%2C%22sunHours%22:%2210:00%20AM%20-%2007:00%20PM%22%2C%22monHours%22:%2210:00%20AM%20-%2008:00%20PM%22%2C%22tueHours%22:%2210:00%20AM%20-%2008:00%20PM%22%2C%22wedHours%22:%2210:00%20AM%20-%2008:00%20PM%22%2C%22thrHours%22:%22CLOSED%22%2C%22friHours%22:%2209:00%20AM%20-%2009:00%20PM%22%2C%22satHours%22:%2209:00%20AM%20-%2008:00%20PM%22%2C%22zip%22:%2280005%22%2C%22storeName%22:%22Westminster%20CO%22%2C%22city%22:%22Westminster%22%2C%22unit%22:7541%2C%22returnPolicyRequired%22:1%2C%22state%22:%22CO%22}; _hjIncludedInSessionSample=0; _hjTLDTest=1; _hjAbsoluteSessionInProgress=0; _hjUserAttributesHash=01bad38b88f546c89540753ea5f6ffe7; _hjCachedUserAttributes={"attributes":{},"userId":"3280a99442d166c6602c-1606128697618"}; _br_uid_2=uid%3D9653504450340%3Av%3D12.1%3Ats%3D1605808080283%3Ahc%3D13; sc_fb_session={%22start%22:1606128707932%2C%22p%22:2}; lastRskxRun=1606128753182; _uetsid=391067202ce511eb96f1db4955a7da40; _uetvid=5d700bc02a8f11eb88818de87a1d84a0; AWSALBTG=qetmdDYzJl7fbsy2qv8eSODJtwDsb3TZkNgqZaPv9CxNThOC8FXUPdAJ4Z3ZVWbjwgE2/NxNGC2hnPiE9YcfhAVC3LLYPzm28GlBGCy461FY+U9MJaa3nzfbiqeTfriKE+Qp2hrmxHOx4jDv7EUeJZ5Sq4vWJH7aBDGo3biOzQ29AXxjSAQ=; AWSALB=ISnrlX28e62wA4rsLWFDMRAq+y2JoWWLdCr68xUiTtxTo3C54H88g3hX3yLner+SEjj7NBNIIeyuLNgPMwOFy3GFRe6v87ZK3LNarRA3Lwy27oK/O6q0Ajkuntwb; sc_fb={%22v%22:0.3%2C%22t%22:499%2C%22p%22:13%2C%22s%22:4%2C%22b%22:[]%2C%22pv%22:[]%2C%22tr%22:0%2C%22e%22:[]}',
'referer': 'https://www.americanfreight.com/br/store-locator',
'sec-fetch-dest': 'empty',
'sec-fetch-mode': 'cors',
'sec-fetch-site': 'same-origin',
'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36',

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
    url = 'https://www.americanfreight.com/br/api/nearbystore?zipCode=15017&browse=true&_=1606128751240'
    loclist = session.get(url, headers=headers, verify=False).json()['storeList']
    #print(loclist)
    for loc in loclist:
        #print(loc)
        link = 'https://www.americanfreight.com'+loc['url']
        street = loc['streetAddr']
        phone = loc['phone']
        pcode = loc['zip']
        city = loc['city']
        store = loc['unit']
        state = loc['state']
        title = loc['storeName']
        hours = 'Sunday '+loc['sunHours'] + ' Monday '+loc['monHours'] +' Tuesday '+loc['tueHours'] + ' Wednesday ' + loc['wedHours'] +' Thursday ' + loc['thrHours'] + ' Friday '+loc['friHours'] + ' Saturday '+ loc['satHours']
        r = session.get(link, headers=headers1, verify=False)
        lat = r.text.split('"latitude": "',1)[1].split('"',1)[0]
        longt = r.text.split('"longitude": "',1)[1].split('"',1)[0]
        if len(phone) < 3:
            phone = r.text.split('"telephone": "',1)[1].split('"',1)
        data.append([
                        'https://www.americanfreight.com',
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
        #input()
                
 
        
    return data


def scrape():    
    data = fetch_data()
    write_output(data)


scrape()
