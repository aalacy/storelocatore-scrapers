import csv
from sgrequests import SgRequests
import re
import json
from bs4 import BeautifulSoup


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
    p = 0
    data = []
    pattern = re.compile(r"\s\s+")
    session = SgRequests()
    HEADERS = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
    }
    r = session.get(
        "https://globalpetfoods.com/portal/store-locations-sitemap/", headers=HEADERS
    )
    loclist = BeautifulSoup(r.text, "html.parser").findAll("url")
    for loc in loclist:
        if "Soon" in loc.text:
            continue
        link = loc.find("loc").text
        r = session.get(link, headers=HEADERS, verify=False, timeout=10)
        locator_domain = "https://globalpetfoods.com/"
        soup = BeautifulSoup(r.content, "html.parser")

        location_name = soup.find("span", {"class": "location_title"}).text.strip()
        if location_name == "":
            continue
        if "Soon" in location_name:
            continue
        try:
            content = r.text.split("type='application/ld+json'>", 1)[1].split(
                "</script", 1
            )[0]
            content = re.sub(pattern, "", content)
            content = json.loads(content)
        except:
            continue
        hours = " ".join(content["openingHours"])
        addy = content["address"]
        city = addy["addressLocality"]
        state = addy["addressRegion"]
        zip_code = addy["postalCode"]
        if zip_code == "HN8 1X7":
            zip_code = "H8N 1X7"
        street_address = addy["streetAddress"]
        phone_number = addy["telephone"].replace("=", "").replace("+1", "").strip()
        if phone_number == "":
            phone_number = "<MISSING>"
        location_name = addy["name"]

        country_code = "CA"

        store_number = link.split("=", 1)[1]
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
            phone_number,
            location_type,
            "<MISSING>",
            "<MISSING>",
            hours,
            page_url,
        ]

        data.append(store_data)

        p += 1
    return data


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
