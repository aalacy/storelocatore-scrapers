from sgrequests import SgRequests
from bs4 import BeautifulSoup
import csv
import re



session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip",
                         "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():

    base_link = "http://hotnjuicycrawfish.com/locations"

    user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
    headers = {'User-Agent': user_agent}

    req = session.get(base_link, headers=headers)

    try:
        base = BeautifulSoup(req.text, "lxml")
    except (BaseException):
        pass
        # print('[!] Error Occured. ')
        # print('[?] Check whether system is Online.')

    items = base.findAll('div', class_="iconbox-wrapper")

    data = []
    for item in items:
        # print(item.a["href"])
        locator_domain = "hotnjuicycrawfish.com"
        try:
            page_link = "http://hotnjuicycrawfish.com" + item.a["href"]

            city_text = item.find('h4').text
            city = city_text[:city_text.find(',')].title()
            if "Planet" in city:
                city = "Las Vegas"
        except:
            continue
            # commingsoon
            # print(page_link)
        req = session.get(page_link, headers=headers)

        try:
            new_base = BeautifulSoup(req.text, "lxml")
        except (BaseException):
            pass
            # print('[!] Error Occured. ')
            # print('[?] Check whether system is Online.')

        location_name = new_base.find('title').text
        location_name = location_name[:location_name.find("-")].strip()
        raw_data = new_base.find('div', attrs={
                                 'class': 'sub-text updates info _2-lines'}).text.replace("Â\xa0", " ")
        street_address = " ".join(raw_data.split(",")[:-1]).replace("Las Vegas", "").replace("Orlando", "").replace("NW Washington", "").replace("Fountain Valley", "").replace(
            "Henderson", "").replace("Tempe", "").replace("Falls Church", "").replace("Glendale", "").replace("Phoenix", "").replace("West Hollywood", "").replace("New York", "").replace("Flushing", "").strip()
        # print(street_address)
        state = raw_data[raw_data.rfind(',') + 1:raw_data.rfind(' ')].strip()
        zip_code = raw_data[raw_data.rfind(' '):].strip()
        country_code = "US"
        store_number = "<MISSING>"
        try:
            phone = new_base.find(
                'div', attrs={'class': 'information w-clearfix'}).text
            if "COMINGÂ SOON" == phone:
                continue
            # print(phone)

        except:
                # print(page_link)
            phone_tag = " ".join(
                list(new_base.find("div", class_="information").stripped_strings))
            try:
                phone = re.findall(re.compile(
                    ".?(\(?\d{3}\D{0,3}\d{3}\D{0,3}\d{4}).?"), str(phone_tag))[-1]

            except:
                phone = "<MISSING>"
        # print(phone)

        page_url = page_link
        location_type = "<MISSING>"
        link = new_base.find('iframe')['src']
        start_point = link.find("2d") + 2
        longitude = link[start_point:link.find('!', start_point)]
        long_start = link.find('!', start_point) + 3
        latitude = link[long_start:link.find('!', long_start)]

        hours_of_operation = new_base.find('div', attrs={'class': 'update pad-bottom'}).get_text(
            separator=u' ').replace("\n", " ").replace("  ", " ").strip()
        hours_of_operation = re.sub(
            ' +', ' ', hours_of_operation).replace("Hours", "").strip()

        data.append([locator_domain, location_name, street_address, city, state, zip_code,
                     country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation, page_url])

    return data


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
