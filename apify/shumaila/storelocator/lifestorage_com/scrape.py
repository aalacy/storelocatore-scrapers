import requests
from bs4 import BeautifulSoup
import csv
import string
import re, time
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('lifestorage_com')



def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    # Your scraper here
    p = 1
    states = ["Alabama","Alaska","Arizona","Arkansas","California","Colorado",
  "Connecticut","Delaware","Florida","Georgia","Hawaii","Idaho","Illinois",
  "Indiana","Iowa","Kansas","Kentucky","Louisiana","Maine","Maryland",
  "Massachusetts","Michigan","Minnesota","Mississippi","Missouri","Montana",
  "Nebraska","Nevada","New Hampshire","New Jersey","New Mexico","New York",
  "North Carolina","North Dakota","Ohio","Oklahoma","Oregon","Pennsylvania",
  "Rhode Island","South Carolina","South Dakota","Tennessee","Texas","Utah",
  "Vermont","Virginia","Washington","West Virginia","Wisconsin","Wyoming"]
    data = []

    pattern = re.compile(r'\s\s+')
    url = 'https://www.lifestorage.com/storage-units/'
    page = requests.get(url)
    soup = BeautifulSoup(page.text, "html.parser")
    for state in states:
        state = state.lower()
        state = state.replace(" ","-")
        slink = "https://www.lifestorage.com/storage-units/" + state +"/"
        logger.info(slink)
        page = requests.get(slink)
        soup = BeautifulSoup(page.text, "html.parser")
        mainul = soup.find_all('ul', {'class': 'noList storeRows cityList'})
        if mainul ==[]:
           continue
        else:
           mainul=mainul[0]
        li_list = mainul.findAll('li')
        del li_list[0]
        logger.info('li_list',len(li_list))

        for li in li_list:
            blink = li.find('a')
            blink = blink['href']
            logger.info(blink)
            check = True
            pagenum = 1
            while check:
                
                clink = "https://www.lifestorage.com" +  blink + "?pagenum=" + str(pagenum)
                pagem = requests.get(clink)
                soupm = BeautifulSoup(pagem.text, "html.parser")
                mainb = soupm.findAll('a', {'class': 'btn store'})
                if len(mainb) == 0:
                    break
                else:
                    try:
                        nex = soupm.find('li', {'class': 'next'})
                        nex = nex.find('a').text
                        pagenum += 1
                    except:
                        check = Fa
                for branch in mainb:
                    link = "https://www.lifestorage.com" + branch['href']
                    try:
                        page2 = requests.get(link)
                        soup2 = BeautifulSoup(page2.text, "html.parser")
                        detail = str(soup2)
                        start = detail.find("alternateName")
                        start = detail.find(":", start)
                        start = detail.find('"', start) + 1
                        end = detail.find('"', start)
                        title = detail[start:end]
                        start = detail.find("branchCode")
                        start = detail.find(":", start)
                        start = detail.find('"', start) + 1
                        end = detail.find('"', start)
                        store = detail[start:end]
                        start = detail.find("streetAddress")
                        start = detail.find(":", start)
                        start = detail.find('"', start) + 1
                        end = detail.find('"', start)
                        street = detail[start:end]
                        start = detail.find("addressLocality")
                        start = detail.find(":", start)
                        start = detail.find('"', start) + 1
                        end = detail.find('"', start)
                        city = detail[start:end]
                        start = detail.find("addressRegion")
                        start = detail.find(":", start)
                        start = detail.find('"', start) + 1
                        end = detail.find('"', start)
                        state = detail[start:end]
                        start = detail.find("postalCode")
                        start = detail.find(":", start)
                        start = detail.find('"', start) + 1
                        end = detail.find('"', start)
                        pcode = detail[start:end]
                        start = detail.find("addressCountry")
                        start = detail.find(":", start)
                        start = detail.find('"', start) + 1
                        end = detail.find('"', start)
                        ccode = detail[start:end]
                        start = detail.find("latitude")
                        start = detail.find(":", start) + 2
                        end = detail.find(',', start)
                        lat = detail[start:end]
                        start = detail.find("longitude")
                        start = detail.find(":", start) + 2
                        end = detail.find('}', start)
                        longt = detail[start:end]
                        start = detail.find('"telephone"')
                        start = detail.find(":", start)
                        start = detail.find('"', start) + 1
                        end = detail.find('"', start)
                        phone = detail[start:end]
                        maind = soup2.find('div', {'id': 'hours'})
                        hdetail = maind.find("ul", {'class': 'noList'})
                        hdetail = hdetail.findAll('li')
                        hours = ""
                        for li in hdetail:
                            hours = hours + li.text + " "
                        hours = re.sub(pattern, " ", hours)
                        hours = hours.replace("\n", "")
                        if len(hours) < 3:
                            hours = "<MISSING>"
                        if len(phone) < 5:
                            phone = "<MISSING>"
                        p += 1
                        flag = True
                        i = 0
                        while i < len(data) and flag:
                            if store == data[i][8] and street == data[i][3]:
                                flag = False
                                break
                            else:
                                i +=1
                        if flag:
                            data.append([
                                'https://www.lifestorage.com/',
                                link,
                                title,
                                street,
                                city,
                                state,
                                pcode,
                                ccode,
                                store,
                                phone,
                                "<MISSING>",
                                lat,
                                longt,
                                hours
                            ])
                    except:
                        pass
                


    return data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()


