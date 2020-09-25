import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re, json

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain","page_url", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"
                         ])
        # Body
        for row in data:
            writer.writerow(row)

session = SgRequests()
all=[]
def fetch_data():
    r=session.get("https://www.sbe.com/")
    p = 0
    soup = BeautifulSoup(r.text,'html.parser')
    divlist = soup.find('ul',{'class':'menu--level-1'}).findAll('li',{'class':'menu__item--column'})[0].find('ul',{'class':'menu--level-2'})
    divlist = divlist.findAll('a')
    for div in divlist:
        if div.text.find('Soon') == -1:
            statelink = 'https://www.sbe.com' + div['href']
            #print("state=",statelink)
            r=session.get(statelink)
            soup = BeautifulSoup(r.text,'html.parser')
            hotellist = soup.findAll('div',{'class':'card__body'})[1].findAll('a')
            flag = 0
            if len(hotellist) == 0:
                hotellist.append(statelink)
                flag = 1
            for hotel in hotellist:
                if flag == 0:
                    if hotel.text.find('Soon') == -1 and hotel['href'].find('resturant') == -1 and hotel['href'].find('nightlife') == -1:
                        if hotel['href'].find('https') == -1:
                            hotel = 'https://www.sbe.com' + hotel['href']
                        else:
                            if hotel['href'].find('https://www.sbe.com') > -1:
                                hotel = hotel['href']
                            else:
                                continue
                         
                        #print("hotel",hotel)
                        r=session.get(hotel)
                        soup = BeautifulSoup(r.text,'html.parser')
                        
                    spacheck = soup.find('ul',{'class':'menu--level-0'}).findAll('a')
                    for spa in spacheck:
                        if spa.text.find('Spa') > -1 and spa['href'].find('ciel') > -1:
                            link = 'https://www.sbe.com' + spa['href']
                            #print('link',link)
                            r=session.get(link)
                            res = r.text.split('<script type="application/ld+json">')[2].split('</script>',1)[0]    
                            res = json.loads(res)    
                            title = res['name']
                            street = res['address']['streetAddress']
                            city  = res['address']['addressLocality']
                            state = res['address']['addressRegion']
                            pcode = res['address']['postalCode']
                            phone = res['telephone']
                            lat = r.text.split('{"lat":"',1)[1].split('"',1)[0]
                            longt = r.text.split('"lng":"',1)[1].split('"',1)[0]
                            hours = '<MISSING>'
                          
                            all.append([
                                    "https://www.sbe.com/hotels/brands/ciel-spa",
                                    link,
                                    title,
                                    street,
                                    city,
                                    state,
                                    pcode,
                                    'US',
                                    "<MISSING>",  # store #
                                    phone,  # phone
                                    "<MISSING>",  # type
                                    lat,  # lat
                                    longt,  # long
                                    hours,  # timing
                                   ])
                            #print(p,all[p])
                            p += 1

      
    
    return all

def scrape():
    data = fetch_data()
    write_output(data)

scrape()

