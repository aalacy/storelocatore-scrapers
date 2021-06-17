import csv
import json

from bs4 import BeautifulSoup

from sgrequests import SgRequests


def write_output(data):
    with open("data.csv", mode="w") as output_file:
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


def fetch_data():

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    base_link = "https://storemapper-herokuapp-com.global.ssl.fastly.net/api/users/10216/stores.js?callback=SMcallback2"

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    js = base.text.split('ores":')[1].split("})")[0]
    stores = json.loads(js)

    data = []
    found = []
    locator_domain = "rockler.com"

    for store in stores:
        link = store["url"].lower()
        if link in found:
            continue
        found.append(link)

        if "rockler.com/retail/stores/" in link and "retail-partner" not in link:
            location_name = store["name"]
            raw_address = store["address"].split(",")
            street_address = raw_address[0]
            city = raw_address[1].strip()
            state = raw_address[2].strip().split()[0]
            try:
                zip_code = raw_address[-1].strip().split()[1]
            except:
                zip_code = raw_address[-1].strip()
            if "Frisco" in state:
                street_address = street_address + " " + city
                city = "Frisco"
                state = "TX"

            phone = store["phone"]
            country_code = "US"
            store_number = store["id"]
            latitude = store["latitude"]
            longitude = store["longitude"]
            location_type = "<MISSING>"

            try:
                req = session.get(link, headers=headers)
                base = BeautifulSoup(req.text, "lxml")
                try:
                    hours_of_operation = " ".join(
                        list(
                            base.find(class_="col-m-6")
                            .find_all(class_="sect")[-1]
                            .stripped_strings
                        )
                    )
                except:
                    try:
                        hours_of_operation = " ".join(
                            list(
                                base.find(class_="row sect")
                                .find_all(class_="sect")[-1]
                                .stripped_strings
                            )
                        )
                    except:
                        hours_of_operation = " ".join(
                            list(
                                base.find_all(class_="row sect")[1]
                                .find_all(class_="sect")[-1]
                                .stripped_strings
                            )
                        )
            except:
                link = "https://www.rockler.com/retail/stores/"
                hours_of_operation = "<MISSING>"
            hours_of_operation = hours_of_operation.replace("Store Hours", "").strip()

            # Store data
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
