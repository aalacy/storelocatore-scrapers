import csv
import re
import time

from bs4 import BeautifulSoup

from sgrequests import SgRequests

from sgselenium import SgChrome


def write_output(data):
    with open("data.csv", mode="w") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )

        # Header
        writer.writerow(
            [
                "locator_domain",
                "location_name",
                "street_address",
                "city",
                "state",
                "zip",
                "country_code",
                "store_number",
                "phone",
                "location_type",
                "latitude",
                "longitude",
                "hours_of_operation",
                "page_url",
            ]
        )
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():

    driver = SgChrome().driver()

    url = "https://stores.worldmarket.com/index.html"
    locator_domain = "https://www.worldmarket.com"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(url, headers=headers)

    base = BeautifulSoup(req.text, "lxml")

    locs = base.find_all(class_="c-directory-list-content-item-link")
    link_list = []
    state_list = []
    city_list = []
    for loc in locs:
        link = "https://stores.worldmarket.com/" + loc["href"]

        if len(link) > 38:

            if "brooklyn.html" in link:
                city_list.append(link)
            else:
                link_list.append(link)
        else:
            state_list.append(link)

    for link in state_list:
        req = session.get(link, headers=headers)
        base = BeautifulSoup(req.text, "lxml")
        cities = base.find_all(class_="c-directory-list-content-item-link")
        for city in cities:

            city_link = "https://stores.worldmarket.com/" + city["href"]

            if len(city_link.split("/")) > 5:
                link_list.append(city_link)
            else:
                city_list.append(city_link)

    for link in city_list:
        req = session.get(link, headers=headers)
        base = BeautifulSoup(req.text, "lxml")

        in_cities = base.find_all(class_="c-location-grid-item-name-link")
        for loc in in_cities:
            if "http" in loc["href"]:
                link = loc["href"]
            else:
                link = ("https://stores.worldmarket.com/" + loc["href"]).replace(
                    "../", ""
                )
            link_list.append(link)

    all_store_data = []
    for link in link_list:
        req = session.get(link, headers=headers)
        item = BeautifulSoup(req.text, "lxml")
        is_bed = False

        try:
            location_name = item.find(id="location-name").text.strip()
        except:
            if "bedbathandbeyond" in req.url:
                is_bed = True
            else:
                continue

        if not is_bed:
            if "COMING SOON" in location_name.upper():
                continue

            street_address = item.find(class_="c-address-street-1").text.strip()
            try:
                street_address = (
                    street_address
                    + " "
                    + item.find(class_="c-address-street-2").text.strip()
                )
                street_address = street_address.strip()
            except:
                pass

            city = item.find(class_="c-address-city").text.replace(",", "").strip()
            state = item.find(class_="c-address-state").text.strip()
            zip_code = item.find(class_="c-address-postal-code").text.strip()

            try:
                phone = item.find(id="telephone").text.strip()
                if not phone:
                    phone = "<MISSING>"
            except:
                phone = "<MISSING>"

            lat = item.find("meta", attrs={"itemprop": "latitude"})["content"]
            longit = item.find("meta", attrs={"itemprop": "longitude"})["content"]

            try:
                hours = " ".join(
                    list(item.find(class_="c-location-hours-details").stripped_strings)
                )
            except:
                hours = "<MISSING>"

        else:
            driver.get(link)
            time.sleep(6)
            location_name = driver.find_element_by_id("liberty-concept").get_attribute(
                "title"
            )

            street_address = driver.find_element_by_xpath(
                '//span[@itemprop="streetAddress"]'
            ).text
            city = (
                driver.find_element_by_xpath('//span[@itemprop="addressLocality"]')
                .text.replace(",", "")
                .strip()
            )
            hours = (
                driver.find_element_by_id("store-hours")
                .text.replace("Store Hours", "")
                .replace("/n", " ")
                .replace("SAT", "SAT ")
                .replace("SUN", "SUN ")
            )
            hours = " ".join(hours.split())

            geo = re.findall(
                r"[0-9]{2}\.[0-9]+,-[0-9]{2,3}\.[0-9]+", driver.page_source
            )[0].split(",")
            lat = geo[0]
            longit = geo[1]

            phone = (
                driver.find_element_by_xpath("//span[contains(text(), 'World Market')]")
                .text.replace("World Market", "")
                .strip()
            )

            state = driver.find_element_by_xpath(
                '//span[@itemprop="addressRegion"]'
            ).text
            zip_code = "11232"

        country_code = "US"
        store_number = "<MISSING>"
        location_type = "<MISSING>"
        page_url = link

        store_data = [
            locator_domain,
            location_name,
            street_address,
            city,
            state,
            zip_code,
            country_code,
            store_number,
            phone,
            location_type,
            lat,
            longit,
            hours,
            page_url,
        ]
        all_store_data.append(store_data)

    driver.close()
    return all_store_data


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
