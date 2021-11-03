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

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    data = []
    locator_domain = "hyatt.com"

    store_link = "https://www.hyatt.com/explore-hotels/service/hotels"

    stores = session.get(store_link, headers=headers).json()

    for i in stores:
        store = stores[i]
        country_code = store["location"]["country"]["key"]
        if country_code in ["US", "CA", "GB"]:
            if "andaz" in store["brand"]["key"].lower():
                location_name = store["name"]
                street_address = store["location"]["addressLine1"].split(",")[0].strip()
                city = store["location"]["city"]
                state = store["location"]["stateProvince"]["key"]
                zip_code = store["location"]["zipcode"]
                store_number = store["spiritCode"]
                location_type = "<MISSING>"
                latitude = store["location"]["geolocation"]["latitude"]
                longitude = store["location"]["geolocation"]["longitude"]
                hours_of_operation = "<MISSING>"
                link = store["url"]

                req = session.get(link, headers=headers)
                base = BeautifulSoup(req.text, "lxml")
                try:
                    phone = base.find(class_="col-phone b-col").a.text
                except:
                    phone = "<MISSING>"
                if (
                    "coming soon"
                    in base.find(
                        class_="site-header-container b-container"
                    ).text.lower()
                ):
                    location_type = "Coming Soon"

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
