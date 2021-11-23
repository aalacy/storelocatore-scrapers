import csv
import json
import time
from sgrequests import SgRequests
from sgselenium import SgChrome

session = SgRequests()


def get_headers(url, requestName, headerIdent):
    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36"
    with SgChrome(is_headless=True, user_agent=user_agent) as driver:
        driver.get(url)
        time.sleep(3)
        for r in driver.requests:
            if requestName in r.path and r.headers[headerIdent]:
                return r.headers


def fetch_data():
    data = []
    url = "https://api.papaginos.com/api/v2/locations"
    headers = get_headers(
        "https://www.papaginos.com/locations", "api/v2/locations", "Authorization"
    )

    r = session.get(url, headers=headers, verify=False)
    loclist = json.loads(r.text)

    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
    }

    for loc in loclist:
        title = loc["name"]
        store = loc["number"]
        sublink = "https://locations.papaginos.com/" + str(store)
        lat = loc["latitude"]
        long = loc["longitude"]
        r = session.get(sublink, headers=headers)
        r = r.text
        street = r.split('itemprop="streetAddress">', 1)[1].split("</span> </span>", 1)[
            0
        ]
        try:
            street1 = street.split('"c-address-street-1 ">', 1)[1].split("</span>", 1)[
                0
            ]
            street2 = street.split('"c-address-street-2 break-before">', 1)[1]
            street = street1 + " " + street2
        except:
            street = street.split('"c-address-street-1 ">', 1)[1]
        city = r.split('<span itemprop="addressLocality">', 1)[1].split("</span>", 1)[0]
        state = r.split('itemprop="addressRegion">', 1)[1].split("</span>", 1)[0]
        zip_code = r.split('itemprop="postalCode">', 1)[1].split("</span>", 1)[0][1:]
        country = r.split('itemprop="addressCountry">', 1)[1].split("</abbr>", 1)[0]
        phone = r.split('itemprop="telephone" id="telephone">', 1)[1].split(
            "</span>", 1
        )[0]
        store_type = "<MISSING>"
        if title == "":
            title = "<MISSING>"
        if store == "":
            store = "<MISSING>"
        if lat == "":
            lat = "<MISSING>"
        if phone == "" or phone is None:
            phone = "<MISSING>"
        if long == "":
            long = "<MISSING>"
        if street == "":
            street = "<MISSING>"
        if city == "":
            city = "<MISSING>"
        if zip_code == "":
            zip_code = "<MISSING>"
        if country == "":
            country = "USA"
        hours_of_operation = ""
        for k in loc["storehours"]:
            hours_of_operation = (
                hours_of_operation + k["days"] + " " + k["times"] + ", "
            )
        hours_of_operation = hours_of_operation[0:-2]
        data.append(
            [
                "https://www.papaginos.com",
                sublink,
                title,
                street,
                city,
                state,
                zip_code,
                country,
                store,
                phone,
                store_type,
                lat,
                long,
                hours_of_operation,
            ]
        )
    return data


def write_output(data):
    with open("data.csv", mode="w", encoding="utf8", newline="") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )

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

        for row in data:
            writer.writerow(row)


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
