import requests
from bs4 import BeautifulSoup
import csv
import re,time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)


def get_driver():
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument("--disable-notifications")
    return webdriver.Chrome('chromedriver.exe', chrome_options=options)
    #return webdriver.Chrome('/Users/Dell/local/chromedriver', chrome_options=options)


endprint = []

def fetch_data():
    data = []
    store_links =[]
    c=0
    t=0;m=0
    url = 'https://www.southstatebank.com/locations/'
    page = requests.get(url)
    soup = BeautifulSoup(page.text, "html.parser")
    maindiv = soup.find('div',{'class':'locations-list-v2'})
    cities_list = maindiv.findAll('a')
    url2='https://www.southstatebank.com'
    cleanr = re.compile('<.*?>')
    driver = get_driver()
    driver1 = get_driver()
    for cities in cities_list:
        city = "https://www.southstatebank.com/locations/" + cities['href']
        city = city.replace(", ",",")
        start = city.find(",")
        m+=1
        if start != len(city)-1:
            t+=1
            driver.get(city)
            time.sleep(5)
            linklist = driver.find_elements_by_class_name('loc_title')
            for i in range(0,len(linklist)):
                link = linklist[i].get_attribute('href')
                store_links.append(link)
    mylist = list(dict.fromkeys(store_links))
    for link in mylist:
        c+=1
        driver1.get(link)
        time.sleep(5)
        soup=BeautifulSoup(driver1.page_source)
        ty=soup.find('meta',property='og:url')['content']
        if(ty.endswith('.html')==True):
            location_name=driver1.find_element_by_class_name('Nap-geomodifier').text
            lat = soup.find('meta',itemprop='latitude')['content']
            long = soup.find('meta',itemprop='longitude')['content']
            street = soup.find('meta',itemprop='streetAddress')['content']
            cty=soup.find('span',itemprop='addressLocality').text
            state=soup.find('abbr',itemprop='addressRegion').text
            pcode=soup.find('span',itemprop='postalCode').text
            ccode=soup.find('abbr',itemprop='addressCountry').text
            phone=soup.find('span',itemprop='telephone').text
            ltype = "Branch"
            store="<MISSING>"
            hrs=soup.find('table',class_ = 'c-location-hours-details')
            day=hrs.find_all('tr',class_='c-location-hours-details-row')
            if len(day) ==0:
                hours='<MISSING>'
            else:
                hours=""
                for item in day:
                    d=item.find('td',class_='c-location-hours-details-row-day')
                    hours=hours+d.text+" "
                    h=item.find('td',class_='c-location-hours-details-row-intervals')
                    hours=hours+h.text+'|'
        else:
            loc=soup.find('h1',itemprop='name').text
            location_name=loc.split(',')[0]
            try:
                coord=soup.find('a',itemprop='map')['href']
            except:
                lat="<MISSING>"
                long="<MISSING"
            else:
                lat = coord[coord.find("=")+1:coord.find(",")]
                long = coord[coord.find(",")+1:coord.find("&")]
            street = soup.find('span',itemprop='streetAddress').text
            cty=soup.find('span',itemprop='addressLocality').text
            state=soup.find('span',itemprop='addressRegion').text
            pcode=soup.find('span',itemprop='postalCode').text
            ccode="US"
            ltype="ATM"
            store="<MISSING>"
            phone="<MISSING>"
            hours="<MISSING>"
        cnt = False
        for i in data:
            if street == i[3]:
                cnt= True
        if cnt == False:
            data.append([url2,link,location_name,street,cty,state,pcode,ccode,store,phone,ltype,lat,int,hours])
    return data



    #return data


def scrape():
    data = fetch_data()
    write_output(data)

scrape()