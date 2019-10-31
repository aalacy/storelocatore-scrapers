# Import libraries
import requests
from bs4 import BeautifulSoup
import csv
import string
import re, time, usaddress




def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain","page_url",  "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)
            

def fetch_data():
    # Your scraper here
    data = []
    p = 1
    url = 'https://pterrys.com'
    page = requests.get(url)
    #driver = get_driver()
    #driver.get(url)
    #time.sleep(2)
    soup = BeautifulSoup(page.text, "html.parser")    
    maindiv = soup.find('ul', {'id': 'navTopLevel'})   
    repo_list = maindiv.findAll('li')    
    cleanr = re.compile('<.*?>')
    pattern = re.compile(r'\s\s+')
    repo_list = repo_list[3]    
    mainul = repo_list.find('ul')
    repo_list = mainul.findAll('li')
    links = []
    for repo in repo_list:
        link = repo.find('a')
        link = "https://pterrys.com"+link['href']
        #print(link)
        page = requests.get(link)
        soup = BeautifulSoup(page.text, "html.parser")
        try:
            div_list = soup.findAll('div',{'class':'item itemPreview hasImg hasHoverEffect hasHoverEffect--grayscale'})
            #print(len(div_list))
            for div in div_list:
                link = div.find('a')
                link = "https://pterrys.com"+link['href']
                #print(link)
                links.append(link)
        except:
            links.append(link)
        

    for link in links:
        page = requests.get(link)
        soup = BeautifulSoup(page.text, "html.parser")
        maindiv = soup.find('itemsCollectionContent items_1mQtEPqTMK39ewnd gridView cols3 itmPd3 itmBw0 itmSy0 txa0')
        title = soup.find('title').text
        start = title.find("-")
        title = title[0:start]
        try:
            ltype = soup.find('div',{'class':'blockInnerContent'}).text
        except:
            ltype = "<MISSING>"
        div_list = soup.findAll('div',{'class':'item itemPreview'})
        
        detail = div_list[0]
        li_list = detail.findAll('li')
        street = li_list[0].text
        state = li_list[1].text
        address = street + " " + state
        address = usaddress.parse(address)
        #print(address)
        i = 0
        street = ""
        city = ""
        state = ""
        pcode = ""
        while i < len(address):
            temp = address[i]
            if temp[1].find("Address") != -1 or temp[1].find("Street") != -1 or temp[1].find("Recipient") != -1 or \
                    temp[1].find("BuildingName") != -1 or temp[1].find("USPSBoxType") != -1 or temp[1].find(
                "USPSBoxID") != -1:
                street = street + " " + temp[0]
            if temp[1].find("PlaceName") != -1:
                city = city + " " + temp[0]
            if temp[1].find("StateName") != -1:
                state = state + " " + temp[0]
            if temp[1].find("ZipCode") != -1:
                pcode = pcode + " " + temp[0]
            i += 1
        


        street = street.lstrip()
        city = city.lstrip()
        city = city.replace(",", "")
        street = street.replace(",", "")
        state = state.replace(",", "")
        if city.find("Building H ") > -1:
            city = city.replace("Building H ","")

        state = state.lstrip()
        pcode = pcode.lstrip()

        #print(link)
        #print(title)
        #print(street)
        #print(city)
        #print(state)
        #print(pcode)
        #print(ltype)
    
        detail = div_list[1]
        hours = ""
        li_list = detail.findAll('li')
        for hdetail in li_list:
            hours = hours + " | " + hdetail.text
        try:
           hours = hours + " |" + detail.find('p').text
        except:
            pass

        hours = hours[3:len(hours)]
        print(hours)

        detail = div_list[2]
        phone = detail.find('li').text
        start = phone.find(' ')
        if start != -1:
            phone = phone[0:start]
        print(phone)
        if len(phone)< 3:
            phone = "<MISSING>"
        if len(street)< 3:
            street = "<MISSING>"
        if len(city) < 3:
            city = "<MISSING>"
        if len(state) < 2:
            state = "<MISSING>"
        if len(pcode) < 3:
            pcode = "<MISSING>"
        
        #print("...........................")

        data.append([
            'https://pterrys.com',
            link,
            title,
            street,
            city,
            state,
            pcode,
            'US',
            "<MISSING>",
            phone,
            "<MISSING>",
            "<MISSING>",
            "<MISSING>",
            hours
        ])

    return data         
        
 
def scrape():
    data = fetch_data()
    write_output(data)


scrape()
