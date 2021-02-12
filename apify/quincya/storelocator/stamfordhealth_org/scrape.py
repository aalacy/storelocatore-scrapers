import csv
import json
import re

from bs4 import BeautifulSoup

from sglogging import sglog

from sgrequests import SgRequests

log = sglog.SgLogSetup().get_logger(logger_name="stamfordhealth.org")


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

    base_link = "https://www.stamfordhealth.org/locations/search-results/"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()

    found_poi = []
    all_links = []

    for i in range(5):
        req = session.get(base_link, headers=headers)
        base = BeautifulSoup(req.text, "lxml")
        links = base.find_all(class_="Name")
        for link in links:
            all_links.append(link)
        try:
            base_link = (
                "https://www.stamfordhealth.org" + base.find(class_="Next")["href"]
            )
        except:
            break

    data = []

    locator_domain = "stamfordhealth.org"

    for raw_link in all_links:
        link = "https://www.stamfordhealth.org" + raw_link["href"].split("&")[0]
        log.info(link)
        req = session.get(link, headers=headers)
        base = BeautifulSoup(req.text, "lxml")

        try:
            script = (
                base.find("script", attrs={"type": "application/ld+json"})
                .text.replace("\n", "")
                .strip()
            )
            json_found = True
        except:
            json_found = False

        if json_found:
            store = json.loads(script)

            final_link = store["url"]

            location_name = store["name"].strip()
            street_address = store["address"]["streetAddress"].strip()
            street_address = (
                street_address.replace("Orthopedic and Spine Institute,", "")
                .replace("Stamford Health Tully Health Center,", "")
                .replace("Tully Health Center,", "")
                .strip()
            )

            if street_address + location_name in found_poi:
                continue
            found_poi.append(street_address + location_name)

            city = store["address"]["addressLocality"]
            try:
                state = store["address"]["addressRegion"]
            except:
                state = "<MISSING>"
            zip_code = store["address"]["postalCode"]
            country_code = "US"

            store_number = link.split("id=")[-1]
            try:
                location_type = ", ".join(
                    list(base.find(class_="facetServiceLine").ul.stripped_strings)
                )
            except:
                location_type = "<MISSING>"
            phone = store["telephone"]

            try:
                hours_of_operation = ""
                raw_hours = store["openingHoursSpecification"]
                for hours in raw_hours:
                    day = hours["dayOfWeek"].replace("http://schema.org/", "")
                    if len(day[0]) != 1:
                        day = " ".join(hours["dayOfWeek"])
                    opens = hours["opens"]
                    closes = hours["closes"]
                    if opens != "" and closes != "":
                        clean_hours = day + " " + opens + "-" + closes
                        hours_of_operation = (
                            hours_of_operation + " " + clean_hours
                        ).strip()

                days = [
                    "Monday",
                    "Tuesday",
                    "Wednesday",
                    "Thursday",
                    "Friday",
                    "Saturday",
                    "Sunday",
                ]
                for day in days:
                    if day.lower() not in hours_of_operation.lower():
                        hours_of_operation = hours_of_operation + " " + day + " Closed"
            except:
                hours_of_operation = "<MISSING>"

            try:
                latitude = store["geo"]["latitude"]
                longitude = store["geo"]["longitude"]
            except:
                latitude = "<MISSING>"
                longitude = "<MISSING>"

        else:
            item = base.find(id="PanelPediatricsContactInfo")
            if not item:
                continue
            location_name = item.strong.text.strip()

            raw_address = list(item.find_all("p")[1].stripped_strings)[:2]

            street_address = raw_address[0].strip()
            city_line = raw_address[-1].strip().split(",")
            city = city_line[0].strip()
            state = city_line[-1].strip().split()[0].strip()
            zip_code = city_line[-1].strip().split()[1].strip()
            country_code = "US"
            store_number = "<MISSING>"
            location_type = "<MISSING>"

            try:
                phone = re.findall(r"[\d]{3}-[\d]{3}-[\d]{4}", str(item))[0]
            except:
                phone = "<MISSING>"

            hours_of_operation = " ".join(
                list(item.find_all("p")[3].stripped_strings)
            ).replace("\xa0", " ")
            latitude = "<MISSING>"
            longitude = "<MISSING>"

            final_link = link

        data.append(
            [
                locator_domain,
                final_link,
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
