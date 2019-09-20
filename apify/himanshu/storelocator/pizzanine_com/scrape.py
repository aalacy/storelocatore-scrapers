import csv
import requests
from bs4 import BeautifulSoup
import re
import json


def write_output(data):
    with open('data.csv', 'w') as output_file:
        writer = csv.writer(output_file, delimiter=",")

        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])

        # print("data::" + str(data))
        for i in data or []:
            writer.writerow(i)


def fetch_data():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
    }

    base_url = "https://pizzanine.com"
    r = requests.get(
        "https://pizzanine.com", headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    # print(soup.prettify())

    return_main_object = []
    # it will used in store data.
    locator_domain = base_url
    location_name = ""
    street_address = "<MISSING>"
    city = "<MISSING>"
    state = "<MISSING>"
    zipp = "<MISSING>"
    country_code = "US"
    store_number = "<MISSING>"
    phone = "<MISSING>"
    location_type = "pepes"
    latitude = "<MISSING>"
    longitude = "<MISSING>"
    raw_address = ""
    hours_of_operation = "<MISSING>"

    # for val in soup.find('div', {'id': 'mainNavigation'}).find("div",class_="folder").find('div', class_="subnav").find_all('div', class_="external"):
    #     print(val)
    for val in soup.find('div', {'id': 'headerNav'}).find('div', class_="folder").find_all("a"):
        if "/locations-order-online" != val['href']:
            r_loc = requests.get(base_url + val['href'], headers=headers)
            soup_loc = BeautifulSoup(r_loc.text, "lxml")

            content_inner = soup_loc.find(
                "div", class_="content-inner").find('div', class_="sqs-row")
            # print(content_inner.prettify())
            location_name = content_inner.find('h1').text.replace("\xa0", " ")
            if "WE DELIVER" != content_inner.find('h2').text:
                phone = content_inner.find('h2').text
            if "WE DELIVER" == content_inner.find('h2').text:
                phone = soup_loc.find(
                    "div", class_="content-inner").find('div', class_="sqs-row").find('p').find('a').text

            if content_inner.find('h2').nextSibling is not None:
                address = content_inner.find('h2').nextSibling
                list_address = list(address.stripped_strings)
                street_address = " ".join(list_address)
            else:
                street_address = "<MISSING>"
                zipp = "<MISSING>"
            if content_inner.find('h2').nextSibling is not None:
                if content_inner.find('h2').nextSibling.nextSibling is not None and "Due to construction on Southern, delivery times will be longer. " != content_inner.find('h2').nextSibling.nextSibling.text:
                    details = content_inner.find(
                        'h2').nextSibling.nextSibling.text.split(',')
                    city = "".join(details[0].strip())
                    state = "".join(details[1].split()[0].strip())
                    zipp = "".join(details[1].split()[-1].strip())

                else:
                    city = content_inner.find('h1').text.split(",")[0]
                    state = content_inner.find(
                        'h1').text.split(",")[1].split()[0]
                    zipp = "<MISSING>"
            if "/rio-rancho" == val['href']:
                content_inner_next = soup_loc.find(
                    "div", class_="content-inner").find('div', class_="sqs-row").find("div", class_="span-12").find("div", class_="row sqs-row").find('div', class_="sqs-block-html")
                hours_of_operation = "".join(
                    content_inner_next.text.replace("\xa0", " ").split("Hours")[1].strip())

            if "/gallup" == val['href'] or "/santa-fe" == val['href']:
                content_inner_next = soup_loc.find("div", class_="content-inner").find('div', class_="sqs-row").find(
                    "div", class_="span-12").find("div", class_="row sqs-row").nextSibling.find('div', class_="col").nextSibling
                hours_of_operation = "".join(
                    content_inner_next.text.replace("\xa0", " ").split("Hours")[1].strip())
                # print(hours_of_operation)
            if "/gallup" != val['href'] and "/santa-fe" != val['href'] and "/rio-rancho" != val['href'] and "/albuquerque" != val['href']:
                content_inner_next = soup_loc.find("div", class_="content-inner").find(
                    'div', class_="sqs-row").nextSibling.find("div", class_="col").nextSibling
                hours_of_operation = "".join(
                    content_inner_next.text.replace("\xa0", " ").split("HOURS"))
            store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                     store_number, phone, location_type, latitude, longitude, hours_of_operation]
            store = ["<MISSING>" if x == "" else x for x in store]
            return_main_object.append(store)
            # print("data = " + str(store))
            # print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')

        if "/albuquerque" == val['href']:
            for content_inner_next in soup_loc.find("div", class_="content-inner").find(
                    'div', class_="sqs-row").nextSibling.find_all('div', class_="col"):
                for inner_details in content_inner_next.find_all(
                        'div', class_="sqs-block-html"):
                    for location_page in inner_details.find_all('a'):
                            # print(location_page['href'])
                        result_loc = requests.get(
                            base_url + location_page['href'], headers=headers)

                        result_soup = BeautifulSoup(
                            result_loc.text, "lxml")
                        content_inner = result_soup.find(
                            "div", class_="content-inner").find('div', class_="sqs-row")

                        location_name = content_inner.find(
                            'h1').text.replace("\xa0", "")
                        phone = content_inner.find('h1').nextSibling.text
                        if "WE ARE NOW OPEN!!!" != content_inner.find('h1').nextSibling.nextSibling.text and "We will be closing at 1:00 pm for the 4th of July." != content_inner.find(
                                'h1').nextSibling.nextSibling.text:
                            street_address = content_inner.find(
                                'h1').nextSibling.nextSibling.text
                            city = content_inner.find(
                                'h1').nextSibling.nextSibling.nextSibling.text.split(",")[0].strip()
                            state = content_inner.find(
                                'h1').nextSibling.nextSibling.nextSibling.text.split(",")[1].split()[0].strip()
                            zipp = content_inner.find(
                                'h1').nextSibling.nextSibling.nextSibling.text.split(",")[1].split()[1].strip()
                            # print(city, state, zipp)

                        else:
                            street_address = content_inner.find(
                                'h1').nextSibling.nextSibling.nextSibling.text
                            city = content_inner.find(
                                'h1').nextSibling.nextSibling.nextSibling.nextSibling.text.split(",")[0].strip()
                            state = content_inner.find(
                                'h1').nextSibling.nextSibling.nextSibling.nextSibling.text.split(",")[1].split()[0].strip()
                            zipp = content_inner.find(
                                'h1').nextSibling.nextSibling.nextSibling.nextSibling.text.split(",")[1].split()[1].strip()
                            # print(city, state, zipp)
                        if "/eubank" != location_page['href'] and "/louisiana" != location_page['href']:
                            hours = result_soup.find(
                                "div", class_="content-inner").find('div', class_="sqs-row").nextSibling.find('div', class_="col").nextSibling
                            hours_of_operation = "".join(
                                hours.text.replace("\xa0", " ").split("HOURS"))
                            # print(hours_of_operation)

                        else:
                            hours = result_soup.find("div", class_="content-inner").find('div', class_="sqs-row").find(
                                "div", class_="span-12").find("div", class_="row sqs-row").nextSibling.find('div', class_="col").nextSibling
                            hours_of_operation = "".join(
                                hours.text.replace("\xa0", " ").split("HOURS"))
                            # print(hours_of_operation)

                        store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                                 store_number, phone, location_type, latitude, longitude, hours_of_operation]
                        store = ["<MISSING>" if x == "" else x for x in store]
                        return_main_object.append(store)
                        # print("data = " + str(store))
                        # print(
                        #     '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
