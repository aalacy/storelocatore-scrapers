import csv
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
    data = []                
    url = 'https://www.cubesmart.com/facilities/query/GetSiteGeoLocations'
    p = 0
    storelist = []
    loclist = session.post(url,headers=headers).json()    
    for loc in loclist:
        
        store = str(loc['Id'])
        street = loc['Address']
        title = 'Self Storage of '+ loc['City']
        city = loc['City'].lower().strip().replace(' ','-')
        state = loc['State']
        lat = loc['Latitude']
        longt = loc['Longitude']        
        link = 'https://www.cubesmart.com/'+state+'-self-storage/'+city+'-self-storage/'+store+'.html'
        if street in storelist:
            continue        
        storelist.append(street)
        r = session.get(link,headers=headers).text
        try:
            pcode = r.split(',"postalCode":"',1)[1].split('"',1)[0]
        except:
            continue
        phone = r.split('},"telephone":"',1)[1].split('"',1)[0]
        try:
            hours = r.split('<p class="csHoursList">',1)[1].split('</p>',1)[0].replace('&ndash;',' - ').replace('<br>',' ').lstrip()
        except:
            hours = '<MISSING>'
        if pcode == '75072':
            pcode ='75070'
   
        if str(loc['OpenSoon']) == 'False':
            data.append([
                'https://www.cubesmart.com/',
                link,                   
                title,
                street,
                str(loc['City']),
                str(loc['State']),
                pcode,
                'US',
                store,
                phone,
                '<MISSING>',
                lat,
                longt,
                hours.replace('<br/>',' ').strip()
            ])
            
            p += 1
        


    

                
        
    return data


def scrape(): 
    data = fetch_data()
    write_output(data)

scrape()

