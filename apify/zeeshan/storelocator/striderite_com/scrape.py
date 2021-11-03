import csv
from sgrequests import SgRequests


def write_output(data):
    with open("data.csv", mode="w", newline="") as output_file:
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


HEADERS = {
    "Referer": "https://www.striderite.com/en/stores",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36",
}

URL = "https://api.storerocket.io/api/user/wjN49rzJGy/locations"

session = SgRequests()


def handle_missing(field):
    if field is None or (isinstance(field, str) and len(field.strip()) == 0):
        return "<MISSING>"
    return field


def fetch_data():
    stores = []
    results = session.get(URL, headers=HEADERS).json()["results"]["locations"]
    for result in results:
        location_name = result["name"].replace('"', "'")
        locator_domain = "striderite.com"
        page_url = handle_missing(str(result["url"]))
        if page_url == "None":
            page_url = "<MISSING>"
        store_number = handle_missing(result["id"])
        street_address = handle_missing(result["address_line_1"]) or "<MISSING>"
        try:
            if len(result["address_line_2"]) > 0:
                street_address += " " + result["address_line_2"]
        except:
            street_address = street_address
        if street_address == "4th Street":
            street_address = handle_missing(result["address"]).split(",")[0].strip()
        latitude = handle_missing(result["lat"])
        longitude = handle_missing(result["lng"])
        city = handle_missing(result["city"])
        state = handle_missing(result["state"])
        zip_code = handle_missing(result["postcode"])
        country_code = handle_missing(result["country"])
        location_type = handle_missing(result["location_type_name"])
        phone = handle_missing(result["phone"])
        days = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
        tmp = []
        for d in days:
            day = d
            try:
                times = result[f"{d}"]
            except:
                times = "None"
            line = f"{day} {times}"
            tmp.append(line)
        hours = ";".join(tmp)
        if hours.count("None") == 7:
            hours = "<MISSING>"

        stores.append(
            [
                locator_domain,
                page_url,
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
                hours,
            ]
        )
    return stores


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
