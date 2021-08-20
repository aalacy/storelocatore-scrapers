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

    base_link = "https://www.caesars.com/harrahs"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    data = []
    final_links = []

    locator_domain = "caesars.com"

    items = base.find_all(class_="card-slider")
    for item in items:
        js = str(item).replace("&quot;", '"').split('items":')[1].split('}"')[0]
        item_js = json.loads(js)
        for i in item_js:
            final_links.append(i["path"])

    for link in final_links:
        req = session.get(link, headers=headers)
        base = BeautifulSoup(req.text, "lxml")

        location_name = base.h1.text.strip()

        fin_script = ""
        all_scripts = base.find_all("script")
        for script in all_scripts:
            if "latitude" in str(script):
                fin_script = str(script)
                break

        try:
            store_data = json.loads(fin_script.split(">")[1].split("<")[0])
            street_address = store_data["address"]["streetAddress"]
            city = store_data["address"]["addressLocality"]
            state = store_data["address"]["addressRegion"]
            zip_code = store_data["address"]["postalCode"]
            phone = store_data["telephone"]
            latitude = store_data["geo"]["latitude"]
            longitude = store_data["geo"]["longitude"]
        except:
            raw_address = list(
                base.find(class_="footer-hotel-address").stripped_strings
            )
            street_address = raw_address[0]
            city = raw_address[1].split(",")[0]
            state = raw_address[1].split(",")[1].split()[0]
            zip_code = raw_address[1].split(",")[1].split()[1]
            phone = raw_address[2].replace("Tel:", "").strip()
            latitude = "<MISSING>"
            longitude = "<MISSING>"

        country_code = "US"
        store_number = "<MISSING>"
        location_type = "<MISSING>"

        try:
            open_text = (
                base.find(class_="CETContainer")
                .find(class_="CETRichText padding-horizontal")
                .h3.text.lower()
            )
        except:
            open_text = (
                base.find(class_="CETContainer")
                .find(class_="CETRichText padding-horizontal")
                .h4.text.lower()
            )
        if "from" in open_text:
            hours_of_operation = open_text.title().split("Open")[1].strip()
        else:
            hours_of_operation = "<MISSING>"

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
