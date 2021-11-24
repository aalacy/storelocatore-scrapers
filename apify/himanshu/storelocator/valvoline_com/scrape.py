import csv
import re

from bs4 import BeautifulSoup

from sglogging import sglog

from sgrequests import SgRequests

from sgzip.dynamic import DynamicZipSearch, SearchableCountries

log = sglog.SgLogSetup().get_logger(logger_name="valvoline.com")

session = SgRequests()


def write_output(data):
    with open("data.csv", mode="w", newline="") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )
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
        for row in data:
            writer.writerow(row)


def fetch_data():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.129 Safari/537.36",
        "content-type": "application/x-www-form-urlencoded",
    }
    locator_domain = "https://www.valvoline.com/"
    addresses = []

    max_results = 500
    max_distance = 25

    search = DynamicZipSearch(
        country_codes=[SearchableCountries.USA],
        max_radius_miles=max_distance,
        max_search_results=max_results,
    )

    for postcode in search:
        log.info(
            "Searching: %s | Items remaining: %s" % (postcode, search.items_remaining())
        )
        data = (
            "scController=StoreLocatorUS&scAction=SubmitLocation&Zip="
            + str(postcode)
            + "&All-hidden=checked&Express-hidden=&HD-hidden=&VIOC-hidden=&Other-hidden=&All-hidden-retail=checked&HD-hidden-retail="
        )
        r = session.post(
            "https://www.valvoline.com/store-locator", headers=headers, data=data
        )
        soup = BeautifulSoup(r.text, "lxml")
        li = soup.find("li", {"data-content": "servicesLocations"})
        if li.find("div", class_="location"):
            for loc in li.find_all("div", class_="location"):
                latitude = loc["data-latitude"]
                longitude = loc["data-longitude"]
                search.found_location_at(latitude, longitude)
                location_type = "<MISSING>"
                city_state_zipp = loc["data-location"].split(",")
                city = city_state_zipp[0].strip()
                state = city_state_zipp[1].strip()
                zipp = city_state_zipp[-1].strip()
                country_code = "US"
                if " " in zipp:
                    country_code = "CA"
                location_name = loc.find("h5", class_="location-title").text.strip()
                full_address = list(
                    loc.find("p", class_="location-address").stripped_strings
                )
                street_address = full_address[0].strip()
                phone_list = re.findall(
                    re.compile(r".?(\(?\d{3}\D{0,3}\d{3}\D{0,3}\d{4}).?"),
                    str(" ".join(full_address)),
                )
                if phone_list:
                    phone = phone_list[0]
                else:
                    phone = "<MISSING>"
                hours_of_operation = "<MISSING>"
                try:
                    hours_of_operation = (
                        " ".join(
                            list(
                                loc.find("p", class_="location-hours").stripped_strings
                            )
                        )
                        .replace("Hours:", "")
                        .strip()
                    )
                except:
                    pass
                try:
                    page_url = loc.find("a", class_="gtm-locator-storeLink")["href"]
                except:
                    page_url = "<MISSING>"
                store_number = "<MISSING>"
                store = [
                    locator_domain,
                    location_name,
                    street_address,
                    city,
                    state,
                    zipp,
                    country_code,
                    store_number,
                    phone,
                    location_type,
                    latitude,
                    longitude,
                    hours_of_operation,
                    page_url,
                ]

                if str(store[2] + " " + store[-5]) not in addresses:
                    addresses.append(str(store[2] + " " + store[-5]))

                    store = [str(x).strip() if x else "<MISSING>" for x in store]
                    yield store


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
