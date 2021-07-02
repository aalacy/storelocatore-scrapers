import csv
import json

from bs4 import BeautifulSoup

from sgrequests import SgRequests


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

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    locator_domain = "https://www.francescas.com"
    ext = "/store-locator/all-stores.do"

    session = SgRequests()
    req = session.get(locator_domain + ext, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    link_list = []
    dup_tracker = set()

    locs = base.find_all(class_="ml-storelocator-store-address")
    for loc in locs:
        link = locator_domain + loc.a["href"]

        if link in link_list:
            continue

        got_page = False
        try:
            req = session.get(link, headers=headers)
            base = BeautifulSoup(req.text, "lxml")
            location_name = base.find("span", attrs={"itemprop": "name"}).text.strip()
            got_page = True
        except:
            got_page = False

        store_number = "<MISSING>"
        hours = "<MISSING>"
        lat = "<MISSING>"
        longit = "<MISSING>"
        country_code = "US"
        location_type = "<MISSING>"

        if not got_page:
            location_name = loc.find(
                class_="eslStore ml-storelocator-headertext"
            ).text.strip()
            if len(location_name.split("#")) == 2:
                store_number = location_name.split("#")[1].split("-")[0].strip()
            else:
                store_number = "<MISSING>"
            street_address = loc.find(class_="eslAddress1").text.strip()
            city = loc.find(class_="eslCity").text.replace(",", "").strip()
            state = loc.find(class_="eslStateCode").text.strip()
            zip_code = loc.find(class_="eslPostalCode").text.strip()
            phone_number = loc.find(class_="eslPhone").text.strip()
            page_url = locator_domain + ext
        else:
            store_number = "<MISSING>"
            if len(location_name.split("#")) == 2:
                store_number = location_name.split("#")[1].split("-")[0].strip()
            else:
                store_number = "<MISSING>"

            street_address = " ".join(
                list(
                    (
                        base.find(
                            "span", attrs={"itemprop": "streetAddress"}
                        ).stripped_strings
                    )
                )
            )
            if street_address not in dup_tracker:
                dup_tracker.add(street_address)
            else:
                continue
            city = base.find("span", attrs={"itemprop": "addressLocality"}).text
            state = base.find("span", attrs={"itemprop": "addressRegion"}).text
            zip_code = base.find("span", attrs={"itemprop": "postalCode"}).text
            if len(zip_code) == 4:
                zip_code = "0" + zip_code
            hours = (
                base.find(class_="ml-storelocator-hours-details")
                .getText(" ")
                .replace("\n", " ")
            )
            phone_number = "<MISSING>"
            try:
                phone_number = base.find("span", attrs={"itemprop": "telephone"}).text
            except:
                phone_number = "<MISSING>"

            loc_j = base.find_all("script")
            for i, loc in enumerate(loc_j):
                if "MarketLive.StoreLocator.storeLocatorDetailPageReady" in str(loc):
                    text = str(loc)
                    start = text.find("location")
                    text_2 = text[start - 1 :]

                    end = text_2.find("}")

                    coords = json.loads(text_2[text_2.find(":") + 1 : end + 1])

                    lat = coords["latitude"]
                    longit = coords["longitude"]
            page_url = link

        yield [
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
            lat,
            longit,
            hours,
            page_url,
        ]


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
