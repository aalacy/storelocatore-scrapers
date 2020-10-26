import csv
import re
from bs4 import BeautifulSoup
from sgrequests import SgRequests

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
    # Your scraper here
    locs = []
    street = []
    states=[]
    cities = []
    types=[]
    phones = []
    zips = []
    long = []
    lat = []
    timing = []
    ids=[]
    page_url=[]
    res=session.get("https://locations.bucadibeppo.com/us")
    soup = BeautifulSoup(res.text, 'html.parser')
    lis = soup.find_all('li', {'class': 'c-directory-list-content-item'})

    for li in lis:
        num = int(li.find('span').text.replace("(","").replace(")",""))
        uli="https://locations.bucadibeppo.com/"+li.find("a").get("href").replace("../","")
        if num == 1 and uli !="https://locations.bucadibeppo.com/us/nj" :

            page_url.append(uli)
        else:
            res = session.get("https://locations.bucadibeppo.com/"+li.find("a").get("href").replace("../",""))
            soup = BeautifulSoup(res.text, 'html.parser')
            llis = soup.find_all('li', {'class': 'c-directory-list-content-item'})
            if llis ==[]:
                res = session.get("https://locations.bucadibeppo.com/" + li.find("a").get("href").replace("../", ""))
                soup = BeautifulSoup(res.text, 'html.parser')
                divs = soup.find_all('div', {'class': 'c-location-grid-col'})
                for div in divs:
                    page_url.append("https://locations.bucadibeppo.com/" +div.find("a").get("href").replace("../", ""))
            for lli in llis:
                num = int(lli.find('span').text.replace("(", "").replace(")", ""))

                if num == 1:
                    page_url.append("https://locations.bucadibeppo.com/" + lli.find("a").get("href").replace("../",""))
                else:
                    res = session.get("https://locations.bucadibeppo.com/" + lli.find("a").get("href").replace("../",""))
                    soup = BeautifulSoup(res.text, 'html.parser')
                    divs = soup.find_all('div', {'class': 'c-location-grid-col'})
                    for div in divs:
                        page_url.append("https://locations.bucadibeppo.com/" +div.find("a").get("href").replace("../",""))

    for url in page_url:
        #print(url)
        res = session.get(url)
        soup = BeautifulSoup(res.text, 'html.parser')
        #print(soup)
        #break
        try:

            ids.append(re.findall(r'{"ids":(.*),"pageSetId"',str(soup),re.DOTALL)[0])
            #print(url)
        except:
                print(url)
                ids.append("<MISSING>")
                locs.append("<MISSING>")
                street.append("<MISSING>")
                cities.append("<MISSING>")
                states.append("<MISSING>")
                zips.append("<MISSING>")
                phones.append("<MISSING>")
                timing.append("<MISSING>")
                long.append("<MISSING>")
                lat.append("<MISSING>")
                continue
        """except:
            urll = "https://locations.bucadibeppo.com/" + soup.find('li', {'class': 'c-directory-list-content-item'}).find("a").get("href").replace("../","")
            print(urll)
            res = requests.get(urll)
            soup = BeautifulSoup(res.text, 'html.parser')
            urll = "soup.find('div', {'class': 'c-location-grid-col'}).find("a").get("href").replace("../","")
            print(urll)
            res = requests.get(urll)
            soup = BeautifulSoup(res.text, 'html.parser')
            page_url[page_url.index(url)]=urll
            ids.append(re.findall(r', {"ids":(.*),', str(soup))[0])"""

        locs.append(soup.find('span', {'class': 'LocationName'}).text)
        street.append(soup.find('span', {'class': 'c-address-street'}).text)
        cities.append(soup.find('span', {'itemprop': 'addressLocality'}).text)
        states.append(soup.find('span', {'itemprop': 'addressRegion'}).text)
        zips.append(soup.find('span', {'itemprop': 'postalCode'}).text)
        phones.append(soup.find('span', {'class': 'c-phone-number-span c-phone-main-number-span'}).text.strip())
        tdays=soup.find_all('td', {'class': 'c-location-hours-details-row-day'})
        topens= soup.find_all('span', {'class': 'c-location-hours-details-row-intervals-instance-open'})
        tcloses=soup.find_all('span', {'class': 'c-location-hours-details-row-intervals-instance-close'})
        tim=""
        #print("tdays",len(tdays),"topens",len(topens),"tcloses",len(tcloses))
        if len(topens)!=0 and len(tcloses)!=0 :
            for t in range(7):
                tim+=tdays[t].text+": "+topens[t].text+" - "+tcloses[t].text+" "
        else:
            tim="Mon - Fri: CLOSED"
        timing.append(tim.strip())
        long.append(soup.find('meta', {'itemprop': 'longitude'}).get("content"))
        lat.append(soup.find('meta', {'itemprop': 'latitude'}).get("content"))
    all = []
    for i in range(0, len(locs)):
        row = []
        row.append("https://www.bucadibeppo.com")
        row.append(locs[i])
        row.append(street[i])
        row.append(cities[i])
        row.append(states[i])
        row.append(zips[i])
        row.append("US")
        row.append(ids[i])  # store #
        row.append(phones[i])  # phone
        row.append("<MISSING>")  # type
        row.append(lat[i])  # lat
        row.append(long[i])  # long
        row.append(timing[i])  # timing
        row.append(page_url[i])  # page url

        all.append(row)
    return all

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
