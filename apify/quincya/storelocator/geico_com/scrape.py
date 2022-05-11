import csv

from bs4 import BeautifulSoup

from sgrequests import SgRequests

from sgzip.dynamic import DynamicZipSearch, SearchableCountries


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
    session = SgRequests()
    headers = {
        "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"
    }
    locator_domain = "geico.com"

    max_results = 10
    max_distance = 50

    dup_tracker = set()

    search = DynamicZipSearch(
        country_codes=[SearchableCountries.USA],
        max_search_distance_miles=max_distance,
        max_search_results=max_results,
    )

    for postcode in search:

        base_link = (
            "https://www.geico.com/public/php/geo_map.php?address=%s&language=en&type=Sales&captcha=false"
            % postcode
        )

        try:
            res_json = session.get(base_link, headers=headers).json()[1:]
        except:
            continue

        for loc in res_json:

            location_name = loc["displayName"].strip()
            phone_number = loc["contactPhone"]
            if not phone_number:
                phone_number = "<MISSING>"
            page_url = "https://www.geico.com" + loc["url"]

            if page_url not in dup_tracker:
                dup_tracker.add(page_url)
            else:
                continue

            lat = loc["latitude"]
            longit = loc["longitude"]
            search.found_location_at(lat, longit)

            raw_address = loc["formattedAddress"]
            city = loc["city"]
            state = raw_address.split(",")[-1].split()[0].strip()
            zip_code = raw_address.split(",")[-1].split()[-1].strip()
            street_address = raw_address[: raw_address.rfind(city) :].strip()
            if street_address[-1:] == ",":
                street_address = street_address[:-1].strip()
            country_code = "US"
            store_number = loc["soa"]
            location_type = "<MISSING>"
            hours = BeautifulSoup(loc["locationHours"], "lxml").get_text(" ")
            if "day" not in hours.lower():
                req = session.get(page_url, headers=headers)
                base = BeautifulSoup(req.text, "lxml")
                hours = " ".join(
                    list(base.find_all(class_="box gfr_margin")[1].stripped_strings)[1:]
                )
                if "day" not in hours.lower():
                    hours = "<MISSING>"
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
                lat,
                longit,
                hours,
                page_url,
            ]

            yield store_data


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
