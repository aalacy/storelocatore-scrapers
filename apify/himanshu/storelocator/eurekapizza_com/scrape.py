import csv
import requests
from bs4 import BeautifulSoup
import re
import io
import json

def write_output(data):
    with open('data.csv', mode='w', encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'
    }
    base_url = "https://www.eurekapizza.com/locations/"
    r = requests.get(base_url, headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    return_main_object = []
    data = soup.find("div", {"id": "1260607478"})

    for semi_part in data.find_all("div", {"class": "dmRespCol"}):
        if(semi_part.find("div",{"class":"dmNewParagraph"})):
            inner_semi = semi_part.find("div",{"class":"dmNewParagraph"})
            temp_storeaddresss = list(inner_semi.stripped_strings)
            if(len(temp_storeaddresss) != 1):
                location_name = temp_storeaddresss[0]
                street_address = temp_storeaddresss[1]
                city = temp_storeaddresss[2].split(",")[0]
                state_zip = temp_storeaddresss[2].split(",")[1]
                state = state_zip.split(" ")[1]
                zip = state_zip.split(" ")[2]
                lat = semi_part.find("div",{"class":"inlineMap"})['data-lat']
                lng = semi_part.find("div",{"class":"inlineMap"})['data-lng']
                link = semi_part.find("a",{"class":"dmDefaultGradient"})['href']
                if("http" in link):
                    page_url = link
                    store_request = requests.get(link)
                    store_soup = BeautifulSoup(store_request.text, "lxml")

                    if(store_soup.find("td",{"id":"ctl00_BP_Content_uRestaurantHeader_tdHours"})):
                        inner_semi_hr = store_soup.find("td",{"id":"ctl00_BP_Content_uRestaurantHeader_tdHours"})
                        temp_hr = list(inner_semi_hr.stripped_strings)
                        hour = ' '.join(map(str, temp_hr))

                    elif(store_soup.find("div",{"class":"restaurant-hours hours"})):
                        inner_semi_hr = store_soup.find("div",{"class":"restaurant-hours hours"})
                        temp_hr = list(inner_semi_hr.stripped_strings)
                        hour = ' '.join(map(str, temp_hr))
                    else:
                        hour = "<INACCESSIBLE>"
                else:
                    hour = "<MISSING>"
                    page_url = "<MISSING>"
                phone = list(semi_part.find_all("span", {"class": "text"})[1].stripped_strings)[0]

                return_object = []
                return_object.append('https://www.eurekapizza.com/')
                return_object.append(location_name)
                return_object.append(street_address)
                return_object.append(city)
                return_object.append(state)
                return_object.append(zip)
                return_object.append("US")
                return_object.append("<MISSING>")
                return_object.append(phone)
                return_object.append("<MISSING>")
                return_object.append(lat)
                return_object.append(lng)
                return_object.append(hour)
                return_object.append(page_url)
                # print("data === "+str(return_object))
                # print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
                return_main_object.append(return_object)

    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)
scrape()
