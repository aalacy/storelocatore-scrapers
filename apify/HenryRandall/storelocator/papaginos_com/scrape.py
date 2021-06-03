import csv
import json
from sgrequests import SgRequests
from sgselenium import SgChrome

session = SgRequests()


def get_headers(url, requestName, headerIdent):
    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36"
    with SgChrome(is_headless=True, user_agent=user_agent) as driver:
        driver.get(url)
        for r in driver.requests:
            if requestName in r.path and r.headers[headerIdent]:
                return r.headers


def fetch_data():
    # Your scraper here
    data = []
    url = "https://api.papaginos.com/api/v2/locations"
    headers = get_headers(
        "https://www.papaginos.com/locations", "api/v2/locations", "Authorization"
    )

    r = session.get(url, headers=headers, verify=False)

    loclist = json.loads(r.text)
    for loc in loclist:
        title = loc["name"]
        store = loc["number"]
        sublink = "https://locations.papaginos.com/" + str(store)

        lat = loc["latitude"]
        longt = loc["longitude"]
        if loc["address2"]:
            street = loc["address1"] + " " + loc["address2"]
        else:
            street = loc["address1"]
        city = loc["city"]
        state = loc["state"]
        pcode = loc["zip"]
        ccode = "USA"
        store_type = "<MISSING>"
        phone = loc["phone"]
        if title == "":
            title = "<MISSING>"
        if store == "":
            store = "<MISSING>"
        if lat == "":
            lat = "<MISSING>"
        if phone == "" or phone is None:
            phone = "<MISSING>"
        if longt == "":
            longt = "<MISSING>"
        if street == "":
            street = "<MISSING>"
        if city == "":
            city = "<MISSING>"
        if pcode == "":
            pcode = "<MISSING>"
        if ccode == "":
            ccode = "USA"
        if store_type == "":
            store_type = "<MISSING>"
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
                pcode,
                ccode,
                store,
                phone,
                store_type,
                lat,
                longt,
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
