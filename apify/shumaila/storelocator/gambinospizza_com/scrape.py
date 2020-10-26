import requests
from bs4 import BeautifulSoup
import csv
import string
import re, time
import usaddress
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

def write_output(data):
    with open('data.csv', mode='w', encoding="utf-8") as output_file:
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
    chrome_path = '/Users/Dell/local/chromedriver'
    #return webdriver.Chrome(chrome_path, chrome_options=options)
    return webdriver.Chrome('chromedriver', chrome_options=options)

def fetch_data():
    # Your scraper here
    data = []

    url = 'https://gambinospizza.com'
    page = requests.get(url)
    soup = BeautifulSoup(page.text, "html.parser")
    mainul = soup.find('nav')
    ul_list = mainul.find('ul')
    li_list = ul_list.findAll('li')
    ul_list = li_list[3].find('ul')
    li_list = ul_list.findAll('li')
    cleanr = re.compile('<.*?>')
    pattern = re.compile(r'\s\s+')
    p = 1
    print(len(li_list))
    i = 1
    for divs in li_list:
        link = divs.find('a')
        link = "https://gambinospizza.com/" + link['href']

        page = requests.get(link)
        soup = BeautifulSoup(page.text, "html.parser")
        try:
            #print(link)
            mainul = soup.find('td', {'align': 'left'})

            links = mainul.findAll('a')

            if len(links) == 0:
                mainul = soup.findAll('td', {'align': 'left'})

                links = mainul[1].findAll('a')


            for link in links:

                try:
                    title = link.text

                    link = "https://gambinospizza.com/stores/" + link['href']
                    page = requests.get(link)

                    flag = 1
                    soup = BeautifulSoup(page.text, "html.parser")
                    # soup = soup.encode("utf-8")
                    div = soup.find('div', {'class': 'storeinfo'})

                    addresslist = div.findAll('h1')
                    hlist = div.text
                    hlist = hlist.replace("\n", "|")
                    flag = 2
                    try:
                        phone = div.find('h4').text
                        phone = phone.replace("\n", "")
                        start = hlist.find("HOURS")
                        start = hlist.find("|", start) + 1
                        end = hlist.find("||", start)
                        hours = hlist[start:end]
                        hours = hours.replace("\t", "")


                    except:

                        driver = get_driver()
                        driver.get(link)
                        time.sleep(2)
                        try:
                            h4 = driver.find_element_by_xpath("/html/body/div[3]/div[2]/div/div[1]/div[2]/h4")
                            phone = h4.text
                        except:
                            phone = "<MISSING>"
                            flag = 11
                        try:
                            print("ll")
                            hlist = driver.find_element_by_xpath("/html/body/div[3]/div[2]/div/div[1]/div[2]").text
                            hlist = hlist.replace("\n", "|")
                            start = hlist.find("HOURS")
                            start = hlist.find("|", start) + 1
                            end = hlist.find("||", start)
                            hours = hlist[start:end]
                            hours = hours.replace("\t", "")

                        except:
                            print("NN")
                            flag = 12
                            start = hlist.find("HOURS")
                            start = hlist.find("|", start) + 1
                            end = hlist.find("||", start)
                            hours = hlist[start:end]
                            hours = hours.replace("\t", "")



                    address = ""
                    for addr in addresslist:
                        address = address +" " +  addr.text

                    flag = 5
                    try:
                        map = soup.find('div', {'class': 'storemap'})
                        map = map.find('iframe')
                        maplink = map['src']
                        #print(maplink)
                        start = maplink.find("!2d")
                        if start == -1:
                            lat = "<MISSING>"
                            longt = "<MISSING>"
                        else:
                            start = start + 3
                            end = maplink.find("!3d", start)
                            longt = maplink[start:end]
                            start = end + 3
                            end = maplink.find("!", start)
                            lat = maplink[start:end]
                    except:
                        lat = "<MISSING>"
                        longt = "<MISSING>"
                    flag = 6
                    address = usaddress.parse(address)
                    i = 0
                    street = ""
                    city = ""
                    state = ""
                    pcode = ""
                    ccode = ""
                    while i < len(address):
                        temp = address[i]
                        if temp[1].find("Address") != -1 or temp[1].find("Street") != -1 or temp[1].find(
                                "Recipient") != -1 or \
                                temp[1].find("BuildingName") != -1 or temp[1].find("USPSBoxType") != -1 or temp[1].find(
                            "USPSBoxID") != -1 or temp[1].find("LandmarkName") != -1:
                            street = street + " " + temp[0]
                        if temp[1].find("PlaceName") != -1:
                            city = city + " " + temp[0]
                        if temp[1].find("StateName") != -1:
                            state = state + " " + temp[0]
                        if temp[1].find("ZipCode") != -1:
                            pcode = pcode + " " + temp[0]

                        i += 1
                    flag = 7
                    street = street.lstrip()
                    if len(street) < 3:
                        street = div.find('h2').text

                    street = street.replace("\n", "")
                    street = street.replace(",", "")

                    if len(city) < 3 or city != title:
                        city = title
                    city = city.lstrip()
                    city = city.replace(",", "")
                    state = state.lstrip()
                    pcode = pcode.lstrip()
                    pcode = pcode.replace("\n", "")


                    flag = 9
                    hours = re.sub(pattern, "", hours)
                    start = hours.find("||")
                    if start != -1:
                        hours = hours[0:start]

                    hours = re.sub('[^A-Za-z0-9-|: ]+', '', hours)


                    flag = 8
                    print(link)
                    print(title)
                    print(street)
                    print(city)
                    print(state)
                    print(pcode)
                    print(phone)
                    print(hours)
                    print(lat)
                    print(longt)
                    print(p)
                    print("..................................")
                    p += 1
                    data.append([
                        url,
                        link,
                        title,
                        street,
                        city,
                        state,
                        pcode,
                        "US",
                        "<MISSING>",
                        phone,
                        "<MISSING>",
                        lat,
                        longt,
                        hours
                    ])



                except:

                    flag =1
        except:

            flag = 2

    return data




def scrape():
        data = fetch_data()
        write_output(data)

scrape()
