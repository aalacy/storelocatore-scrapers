import csv
import re

from bs4 import BeautifulSoup

from sglogging import SgLogSetup

from sgrequests import SgRequests

logger = SgLogSetup().get_logger("cibc_com")


def write_output(data):
    with open("data.csv", mode="w", encoding="utf-8") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )

        # Header
        writer.writerow(
            [
                "locator_domain",
                "page_url",
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
            ]
        )
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()

    data = []
    found = []
    locator_domain = "cibc.com"

    provs = ["AB", "BC", "SK", "NS", "MB", "QC", "ON", "NT", "PE", "NL", "NU", "YT"]

    for prov in provs:
        logger.info(prov)
        state_link = "https://locations.cibc.com/" + prov.lower()
        req = session.get(state_link, headers=headers)
        base = BeautifulSoup(req.text, "lxml")

        city_links = base.find(class_="grid_12").find_all("a")
        for city_link in city_links:
            if "letter=" in str(city_link):
                continue
            for num in range(1, 100):
                base_link = (
                    "https://locations.cibc.com"
                    + city_link["href"]
                    + "?t=&page=%s&filters=filter-_-Branch" % (num)
                )
                req = session.get(base_link, headers=headers)
                base = BeautifulSoup(req.text, "lxml")

                try:
                    items = base.find(id="results_list").find_all("li")

                    all_scripts = base.find_all("script")
                except:
                    break

                for script in all_scripts:
                    if '"lat":' in str(script):
                        script = script.text
                        break
                lats = re.findall(r'lat":[0-9]{2}\.[0-9]+', script)
                lons = re.findall(r'lon":-[0-9]{2,3}\.[0-9]+', script)
                ids = re.findall(r'"id":"[0-9]+', script)

                for i, item in enumerate(items):
                    store_number = ids[i].split('"')[-1]
                    if store_number in found:
                        continue
                    found.append(store_number)

                    location_name = item.h2.text.strip()
                    if not location_name:
                        continue
                    street_address = item.find(
                        class_="line street-address"
                    ).text.strip()
                    city = item.find(class_="locality").text.strip()
                    state = item.find(class_="region").text.strip()
                    zip_code = item.find(class_="postal-code").text.strip()
                    country_code = "CA"
                    location_type = "Branch"
                    phone = item.find(class_="tel").text.strip()

                    if "temporary clos" in item.text.lower():
                        hours_of_operation = "Temporary Closure"
                    else:
                        try:
                            hours_of_operation = " ".join(
                                list(
                                    item.find(
                                        class_="locationHours bankHours"
                                    ).table.stripped_strings
                                )
                            )
                        except:
                            hours_of_operation = "<MISSING>"

                    if "closed branch" in hours_of_operation.lower():
                        hours_of_operation = "<MISSING>"

                    latitude = lats[i].split(":")[-1]
                    longitude = lons[i].split(":")[-1]

                    link = "https://locations.cibc.com" + item.a["href"]

                    data.append(
                        [
                            locator_domain,
                            link,
                            location_name,
                            street_address,
                            city,
                            state,
                            zip_code,
                            country_code,
                            store_number,
                            phone,
                            location_type,
                            latitude,
                            longitude,
                            hours_of_operation,
                        ]
                    )

                if not base.find("a", attrs={"aria-label": "Next page"}):
                    break

    # US locations
    base_link = "https://us.cibc.com/en/about-us/locations.html"
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    sections = base.find(class_="main-content").find_all(
        class_="column margins-padding no-sides large-padding-top medium-padding-bottom"
    )
    for section in sections:
        location_type = section.find(class_="sticky-inpage-anchor").text.strip()
        if location_type == "ATMs":
            continue
        logger.info(location_type)
        items = section.find_all(class_="container-content")
        for item in items:
            location_name = item.p.text.strip()

            raw_address = list(item.find_all("p")[1].stripped_strings)[1:]

            street_address = " ".join(raw_address[:-1]).strip()
            if street_address in found:
                continue
            found.append(street_address)

            logger.info(location_name)

            if "Three Embarcadero Center Suite 1600" in street_address:
                street_address = "Three Embarcadero Center Suite 1600"
                city = "San Francisco"
                state = "California"
                zip_code = "94111"
            elif "3290 Northside Parkway NW 7th Floor" in street_address:
                street_address = "3290 Northside Parkway NW 7th Floor"
                city = "Atlanta"
                state = "Georgia"
                zip_code = "30327"
            else:
                city_line = raw_address[-1].strip().split(",")
                city = city_line[0].strip()
                state = city_line[-1].strip().split()[0].strip()
                zip_code = city_line[-1].strip().split()[1].strip()

            if "34901 Woodward Avenue Suite 200" in street_address:
                street_address = "34901 Woodward Avenue Suite 200"
                city = "Birmingham"

            if "425 Lexington Avenue" in street_address:
                state = "New York"
                zip_code = "10017"

            if "1177 Avenue of the Americas" in street_address:
                state = "New York"
                zip_code = "10036"

            country_code = "US"
            store_number = "<MISSING>"

            try:
                phone = re.findall(r"[\d]{3}-[\d]{3}-[\d]{4}", str(item))[0]
            except:
                try:
                    phone = re.findall(r"[\d]{3}.+[\d]{3}-[\d]{4}", str(item))[0]
                except:
                    phone = "<MISSING>"

            hours_of_operation = (
                item.find_all("p")[3].text.split("Please call")[0].strip()
            )
            if "not available" in hours_of_operation:
                hours_of_operation = (
                    item.find_all("p")[2].text.split("Please call")[0].strip()
                )

            hours_of_operation = (
                hours_of_operation.replace("Office Hours", "")
                .replace("Lobby Hours", "")
                .strip()
            )

            if "closed branch" in hours_of_operation.lower():
                hours_of_operation = "<MISSING>"

            latitude = "<MISSING>"
            longitude = "<MISSING>"

            data.append(
                [
                    locator_domain,
                    base_link,
                    location_name,
                    street_address,
                    city,
                    state,
                    zip_code,
                    country_code,
                    store_number,
                    phone,
                    location_type,
                    latitude,
                    longitude,
                    hours_of_operation,
                ]
            )

    return data


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
