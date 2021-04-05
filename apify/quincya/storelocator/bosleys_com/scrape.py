import csv

from sglogging import sglog

from sgrequests import SgRequests

from sgzip.dynamic import DynamicGeoSearch, SearchableCountries

log = sglog.SgLogSetup().get_logger(logger_name="petvalu.com")

session = SgRequests()

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


def parse_hours(store):
    hrs = store["op"]
    days = ["mon", "tues", "wed", "thurs", "fri", "sat", "sun"]
    hours = []
    for dayidx in range(len(days)):
        day = days[dayidx]
        start = hrs[str(dayidx * 2)]
        end = hrs[str(dayidx * 2 + 1)]
        hours.append("{}: {}-{}".format(day, start, end))
    return ", ".join(hours)


def fetch_data():
    headers = {
        "authority": "store.petvalu.com",
        "accept": "application/json, text/javascript, */*; q=0.01",
        "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
        "origin": "https://store.petvalu.com",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.117 Safari/537.36",
    }
    base_url = "petvalu.com"
    keys = set()

    max_distance = 100

    search = DynamicGeoSearch(
        country_codes=[SearchableCountries.CANADA],
        max_radius_miles=max_distance,
    )

    for lat, lng in search:
        log.info(
            "Searching: %s, %s | Items remaining: %s"
            % (lat, lng, search.items_remaining())
        )

        stores = (
            session.post(
                "https://store.petvalu.com/ca/wp-admin/admin-ajax.php",
                headers=headers,
                data="action=get_stores&lat={}&lng={}&radius={}&store=&states=&cities=&adds=&zip=".format(
                    lat, lng, max_distance
                ),
            )
            .json()
            .values()
        )
        for store in stores:
            location_name = store["na"]
            if "bosley" not in location_name.lower():
                continue
            store_number = store["ID"]
            street_address = store["st"]
            if "<" in street_address:
                street_address = street_address.split("<")[0].strip()
            city = store["ct"].strip()
            state = store["rg"].strip()
            zipp = store["zp"].strip()
            country_code = store["co"].strip()
            if country_code.lower() != "ca":
                continue
            key = "|".join([street_address, city, state, zipp, country_code])
            if key in keys:
                continue
            else:
                keys.add(key)
            phone = store["te"] if "te" in store else "<MISSING>"
            location_type = "<MISSING>"
            latitude = store["lat"]
            longitude = store["lng"]
            search.found_location_at(latitude, longitude)
            page_url = store["gu"]
            hours = parse_hours(store)
            res = [base_url]
            res.append(location_name if location_name else "<MISSING>")
            res.append(street_address if street_address else "<MISSING>")
            res.append(city if city else "<MISSING>")
            res.append(state if state else "<MISSING>")
            res.append(zipp if zipp else "<MISSING>")
            res.append(country_code if country_code else "<MISSING>")
            res.append(store_number if store_number else "<MISSING>")
            res.append(phone if phone else "<MISSING>")
            res.append(location_type if location_type else "<MISSING>")
            res.append(latitude if latitude else "<MISSING>")
            res.append(longitude if longitude else "<MISSING>")
            res.append(hours if hours else "<MISSING>")
            res.append(
                page_url.replace("-/", "/").replace("---", "-")
                if page_url
                else "<MISSING>"
            )
            yield res


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
