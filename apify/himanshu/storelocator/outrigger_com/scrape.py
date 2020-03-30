import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
# from selenium import webdriver
# from selenium.webdriver.firefox.options import Options




session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w', encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_ALL)
        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation",
                         "page_url"])
        # Body
        for row in data:
            writer.writerow(row)




def fetch_data():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
        # 'Content-Type': 'application/json',
    }

    return_main_object = []
    base_url = "https://www.outrigger.com"
    # it will used in store data.
    locator_domain = "https://www.outrigger.com"
    location_name = ""
    street_address = "<MISSING>"
    city = "<MISSING>"
    state = "<MISSING>"
    zipp = "<MISSING>"
    country_code = "US"
    store_number = "<MISSING>"
    phone = "<MISSING>"
    location_type = "outrigger"
    latitude = "<MISSING>"
    longitude = "<MISSING>"
    raw_address = ""
    hours_of_operation = "<MISSING>"
    page_url = "<MISSING>"

    r = session.get(
        "https://www.outrigger.com/hotels-resorts", headers=headers)
    soup = BeautifulSoup(r.text, "lxml")

    for view in soup.find_all('a',class_="promo-cta"):
        page_url = base_url + view['href']
        r1 = session.get(base_url+view['href'],headers = headers)
        soup_r1 = BeautifulSoup(r1.text,'lxml')
        div = soup_r1.find('p',class_ = "pdp-overview-promo-desc")
        if div != None:
            location_name = soup_r1.find('h1',class_="pdp-head-title").text.strip()
            # print(location_name)
            # print(div.prettify())
            # print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
            list_div = list(div.stripped_strings)
            # print(len(list_div))
            # print(list_div)
            # print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
            if len(list_div) == 5:
                # print(len(list_div))
                # print(list_div)
                # print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
                street_address = "".join(list_div[0])
                city = "".join(list_div[1].split(',')[0])
                # phone = "".join(list_div[2].replace("Ph:","").replace("T:","").strip())
                phone1 = "".join(list_div[2])
                phone_list = re.findall(re.compile(".?(\(?\d{3}\D{0,3}\d{3}\D{0,3}\d{4}).?"), str(phone1))
                # print(phone_list)
                if phone_list:
                    phone = phone_list[0]
                else:
                    phone = "<MISSING>"
                # print(phone)
                if len(list_div[1].split(',')[1].split()) == 2:

                    state = "".join(list_div[1].split(',')[1].split()[0])
                    zipp = "".join(list_div[1].split(',')[1].split()[-1])

                else:
                    state = "".join(list_div[1].split(',')[1].split()[0])
                    zipp = "<MISSING>"
                # print(street_address + " | " +city + " | "+ state + " | " + zipp)
            if len(list_div) == 6:
                street_address = "".join(list_div[0])
                city = "".join(list_div[1].split(',')[0])

                state = "".join(list_div[1].split(',')[1])
                zipp = "".join(list_div[1].split(',')[-1])
                phone = "".join(list_div[3].replace("Ph:","").strip())
                # print(street_address + " | " +city + " | "+ state + " | " + zipp + " | "+phone)
            if len(list_div) == 7:
                # print(len(list_div))
                # print(list_div)
                # print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
                street_address = "".join(list_div[1].split(',')[0])
                city = "".join(list_div[1].split(',')[1])
                state = "".join(list_div[1].split(',')[-1])
                phone1 = "".join(list_div[2])
                phone_list = re.findall(re.compile(".?(\(?\d{3}\D{0,3}\d{3}\D{0,3}\d{4}).?"), str(phone1))
                # print(phone_list)
                if phone_list:
                    phone = phone_list[0]
                else:
                    phone = "<MISSING>"
                zipp = "<MISSING>"
                # print(street_address + " | " +city + " | "+ state + " | " + zipp + " | "+phone)
            if len(list_div) == 8:
                street_address = "".join(list_div[1].split(',')[:-2])
                city = "".join(list_div[1].split(',')[-2])
                state = "".join(list_div[1].split(',')[-1].split()[0])
                zipp = "".join(list_div[1].split(',')[-1].split()[-1])
                phone= "".join(list_div[2].replace("T:","").strip())
                # print(street_address + " | " +city + " | "+ state + " | " + zipp + " | "+phone)
            if len(list_div) == 11:
                # print(len(list_div))
                # print(list_div)
                # print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
                saddress = list_div[0].split(',')
                if len(saddress) ==1:
                    street_address = "".join(saddress[0])
                else:
                    street_address ="".join(saddress[0])
                    city = "".join(saddress[-1])
                caddress = list_div[1].split(',')
                if len(caddress) ==1:
                    city = "<MISSING>"
                    state = "".join(caddress[0])
                else:
                    city = "".join(caddress[0])
                    state = "".join(caddress[-1])
                zipp= "<MISSING>"
                phone1 = "".join(list_div[2])
                phone_list = re.findall(re.compile(".?(\(?\d{3}\D{0,3}\d{3}\D{0,3}\d{4}).?"), str(phone1))
                # print(phone_list)
                if phone_list:
                    phone = phone_list[0]
                else:
                    phone = "<MISSING>"
                # print(street_address + " | " +city + " | "+ state + " | " + zipp + " | "+phone)
            if len(list_div) == 4:
                street_address = "".join(list_div[0])
                city = "".join(list_div[1].split(',')[0])
                state = "".join(list_div[1].split(',')[1].split()[0])
                zipp = "".join(list_div[1].split(',')[1].split()[-1])
                phone1 = "".join(list_div[2])
                phone_list = re.findall(re.compile(".?(\(?\d{3}\D{0,3}\d{3}\D{0,3}\d{4}).?"), str(phone1))
                # print(phone_list)
                if phone_list:
                    phone = phone_list[0]
                else:
                    phone = "<MISSING>"
                # print(street_address + " | " +city + " | "+ state + " | " + zipp + " | "+phone)

            if len(list_div) == 0:
                div = soup_r1.find('div',class_ = "pdp-overview-promo-info promo-content")
                list_div = list(div.stripped_strings)
                if len(list_div) == 10:
                    street_address = "".join(list_div[0])
                    city = "".join(list_div[1])
                    state = "".join(list_div[2].split()[0].strip())
                    zipp = "".join(list_div[2].split()[-1])
                    phone = "".join(list_div[3].replace("T:","").strip())
                    # print(street_address + " | " +city + " | "+ state + " | " + zipp + " | "+phone)
                else:

                    street_address = "".join(list_div[0])
                    city  = "".join(list_div[1].split(',')[0])
                    state = "".join(list_div[1].split(',')[-1].split()[0])
                    zipp = "".join(list_div[1].split(',')[-1].split()[-1])
                    phone1 = "".join(list_div[2])
                    phone_list = re.findall(re.compile(".?(\(?\d{3}\D{0,3}\d{3}\D{0,3}\d{4}).?"), str(phone1))
                    # print(phone_list)
                    if phone_list:
                        phone = phone_list[0]
                    else:
                        phone = "<MISSING>"
                    # print(street_address + " | " +city + " | "+ state + " | " + zipp + " | "+phone)
        else:
            location_name = soup_r1.find('div',class_ = "no-image").text.strip()

            div = soup_r1.find('div',class_ = "text-block").find("div",class_="col-md-6")
            # print(div)
            # print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~`")
            list_div = list(div.stripped_strings)
            street_address = "".join(list_div[0])
            city = "".join(list_div[1].split(',')[0])
            state = "".join(list_div[1].split(',')[1].split()[0])
            zipp = "".join(list_div[1].split(',')[1].split()[-1])
            phone1 = "".join(list_div[2])
            phone_list = re.findall(re.compile(".?(\(?\d{3}\D{0,3}\d{3}\D{0,3}\d{4}).?"), str(phone1))
            # print(phone_list)
            if phone_list:
                phone = phone_list[0]
            else:
                phone = "<MISSING>"
            # print(street_address + " | " +city + " | "+ state + " | " + zipp + " | "+phone)
        store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                         store_number, phone, location_type, latitude, longitude, hours_of_operation,page_url]
        store = ["<MISSING>" if x == "" else x for x in store]

        # if store[2] in addresses:
        #     continue
        # addresses.append(store[2])
        # print("data = " + str(store))
        # print(
        #     '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')

        return_main_object.append(store)
    return return_main_object





        # print(soup_r1.prettify())

    # locator_domain = base_url
    # location_name = ""
    # street_address = ""
    # city = ""
    # state = ""
    # zipp = ""
    # country_code = "US"
    # store_number = ""
    # phone = ""
    # location_type = ""
    # latitude = ""
    # longitude = ""
    # raw_address = ""
    # hours_of_operation = ""
    # page_url = ""

    # store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
    #          store_number, phone, location_type, latitude, longitude, hours_of_operation, page_url]

    # if str(store[1]) + str(store[2]) not in addresses and "coming soon" not in location_name.lower():
    #     addresses.append(str(store[1]) + str(store[2]))

    #     store = [x.encode('ascii', 'ignore').decode(
    #         'ascii').strip() if x else "<MISSING>" for x in store]

    #     # print("data = " + str(store))
    #     # print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
    #     yield store


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
