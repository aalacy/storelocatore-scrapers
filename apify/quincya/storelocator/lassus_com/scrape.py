import csv

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

    base_link = "https://www.lassus.com/locations/"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    items = base.find_all(class_="single-location col-3")

    all_scripts = base.find_all("script")
    for script in all_scripts:
        if "var stores" in str(script):
            script = str(script).replace("\\", "")
            break
    store_data = script.split("Directions")

    data = []
    for item in items:
        locator_domain = "lassus.com"
        location_name = item.h3.text
        street_address = item.p.text.strip()
        city_line = item.find(class_="h5 location-link").text.strip().split(",")
        city = city_line[0].strip()
        state = city_line[-1].strip().split()[0].strip()
        zip_code = city_line[-1].strip().split()[1].strip()
        country_code = "US"
        store_number = item.find(class_="store-no").text
        try:
            location_type = item.find(class_="modal-location-alert").text
        except:
            location_type = "Open"
        if "coming soon" in location_type.lower():
            continue
        phone = item.find(class_="location-phone-number").text.strip()
        hours_of_operation = item.header.find_all("p")[-1].text.strip()
        latitude = "<MISSING>"
        longitude = "<MISSING>"

        for store in store_data:
            num = store.split('store_number":')[1].split('",')[0][1:]
            if num == store_number:
                latitude = store.split('latitude":')[1].split(",")[0]
                longitude = store.split('longitude":')[1].split(",")[0]
                break

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
