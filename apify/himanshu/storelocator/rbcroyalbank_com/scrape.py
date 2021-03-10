import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import time
from sgzip.dynamic import DynamicZipSearch, SearchableCountries
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("rbcroyalbank_com")
session = SgRequests()


def write_output(data):
    with open("data.csv", mode="w") as output_file:
        writer = csv.writer(
            output_file,
            delimiter=",",
            quotechar='"',
            quoting=csv.QUOTE_ALL,
            lineterminator="\n",
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


def request_wrapper(url, method, headers, data=None):
    request_counter = 0
    if method == "get":
        while True:
            try:
                r = session.get(url, headers=headers)
                return r
                break
            except:
                time.sleep(2)
                request_counter = request_counter + 1
                if request_counter > 10:
                    return None
                    break
    elif method == "post":
        while True:
            try:
                if data:
                    r = session.post(url, headers=headers, data=data)
                else:
                    r = session.post(url, headers=headers)
                return r
                break
            except:
                time.sleep(2)
                request_counter = request_counter + 1
                if request_counter > 10:
                    return None
                    break
    else:
        return None


def fetch_data():

    addressess = []
    search = DynamicZipSearch(
        country_codes=[SearchableCountries.CANADA],
        max_radius_miles=50,
        max_search_results=200,
    )

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36",
        "x-requested-with": "XMLHttpRequest",
        "referer": "https://www.thetinfishrestaurants.com/locations-menus/find-a-tin-fish-location-near-you/",
        "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
    }
    for coord in search:
        result_coords = []
        locator_domain = "https://www.rbcroyalbank.com"
        location_name = ""
        street_address = ""
        city = ""
        state = ""
        zipp = ""
        country_code = "CA"
        store_number = ""
        phone = ""
        location_type = ""
        latitude = ""
        longitude = ""
        hours_of_operation = ""
        page_url = ""
        data = "useCookies=1&lang=&q=" + str(coord) + "&searchBranch=1&searchATM=1"

        try:
            r = session.post(
                "https://maps.rbcroyalbank.com/index.php", headers=headers, data=data
            )
        except:
            continue

        soup = str(BeautifulSoup(r.text, "lxml"))
        if "markerData[1]" in soup:
            script = (
                soup.split("markerData[1]=")[1]
                .split("=true;for(var")[0]
                .split("{label:")
            )
            for i in range(len(script))[1:]:
                latitude = script[i].split("lat:")[1].split(",")[0]
                longitude = script[i].split("lat:")[1].split(",")[1].split("lng:")[1]
                id1 = script[i].split("locationId:'")[1].split("',t")[0]
                http = (
                    "https://maps.rbcroyalbank.com/locator/locationDetails.php?l="
                    + str(id1)
                )
                r1 = request_wrapper(http, "post", headers=headers, data=data)
                if r1 is None:
                    continue
                soup1 = BeautifulSoup(r1.text, "lxml")

                loc_dat = soup1.find(
                    "table",
                    {
                        "width": "380px",
                        "border": "0",
                        "cellspacing": "0",
                        "cellpadding": "2",
                    },
                )
                loc_dat1 = soup1.find(
                    "table",
                    {
                        "width": "402px",
                        "border": "0",
                        "cellspacing": "0",
                        "cellpadding": "2",
                    },
                )

                if loc_dat1 is not None:
                    location_name = list(loc_dat1.stripped_strings)[0]
                    street_address = list(loc_dat1.stripped_strings)[1]
                    city_state_zipp = (
                        list(loc_dat1.stripped_strings)[2].strip().lstrip()
                    )

                    ca_zip_list = re.findall(
                        r"[A-Z]{1}[0-9]{1}[A-Z]{1}\s*[0-9]{1}[A-Z]{1}[0-9]{1}",
                        str(city_state_zipp),
                    )
                    us_zip_list = re.findall(
                        re.compile(r"\b[0-9]{5}(?:-[0-9]{4})?\b"), str(city_state_zipp)
                    )
                    state_list = re.findall(r" ([A-Z]{2})", str(city_state_zipp))
                    location_type = "ATM"

                    if ca_zip_list:
                        zipp = ca_zip_list[-1]
                        country_code = "CA"

                    if us_zip_list:
                        zipp = us_zip_list[-1]
                        country_code = "US"

                    if state_list:
                        state = state_list[-1]

                    city = (
                        city_state_zipp.replace(zipp, "")
                        .replace(state, "")
                        .replace(",", "")
                    )

                if loc_dat is not None:
                    location_name = list(loc_dat.stripped_strings)[0]
                    street_address = list(loc_dat.stripped_strings)[1]
                    city_state_zipp = list(loc_dat.stripped_strings)[2].strip().lstrip()
                    ca_zip_list = re.findall(
                        r"[A-Z]{1}[0-9]{1}[A-Z]{1}\s*[0-9]{1}[A-Z]{1}[0-9]{1}",
                        str(city_state_zipp),
                    )
                    us_zip_list = re.findall(
                        re.compile(r"\b[0-9]{5}(?:-[0-9]{4})?\b"), str(city_state_zipp)
                    )
                    state_list = re.findall(r" ([A-Z]{2})", str(city_state_zipp))
                    location_type = "Branch"

                    if ca_zip_list:
                        zipp = ca_zip_list[-1]
                        country_code = "CA"

                    if us_zip_list:
                        zipp = us_zip_list[-1]
                        country_code = "US"

                    if state_list:
                        state = state_list[-1]

                    city = (
                        city_state_zipp.replace(zipp, "")
                        .replace(state, "")
                        .replace(",", "")
                    )
                    phone = "<MISSING>"
                    hours_of_operation = " ".join(list(loc_dat.stripped_strings)[8:22])

                if location_name == "Important":
                    location_name = "RBC On Campus Laurier University"
                if city == "RBC On Campus Laurier University":
                    city = "Waterloo"
                if (
                    street_address
                    == "This branch is temporarily closed. Please consider using Online Banking or the Mobile app to meet your banking needs during this time, or search for the next closest branch in your area."
                ):
                    street_address = "75 University Ave W"
                else:
                    pass
                store = []
                result_coords.append((latitude, longitude))
                store.append(locator_domain if locator_domain else "<MISSING>")
                store.append(location_name if location_name else "<MISSING>")
                store.append(street_address if street_address else "<MISSING>")
                store.append(city.strip() if city else "<MISSING>")
                store.append(state.strip() if state else "<MISSING>")
                store.append(zipp if zipp else "<MISSING>")
                store.append(country_code if country_code else "<MISSING>")
                store.append(store_number if store_number else "<MISSING>")
                store.append(phone if phone else "<MISSING>")
                store.append(location_type if location_type else "<MISSING>")
                store.append(latitude if latitude else "<MISSING>")
                store.append(longitude if longitude else "<MISSING>")
                store.append(hours_of_operation if hours_of_operation else "<MISSING>")
                store.append(page_url if page_url else "<MISSING>")

                if store[2] in addressess:
                    continue
                addressess.append(store[2])

                yield store


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
