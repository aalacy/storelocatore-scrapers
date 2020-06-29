import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation",
                         "page_url"])
        # Body
        for row in data:
            writer.writerow(row)


session = SgRequests()
all=[]
def fetch_data():
    # Your scraper here
    headers={
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
'accept-encoding': 'gzip, deflate',
'accept-language': 'en-US,en;q=0.9',
'cache-control': 'max-age=0',
'sec-fetch-dest': 'document',
'sec-fetch-mode': 'navigate',
'sec-fetch-site': 'none',
'sec-fetch-user': '?1',
'upgrade-insecure-requests': '1',
'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36'
    }
    res=session.get("https://midwest-dental.com/locations/",headers=headers)
    soup = BeautifulSoup(res.text, 'html.parser')
    #print(soup)
    links = soup.find_all('li', {'class': 'office-link'})

   # print(len(links))
    for link in links:

        url = "https://midwest-dental.com" + link.find('a').get('href')
        res = session.get(url,headers=headers)
        soup = BeautifulSoup(res.text, 'html.parser')
        slinks = soup.find_all('li', {'class': 'office-link'})
        if slinks != []:
            for slink in slinks:
                url = slink.find('a').get('href')
                print(url)
                res = session.get(url,headers=headers)
                soup = BeautifulSoup(res.text, 'html.parser')
                loc=soup.find('title').text.split('|')[1].strip()
                div=soup.find('div', {'id': 'breadcrumb'})
                sa=div.find_all('a')
                phone = sa[0].get('href').replace('tel:','')
                #print(sa[1].get('href'))
                try:
                    lat,long= re.findall(r'/@(-?[\d\.]+),(-?[\d\.]+)',sa[1].get('href'))[0]
                except:
                    lat=long="<MISSING>"
                addr=sa[1].text.replace('  ',' ').strip().split(',')
                sz=addr[-1].strip().split(' ')
                state=sz[0]
                zip=sz[1]
                del addr[-1]
                city=addr[-1].strip()
                del addr[-1]
                street = ','.join(addr)

                spans= soup.find('div', {'id': 'hours-drop'}).find_all('span')
                del spans[0]
                del spans[0]
                tim=""
                for span in spans:
                    tim+=span.text+" "
                tim=tim.strip()

                all.append([
                    "https://midwest-dental.com",
                    loc,
                    street,
                    city,
                    state,
                    zip,
                    'US',
                    "<MISSING>",  # store #
                    phone,  # phone
                    "<MISSING>",  # type
                    lat,  # lat
                    long,  # long
                    tim,  # timing
                    url])


        else:
            hours = soup.find_all('div', {'id': 'hours-drop'})
            if hours == []:
                continue
            else:
                loc = soup.find('title').text.split('|')[1].strip()
                div = soup.find('div', {'id': 'breadcrumb'})
                sa = div.find_all('a')
                phone = sa[0].get('href').replace('tel:', '')
                try:
                    lat, long = re.findall(r'/@(-?[\d\.]+),(-?[\d\.]+)', sa[1].get('href'))[0]
                except:
                    lat = long = "<MISSING>"
                addr = sa[1].text.replace('  ',' ').strip().split(',')
                sz = addr[-1].strip().split(' ')
                state = sz[0]
                zip = sz[1]
                del addr[-1]
                city = addr[-1].strip()
                del addr[-1]
                street = ','.join(addr)

                spans = soup.find('div', {'id': 'hours-drop'}).find_all('span')
                del spans[0]
                del spans[0]
                tim = ""
                for span in spans:
                    tim += span.text + " "
                tim = tim.strip()

                all.append([
                    "https://midwest-dental.com",
                    loc,
                    street,
                    city,
                    state,
                    zip,
                    'US',
                    "<MISSING>",  # store #
                    phone,  # phone
                    "<MISSING>",  # type
                    lat,  # lat
                    long,  # long
                    tim,  # timing
                    url])
    return all

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
