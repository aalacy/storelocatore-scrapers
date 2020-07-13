import csv
from bs4 import BeautifulSoup
from sgselenium import SgSelenium

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

driver = SgSelenium().chrome()

all=[]
def fetch_data():
    # Your scraper here


    driver.get("https://www.iroparis.com/us/stores?country=US")


    """divs=driver.find_elements_by_class_name('Store-btnDetails js-Store-btnDetails--more Store-btnDetails--visible')
    print(len(divs))
    for div in divs:
        div.find_element_by_tag_name('i').click()"""

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    print(soup)
    tims= str(soup).split('<div class="Store-slider js-Store-slider"')

    print(tims)

    divs = soup.find_all('div', {'class': 'Store-info'})
    print(len(divs))
    for div in divs:
        loc = div.find('h3').text
        addr=div.find('a', {'class': 'Store-text Store-text--underline'}).text.strip().split('\n')
        #print(addr)
        city = div.find('span', {'class': 'Store-city'}).text
        street =addr[0]
        zip=addr[1].strip().split(' ')[0]

        phone=div.find('a', {'class': 'Store-text Store-text--phone'}).text
        tim = tims[divs.index(div)].split('div class="Store-opening">')[1].replace('OPENING HOURS','').replace('</div>','').replace('</ul>','').replace('<br/>','').replace('<ul class="Store-openingList">','').replace('<li class="Store-openingItem">','').replace('</li>','').strip().replace('\n',', ')
        print(tim)

        all.append([
            "https://www.iroparis.com",
            loc,
            street,
            city,
            "<MISSING>",
            zip,
            "US",
            "<MISSING>",  # store #
            phone,  # phone
            "<MISSING>",  # type
            "<MISSING>",  # lat
            "<MISSING>",  # long
            tim,  # timing
            "https://www.iroparis.com/us/stores?country=US"])
    return all
def scrape():
    data = fetch_data()
    write_output(data)


scrape()
