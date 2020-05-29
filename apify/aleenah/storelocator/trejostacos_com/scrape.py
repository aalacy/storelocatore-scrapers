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
    page_url=[]
    res=session.get("https://www.yelp.com/search?find_desc=Trejos+Tacos&find_loc=Los+Angeles%2C+CA")
    soup = BeautifulSoup(res.text, 'html.parser')
    urls = soup.find_all('a', {'class': 'lemon--a__373c0__IEZFH link__373c0__1G70M link-color--inherit__373c0__3dzpk link-size--inherit__373c0__1VFlE'})

    for url in urls:
        if "Trejos" in url.text or "Trejo’s" in url.text:
            url="https://www.yelp.com"+url.get('href')
            res = session.get(url)
            soup = BeautifulSoup(res.text, 'html.parser')
            tim = soup.find('table', {'class': 'lemon--table__373c0__2clZZ hours-table__373c0__2cULu table__373c0__3JVzr table--simple__373c0__3lyDA'}).text.replace("Mon"," Mon ").replace("Tue"," Tue ").replace("Wed"," Wed ").replace("Thu"," Thu ").replace("Fri"," Fri ").replace("Sat"," Sat ").replace("Sun"," Sun ").strip()
            if tim=="":
                tim="<MISSING>"

            street = soup.find('span', {'itemprop': 'streetAddress'}).text.replace("StS","St S").strip()
            #print(street)
            city=soup.find('span', {'itemprop': 'addressLocality'}).text
            state=soup.find('span', {'itemprop': 'addressRegion'}).text
            country=soup.find('meta', {'itemprop': 'addressCountry'}).get('content')
            zip=soup.find('span', {'itemprop': 'postalCode'}).text
            phone=soup.find('span', {'itemprop': 'telephone'}).text.strip()
            loc = soup.find('h1', {'class': 'lemon--h1__373c0__2ZHSL heading--h1__373c0__1VUMO heading--no-spacing__373c0__1PzQP heading--inline__373c0__1F-Z6'}).text
            img=soup.find('img', {'alt': 'Map'}).get('src')
            lat,long=re.findall(r'center=([\d\.]+)%2C([\d\.\-]+)&',img)[0]
            #print(lat,long)

            all.append([
                "https://www.trejostacos.com",
                loc,
                street,
                city,
                state,
                zip,
                country,
                "<MISSING>",  # store #
                phone,  # phone
                "<MISSING>",  # type
                lat,  # lat
                long,  # long
                tim,  # timing
                url])
    """for url in urls: #for official trejos website temoprariliy don due to corona virus
        url="https://www.trejostacos.com"+url.get('href')
        print(url)
        driver.get(url)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        print(soup)
        p = soup.find('div', {'class': 'sqs-block-content'}).find_all('p')
        print(soup.find('div', {'class': 'sqs-block-content'}).text)
        street=p[0].text
        addr=p[1].text.strip().split(",")
        city=addr[0].strip()
        addr=addr[1].strip().split(" ")
        state=addr[0]
        zip=addr[1]
        phone=p[2].find('a').text.strip()
        tim= re.findall(r'HOURS(.*)-------------------------------------------',soup.find('div', {'class': 'sqs-block-content'}).text,re.DOTALL)[0]
        print(phone)
        print(tim)"""
    return all

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
