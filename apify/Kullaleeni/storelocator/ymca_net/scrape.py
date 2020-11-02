import requests
from bs4 import BeautifulSoup
import csv
import string
import re, time
import usaddress
import sgzip
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('ymca_net')




def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(
            ["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code",
             "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    # Your scraper here
   

    MAX_RESULTS = 20  # max number of results the website gives
    MAX_DISTANCE = 50.0  # max number of distance from the zip it covers
    data = []
    p = 0
    pattern = re.compile(r'\s\s+')
    search = sgzip.ClosestNSearch()
    search.initialize()
    query_coord = search.next_zip()
    logger.info(query_coord)
    # 2:56
    while query_coord:
        count = 0
        result_coords = []  # mantain the list of coords of data collected
        # for s in range(0,len(states)):
        url = 'https://www.ymca.net/find-your-y/?address=' + query_coord
        logger.info(url)
        try:

            page = requests.get(url)
            soup = BeautifulSoup(page.text, "html.parser")
            mainul = soup.findAll('ul', {'class': 'find-y-page'})
            # logger.info(len(mainul))
            for ul in mainul:
                li_list = ul.findAll('li')
                count += len(li_list)  # to calculate total # of results
                for li in li_list:
                    
                    lat = li['data-latitude']
                    longt = li['data-longitude']
                    result_coords.append((lat, longt))  # add coords to list
                    link = li.find('a')

                    link = "https://www.ymca.net" + link['href']
                    try:
                        #link = 'https://www.ymca.net/y-profile/?id=2973'
                        page1 = requests.get(link)
                        soup1 = BeautifulSoup(page1.text, "html.parser")
                        soup1 = soup1.find('div', {'class': 'col-md-4'})
                        title = soup1.find('h1').text
                        mainp = soup1.findAll('p')
                        address = mainp[0].text
                        phone = address[address.find("Phone"):len(address)]
                        phone = phone.replace("Phone: ", "")
                        address = address[0: address.find("Phone")]
                        address = address.replace("\n", " ")
                        address = usaddress.parse(address)
                        i = 0
                        street = ""
                        city = ""
                        state = ""
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
                            if temp[1].find("ZipCode") != -1:
                                pcode = pcode + " " + temp[0]
                            i += 1

                        hours = mainp[2].text
                        hours = re.sub(pattern, " ", hours)
                        hours = hours.replace("\n", "")
                        phone = re.sub(pattern, "", phone)
                        phone = phone.replace("\n", "")
                        pcode = pcode.replace("\n", "")
                        pcode = pcode.lstrip()
                        street = street.lstrip()
                        city = city.lstrip()
                        city = city.replace(",", "")
                        state = state.lstrip()
                        hours = hours.lstrip()
                        hours = hours.replace("Hours of Operation:", "")

                        store = link[link.find("=") + 1:len(link)]
                        if len(phone) < 3:
                            phone = "<MISSING>"

                        if len(hours) < 3:
                            hours = "<MISSING>"
                        if len(store) < 3:
                            store = "<MISSING>"
                        if len(street) < 3:
                            street = "<MISSING>"
                        if len(lat) < 3:
                            lat = "<MISSING>"
                        if len(longt) < 3:
                            longt = "<MISSING>"
                        if len(city) < 3:
                            city = "<MISSING>"
                        #https://www.ymca.net/y-profile/?id=2973'
                        if len(state) < 2:
                            state = "<MISSING>"
                        else:
                            try:
                                state = state.lstrip()
                                temp,state = state.split(' ',1)
                            except:
                                pass
                        if len(pcode) < 3:
                            pcode = "<MISSING>"

                        try:
                            if pcode.find("/") > -1:
                                temp,pcode = pcode.split(' ',1)
                            else:
                                pcode, temp = pcode.split(' ', 1)
                        except:
                            pass


                        flag = True
                        m = 0
                        while m < len(data) and flag:
                            if store == data[m][8] and title == data[m][2] and state == data[m][5]:
                                flag = False
                                break
                            else:
                                m += 1
                        if flag:
                            data.append([
                                'https://www.ymca.net/',
                                link,
                                title,
                                street,
                                city,
                                state,
                                pcode,
                                "US",
                                store,
                                phone,
                                "<MISSING>",
                                lat,
                                longt,
                                hours
                            ])
                            #logger.info(p, ",", data[p])
                            p += 1

                    except Exception as e:
                        logger.info(link)
                        logger.info(e)
                        #pass
        except:
            #logger.info(url)
            #logger.info(e)
            pass
        #if count < MAX_RESULTS:  # check a near zip code
        #logger.info("max distance update")
        search.max_distance_update(MAX_DISTANCE)
        '''elif count == MAX_RESULTS:  # check to save lat lngs to find zip that excludes them
            logger.info("max count update")'''
        search.max_count_update(result_coords)
        #else:
         #   logger.info("oops! the maxcount should be", count)
          #  raise Exception("expected at most " + MAX_RESULTS + " results")

        query_coord = search.next_zip()

    return data


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
