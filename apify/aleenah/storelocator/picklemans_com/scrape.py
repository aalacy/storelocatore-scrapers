import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
from sgselenium import SgSelenium

driver = SgSelenium().chrome()


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
all = []


def fetch_data():
    # Your scraper here
    page_url = []
    driver.get(
        "https://www.picklemans.com/locations.php")  # ,headers={'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36'})
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    # print(soup)
    urls = soup.find_all('p', {'class': 'storemapper-address'})
    print(len(urls))
    for url in urls:
        a = url.find_all('a')
        if a == []:
            continue
        url = "https://www.picklemans.com/" + a[0].get('href')
        print(url)
        res = session.get(url)
        soup = BeautifulSoup(res.text, 'html.parser')
        try:
            loc = soup.find('h6', {'itemprop': 'name'}).text.replace("\n", " ").strip()
        except:
            loc = soup.find('h1', {'itemprop': 'name'}).text.replace("\n", " ").strip()
        street = soup.find('span', {'itemprop': 'streetAddress'}).text
        city = soup.find('span', {'itemprop': 'addressLocality'}).text
        try:
            state = soup.find('span', {'itemprop': 'addressRegion'}).text
        except:
            state = soup.find_all('span', {'itemprop': 'addressLocality'})[1].text
        zip = soup.find('span', {'itemprop': 'postalCode'}).text


        timli = soup.find_all('bd1')
        if timli == []:
            timl = soup.find('h5').text
        else:
            timl = timli[0].text
            if "temporarily closed" in timl.lower():
                type = re.findall(r'(Temporarily.*)', timl)[0].strip()
                if "Hours:" not in timl:
                    timl = timli[1].text
            else:
                type = "open"
        # print(timl)

        try:
            tim = re.findall(r'(Temporary Hours:.*)', timl.replace("\n", " ").replace(".", ""), re.DOTALL)[
                0].strip().replace("\t", "").replace("    ", "")
        except:
            tim = re.findall(r'Hours:(.*)', timl.replace("\n", " ").replace(".", ""), re.DOTALL)[0].strip()
            if "Hours:" in tim:
                tim = re.findall(r'Hours:(.*)', tim)[0]
        if 'CLOSED' == tim.strip():
            continue
        phone = soup.find('span', {'itemprop': 'telephone'}).text
        # print(soup.find('iframe').get('src'))
        long, lat = re.findall(r'.*!2d(.*)!3d([\d\.]+)!', soup.find('iframe').get('src'))[0]

        # print(lat,long)
        all.append([
            "https://www.picklemans.com/",
            loc,
            street,
            city,
            state.replace(",", "").strip(),
            zip,
            'US',
            "<MISSING>",  # store #
            phone,  # phone
            type,  # type
            lat,  # lat
            long,  # long
            tim,  # timing
            url])
    return all


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
