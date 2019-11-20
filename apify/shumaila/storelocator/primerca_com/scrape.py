
#http://www.primerica.com/public/locations.html
#https://pterrys.com

# Import libraries
import requests
from bs4 import BeautifulSoup
import csv
import string
import re, time
import usaddress
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select

def get_driver():
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    chrome_path = '/Users/Dell/local/chromedriver'
    #return webdriver.Chrome(chrome_path)
    return webdriver.Chrome('chromedriver')


def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain","page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    # Your scraper here
    data = []
    links = []
    nxtlinks = []
    p = 1
    url = 'http://www.primerica.com/public/locations.html'
    page = requests.get(url)
    soup = BeautifulSoup(page.text, "html.parser")
    maidiv = soup.find('main')
    mainsection = maidiv.findAll('section',{'class':'content locList'})
    print(len(mainsection))
    sec = 0
    while sec < 2:

        if sec == 0:
            ccode = "US"
        if sec == 1:
            ccode = "CA"

        rep_list = mainsection[sec].findAll('a')
        #print(maindiv)
        cleanr = re.compile('<.*?>')
        pattern = re.compile(r'\s\s+')
        for rep in rep_list:
            link = "http://www.primerica.com/public/" + rep['href']
            #link = 'http://www.primerica.com/public/FindRep?pageName=FINDREPZIP&province=NewFoundland&abbrv=NF'
            print(link)

            try:
                n = 0
                while True:
                    driver1 = get_driver()
                    driver1.get(link)
                    maindiv = driver1.find_element_by_tag_name('main')
                    xip_list = maindiv.find_elements_by_tag_name('a')

                    #for i in range(0,len(xip_list)):
                    #title = xip_list[n].text
                    if ccode == "CA":
                        pcode = xip_list[n].text
                    xip_list[n].click()
                    time.sleep(2)
                    mainul = driver1.find_element_by_class_name('agent-list')
                    #print(mainul.text)

                    try:
                        li_list = mainul.find_elements_by_tag_name('li')
                        #print(len(li_list))
                        for m in range(0, len(li_list)):

                            alink = li_list[m].find_element_by_tag_name('a')
                            mainlink = alink.get_attribute('href')
                            title = alink.text
                            driver = get_driver()
                            driver.get(alink.get_attribute('href'))
                            time.sleep(1)
                            #address = driver.find_element_by_class_name('officeinfo1of3blocks')
                            address = driver.find_element_by_class_name('officeInfoDataWidth')
                            address = str(address.text)
                            address = address.replace("\n", " ")
                            pdetail =driver.find_element_by_class_name('telephoneLabel')
                            phone = str(pdetail.text)
                            phone = phone.replace("Office: ", "")

                            address = usaddress.parse(address)
                            i = 0
                            street = ""
                            city = ""
                            state = ""
                            if ccode == "US":
                                pcode = ""
                            while i < len(address):
                                temp = address[i]
                                if temp[1].find("Address") != -1 or temp[1].find("Street") != -1 or temp[1].find(
                                        "Recipient") != -1 or \
                                        temp[1].find("BuildingName") != -1 or temp[1].find("USPSBoxType") != -1 or temp[
                                    1].find(
                                    "USPSBoxID") != -1:
                                    street = street + " " + temp[0]
                                if temp[1].find("PlaceName") != -1:
                                    city = city + " " + temp[0]
                                if temp[1].find("StateName") != -1:
                                    state = state + " " + temp[0]
                                if ccode == "US":
                                    if temp[1].find("ZipCode") != -1:
                                        pcode = pcode + " " + temp[0]
                                i += 1


                            street = street.lstrip()
                            city = city.lstrip()
                            city = city.replace(",", "")
                            state = state.lstrip()
                            pcode = pcode.lstrip()
                            if len(phone) < 2:
                                phone = "<MISSING>"
                            if len(street) < 2 :
                                street = "<MISSING>"
                            if len(city) < 2:
                                city  = "<MISSING>"
                            if len(state) > 2:
                                state = state[0:2]
                            if len(state) < 2 :
                                state = "<MISSING>"

                            if len(pcode) < 2:
                                pcode = "<MISSING>"

                            if len(phone) < 11:
                                phone = "<MISSING>"

                            #print(address)
                            #print(mainlink)
                            #print(title)
                            #print(street)
                            #print(city)
                            #print(state)
                            #print(pcode)
                            #print(ccode)
                            #print(phone)
                            #print(p)
                            p += 1
                            #print("...................")
                            flag = True
                            #print(len(data))
                            i = 0
                            while i < len(data) and flag:
                                if title == data[i][2]:
                                    flag = False
                                    break
                                else:
                                    i += 1
                            if state == "NF":
                                state = "NL"
                            phone = phone.replace("Mobile","")
                            phone = phone.replace(":","")
                            phone = phone.strip()

                            if flag:
                                data.append([
                                    'http://www.primerica.com/',
                                    mainlink,
                                    title,
                                    street,
                                    city,
                                    state,
                                    pcode,
                                    ccode,
                                    "<MISSING>",
                                    phone,
                                    "<MISSING>",
                                    "<MISSING>",
                                    "<MISSING>",
                                    "<MISSING>",
                                ])
                            driver.quit()

                    except:
                        pass
                    n += 1
                    #driver1.back()
                    driver1.quit()
                    #if p == 100:
                        #break


                    #break
            except:
                #print("error")
                pass

            #driver1.quit()
            #break
        sec += 1
        #if sec == 1:
            #break

    return data




def scrape():

    data = fetch_data()
    write_output(data)


scrape()
