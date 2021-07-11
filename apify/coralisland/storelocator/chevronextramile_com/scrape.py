import csv

from sglogging import sglog

from sgrequests import SgRequests

from sgzip.dynamic import DynamicGeoSearch, SearchableCountries

log = sglog.SgLogSetup().get_logger(logger_name="chevronextramile.com")

base_url = "https://www.chevronextramile.com"


def validate(item):
    if item is None:
        item = ""
    if type(item) == int or type(item) == float:
        item = str(item)
    if type(item) == list:
        item = " ".join(item)
    return item.replace("\u2013", "-").strip()


def get_value(item):
    if item is None:
        item = "<MISSING>"
    item = validate(item)
    if item == "":
        item = "<MISSING>"
    return item


def eliminate_space(items):
    rets = []
    for item in items:
        item = validate(item)
        if item != "":
            rets.append(item)
    return rets


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

    session = SgRequests()

    history = []

    max_distance = 35

    search = DynamicGeoSearch(
        country_codes=[SearchableCountries.USA],
        max_radius_miles=max_distance,
    )

    for lat, lng in search:
        log.info(
            "Searching: %s, %s | Items remaining: %s"
            % (lat, lng, search.items_remaining())
        )

        base_link = (
            "https://www.chevronwithtechron.com/api/app/techron2go/ws_getChevronExtraMileNearMe_v1.aspx?radius=35&lat="
            + str(lat)
            + "&lng="
            + str(lng)
            + "&token=DC-A2FF22B238E6&search5=1"
        )
        store_list = session.get(base_link, headers=headers).json()["stations"]

        for store in store_list:
            search.found_location_at(store["lat"], store["lng"])
            uni_id = validate(store["lat"]) + "-" + validate(store["lng"])
            if uni_id not in history:
                history.append(uni_id)
                output = []
                output.append(base_url)  # url
                output.append(
                    "https://www.chevronextramile.com/station-finder/"
                )  # page url
                output.append(get_value(store["name"]))  # location name
                output.append(
                    get_value(store["address"].replace("&amp;", "&"))
                )  # address
                output.append(get_value(store["city"]))  # city
                output.append(get_value(store["state"]))  # state
                output.append(get_value(store["zip"]))  # zipcode
                output.append("US")  # country code
                output.append(get_value(store["id"]))  # store_number
                output.append(get_value(store["phone"]))  # phone
                output.append("<MISSING>")  # location type
                output.append(get_value(store["lat"]))  # latitude
                output.append(get_value(store["lng"]))  # longitude
                output.append(get_value(store["hours"]))  # opening hours
                yield output


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
