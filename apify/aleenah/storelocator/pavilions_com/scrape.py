import csv
import json
from sgrequests import SgRequests
from bs4 import BeautifulSoup

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)

session = SgRequests()
def fetch_data():

    all=[]
    res= session.get("https://local.pavilions.com/index.html")
    soup = BeautifulSoup(res.text, 'html.parser')
    sa = soup.find_all('a', {'class': 'Directory-listLink'})
    for a in sa:
        res = session.get("https://local.pavilions.com/"+a.get('href'))
        soup = BeautifulSoup(res.text, 'html.parser')
        stores = soup.find_all('a', {'class': 'Directory-listLink'})

        for store in stores:
            if store.get('data-count') =="(1)":
                url="https://local.pavilions.com/" + store.get('href')
                res = session.get("https://local.pavilions.com/" + store.get('href'))
                soup = BeautifulSoup(res.text, 'html.parser')

                loc= soup.find('div', {'class': 'Heading--lead ContentBanner-title'}).text
                street = soup.find('span', {'class': 'c-address-street-1'}).text
                state=soup.find('abbr', {'class': 'c-address-state'}).text
                city=soup.find('span', {'class': 'c-address-city'}).text
                zip=soup.find('span', {'class': 'c-address-postal-code'}).text
                lat=soup.find('meta', {'itemprop': 'latitude'}).get('content')
                long=soup.find('meta', {'itemprop': 'longitude'}).get('content')
                phones=soup.find_all('div', {'class': 'Core-phone'})
                tims=soup.find_all('div', {'class': 'c-hours-details-wrapper js-hours-table'})
                for p in phones:
                    type = p.find('div',{'class':'Phone-label'}).text.replace(" Phone","").replace(":","")
                    phone= p.find('div',{'class':'Phone-display Phone-display--withLink'}).text
                    timi = json.loads(tims[phones.index(p)].get('data-days'))
                    tim=""
                    for day in timi:
                        start=str(day['intervals'][0]['start'])[:-2]+":"+str(day['intervals'][0]['start'])[-2:]
                        end=str(day['intervals'][0]['end'])[:-2]+":"+str(day['intervals'][0]['end'])[-2:]
                        tim+=day['day']+": "+start+" - "+end+" "

                    #print(tim)
                    print(type)
                    all.append([
                        "https://pavilions.com",
                        loc,
                        street,
                        city,
                        state,
                        zip,
                        "US",
                        "<MISSING>",  # store #
                        phone,  # phone
                        type,  # type
                        lat,  # lat
                        long,  # long
                        tim.strip(),  # timing
                        url])

            else:
                res = session.get("https://local.pavilions.com/" + store.get('href'))
                soup = BeautifulSoup(res.text, 'html.parser')
                mstores=soup.find_all('a', {'class': 'Teaser-titleLink'})
                for m in mstores:
                    url="https://local.pavilions.com/" + m.get('href').replace('../','')
                    res = session.get("https://local.pavilions.com/" + m.get('href').replace('../',''))

                    soup = BeautifulSoup(res.text, 'html.parser')

                    loc = soup.find('div', {'class': 'Heading--lead ContentBanner-title'}).text
                    street = soup.find('span', {'class': 'c-address-street-1'}).text
                    state = soup.find('abbr', {'class': 'c-address-state'}).text
                    city = soup.find('span', {'class': 'c-address-city'}).text
                    zip = soup.find('span', {'class': 'c-address-postal-code'}).text
                    lat = soup.find('meta', {'itemprop': 'latitude'}).get('content')
                    long = soup.find('meta', {'itemprop': 'longitude'}).get('content')
                    phones = soup.find_all('div', {'class': 'Core-phone'})
                    tims = soup.find_all('div', {'class': 'c-hours-details-wrapper js-hours-table'})
                    for p in phones:
                        type = p.find('div', {'class': 'Phone-label'}).text.replace(" Phone", "").replace(":","")
                        phone = p.find('div', {'class': 'Phone-display Phone-display--withLink'}).text
                        timi = json.loads(tims[phones.index(p)].get('data-days'))
                        tim = ""
                        for day in timi:
                            start = str(day['intervals'][0]['start'])[:-2] + ":" + str(day['intervals'][0]['start'])[-2:]
                            end = str(day['intervals'][0]['end'])[:-2] + ":" + str(day['intervals'][0]['end'])[-2:]
                            tim += day['day'] + ": " + start + " - " + end + " "

                        # print(tim)
                        print(type)
                        all.append([
                            "https://pavilions.com",
                            loc,
                            street,
                            city,
                            state,
                            zip,
                            "US",
                            "<MISSING>",  # store #
                            phone,  # phone
                            type,  # type
                            lat,  # lat
                            long,  # long
                            tim.strip(),  # timing
                            url])

    return all
    
def scrape():
    data = fetch_data()
    write_output(data)

scrape()

