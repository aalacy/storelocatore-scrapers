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

    base_link = "https://www.howards.com/stores/"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    data = []

    items = base.find_all(class_="stores-page-box")
    locator_domain = "howards.com"

    for item in items:

        location_name = item.h3.text.strip()
        if "store closed" in location_name.lower():
            continue

        raw_address = str(item.find_all("p")[1])[3:-4].split("<br/>")
        street_address = raw_address[0].strip()
        city_line = raw_address[1].split(",")
        city = city_line[0].strip()
        state = city_line[1].strip()[:2].strip()
        zip_code = city_line[1][3:9].strip()
        country_code = "US"
        store_number = "<MISSING>"
        location_type = "<MISSING>"
        phone = item.find(class_="store-phone").text.replace("Phone:", "").strip()
        hours_of_operation = item.find_all("p")[-1].text.replace("\r\n", " ").strip()

        link = "https://www.howards.com" + item.a["href"]
        req = session.get(link, headers=headers)
        base = BeautifulSoup(req.text, "lxml")

        fin_script = ""
        all_scripts = base.find_all("script", attrs={"type": "application/ld+json"})
        for script in all_scripts:
            if "latitude" in str(script):
                fin_script = script.text.replace("\n", "").strip()
                break
        if fin_script:
            store = json.loads(fin_script)
            latitude = store["geo"]["latitude"]
            longitude = store["geo"]["longitude"]
            if link == "https://www.howards.com/stores/marina-pacifica/":
                latitude = "33.759772"
                longitude = "-118.113817"
        else:
            latitude = "<MISSING>"
            longitude = "<MISSING>"

        if "6346 E. Pacific" in street_address:
            latitude = "33.760438"
            longitude = "-118.113446"

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

    return data


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
