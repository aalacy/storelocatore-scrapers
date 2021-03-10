import csv
import json

from bs4 import BeautifulSoup

from sgrequests import SgRequests


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

    # API scrape
    api_link = "https://c2b-services.bmw.com/c2b-localsearch/services/cache/v4/ShowAll?country=ca&category=BD&clientid=UX_NICCE_FORM_DLO"

    req = session.get(api_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    js = base.text.split('"data":')[1].split(',"count"')[0]

    items = json.loads(js)["pois"]

    data = []
    api_data = []
    found = []

    locator_domain = "bmw-motorrad.ca"

    for item in items:

        location_name = item["name"].strip()
        street_address = item["street"].strip()
        if street_address[-1:] == ",":
            street_address = street_address[:-1]
        city = item["city"].split(",")[0].strip()
        state = item["state"].strip()
        zip_code = item["postalCode"].strip()
        country_code = item["countryCode"].strip()
        store_number = item["attributes"]["agDealerCode"].split(",")[0].strip()
        location_type = "<MISSING>"
        phone = item["attributes"]["phone"].strip()
        hours_of_operation = "<MISSING>"
        latitude = item["lat"]
        longitude = item["lng"]
        link = item["attributes"]["homepage"].strip()
        if not link:
            link = "<MISSING>"

        api_data.append(
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

    # Final scrape
    base_link = (
        "https://www.bmw-motorrad.ca/en/public-pool/content-pool/dealerlocator.html"
    )

    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    locator_domain = "bmw-motorrad.ca"

    js = base.find(class_="module dealerlocator nosection")["data-nsc-dealers"]

    stores = json.loads(js)["dealers"]

    for store in stores:
        location_name = store["dealerName"].strip()
        store_number = store["contact"]["distributionPartnerId"]
        if store_number:
            if store_number in found:
                continue
            found.append(store_number)
        if location_name:
            street_address = store["contact"]["address"]["dealerStreet"]
            city = store["contact"]["address"]["dealerCity"]
            state = store["contact"]["address"]["addressQuery"].split(",")[2].strip()
            zip_code = store["contact"]["address"]["dealerPostCode"]
            country_code = "CA"
            location_type = "<MISSING>"
            phone = store["contact"]["phone"]
            latitude = "<MISSING>"
            longitude = "<MISSING>"
            for row in api_data:
                if (
                    row[8].replace("21861", "09238").replace("33022", "33021")[1:]
                    == store_number[1:]
                ):
                    latitude = row[-3]
                    longitude = row[-2]
                    break
            link = "https://www.bmw-motorrad.ca" + store["dealerHomePage"]
            if link:
                req = session.get(link, headers=headers)
                base = BeautifulSoup(req.text, "lxml")
                hours_of_operation = " ".join(
                    list(base.find(class_="dealerheader__items").stripped_strings)
                )
            else:
                link = "<MISSING>"
                hours_of_operation = ""
                raw_hours = store["times"]["openingTimes"]
                for raw_hour in raw_hours:
                    hours_of_operation = (
                        hours_of_operation
                        + " "
                        + raw_hour["daysLabel"]
                        + " "
                        + raw_hour["time"][0]["from"]
                        + "-"
                        + raw_hour["time"][0]["to"]
                    ).strip()

        else:
            if store_number:
                for row in api_data:
                    if (
                        row[8].replace("21861", "09238").replace("33022", "33021")[1:]
                        == store_number[1:]
                    ):
                        link = row[1]
                        location_name = row[2]
                        street_address = row[3]
                        city = row[4]
                        state = row[5]
                        zip_code = row[6]
                        country_code = "CA"
                        location_type = "<MISSING>"
                        phone = row[9]
                        latitude = row[-3]
                        longitude = row[-2]
                        try:
                            hours_of_operation = ""
                            raw_hours = store["times"]["openingTimes"]
                            for raw_hour in raw_hours:
                                hours_of_operation = (
                                    hours_of_operation
                                    + " "
                                    + raw_hour["daysLabel"]
                                    + " "
                                    + raw_hour["time"][0]["from"]
                                    + "-"
                                    + raw_hour["time"][0]["to"]
                                ).strip()
                        except:
                            hours_of_operation = "<MISSING>"
                        break
            else:
                continue

        if link in found:
            continue
        found.append(link)

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

    # Append data found in api but not in page_source
    for row in api_data:
        lat = row[-3]
        lat_found = False
        for i in data:
            if lat == i[-3]:
                lat_found = True

        if not lat_found:
            data.append(row)

    return data


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
