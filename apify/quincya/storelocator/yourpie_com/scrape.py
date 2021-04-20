import csv

from bs4 import BeautifulSoup

from sglogging import sglog

from sgrequests import SgRequests

from sgzip.dynamic import DynamicZipSearch, SearchableCountries

log = sglog.SgLogSetup().get_logger(logger_name="yourpie.com")


def write_output(data):
    with open("data.csv", mode="w") as output_file:
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

    found_poi = []

    max_results = 10
    max_distance = 50

    search = DynamicZipSearch(
        country_codes=[SearchableCountries.USA],
        max_radius_miles=max_distance,
        max_search_results=max_results,
    )

    log.info("Running sgzip ..")
    for postcode in search:
        base_link = (
            "https://yourpie.com/locations/?proximity=%s&units=Miles&origin=%s"
            % (max_distance, postcode)
        )
        req = session.get(base_link, headers=headers)
        base = BeautifulSoup(req.text, "lxml")

        try:
            items = base.find(class_="locationInfo").find_all("li")
        except:
            continue
        for item in items:
            locator_domain = "citizensbank.com"
            if "COMING SOON" in item.text.upper():
                continue

            location_name = "Your Pie - " + item.a.text.strip()

            raw_address = list(item.p.stripped_strings)
            street_address = raw_address[0].strip()
            city = raw_address[1].split(",")[0].strip()
            state = raw_address[1].split(",")[1].strip().split()[0]
            try:
                zip_code = raw_address[1].split(",")[1].strip().split()[1]
                if not zip_code.isdigit():
                    zip_code = "<MISSING>"
            except:
                zip_code = "<MISSING>"
            country_code = "US"
            store_number = "<MISSING>"
            phone = item.find(class_="phone").text.strip()
            if phone in found_poi:
                continue
            found_poi.append(phone)
            location_type = "<MISSING>"
            latitude = item["data-lat"]
            longitude = item["data-lng"]

            search.found_location_at(latitude, longitude)

            link = item.a["href"]
            log.info(link)
            req = session.get(link, headers=headers)
            base = BeautifulSoup(req.text, "lxml")

            try:
                hours_of_operation = " ".join(
                    list(base.find(class_="thirty hours").div.stripped_strings)
                )
            except:
                hours_of_operation = "<MISSING>"

            yield [
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


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
