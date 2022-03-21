import csv

from concurrent import futures
from sgrequests import SgRequests


def write_output(data):
    with open("data.csv", mode="w", encoding="utf8", newline="") as output_file:
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


def get_ids():
    ids = []
    api_url = "https://api.flipdish.co/Restaurant/PickupPhysicalRestaurantSummariesFromCoordinates"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "uk-UA,uk;q=0.8,en-US;q=0.5,en;q=0.3",
        "Flipdish-White-Label-Id": "caspianpizza",
        "X-Coordinates": "27.9475,-82.4584,4",
        "Flipdish-App-Type": "Web",
        "Origin": "https://caspian.pizza",
        "Connection": "keep-alive",
        "Referer": "https://caspian.pizza/",
        "TE": "Trailers",
    }

    params = (
        ("Latitude", "27.9475"),
        ("Longitude", "-82.4584"),
        ("skip", "0"),
        ("count", "1000"),
    )

    session = SgRequests()
    r = session.get(api_url, headers=headers, params=params)
    js = r.json()["Data"]
    for j in js:
        ids.append(j.get("PhysicalRestaurantId"))

    return ids


def get_data(_id):
    locator_domain = "https://caspian.pizza/"
    page_url = "https://caspian.pizza/order-online-2/#/collection"
    api_url = f"https://api.flipdish.co/Restaurant/PickupRestaurantDetails/{_id}"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "uk-UA,uk;q=0.8,en-US;q=0.5,en;q=0.3",
        "Flipdish-White-Label-Id": "caspianpizza",
        "Flipdish-App-Type": "Web",
        "Origin": "https://caspian.pizza",
        "Connection": "keep-alive",
        "Referer": "https://caspian.pizza/",
        "TE": "Trailers",
    }

    session = SgRequests()
    r = session.get(api_url, headers=headers)
    j = r.json()["Data"]

    location_name = j.get("RestaurantName")
    line = j.get("PhysicalRestaurantAddress").split(",")
    line = list(filter(None, line))

    street_address = line.pop(0).strip()
    city = line[0].strip()
    postal = line[-1].strip()
    if city.startswith("LN1"):
        city = line[-1].strip()
        postal = line[-2].strip()
    if " " not in postal:
        postal = "<MISSING>"
        city = line[-1].strip()
    state = "<MISSING>"
    country_code = "GB"
    store_number = "<MISSING>"
    phone = j.get("DisplayPhoneNumber") or "<MISSING>"
    latitude = j.get("Latitude") or "<MISSING>"
    longitude = j.get("Longitude") or "<MISSING>"
    location_type = "<MISSING>"
    hours_of_operation = "<MISSING>"

    row = [
        locator_domain,
        page_url,
        location_name,
        street_address,
        city,
        state,
        postal,
        country_code,
        store_number,
        phone,
        location_type,
        latitude,
        longitude,
        hours_of_operation,
    ]

    return row


def fetch_data():
    out = []
    ids = get_ids()

    with futures.ThreadPoolExecutor(max_workers=2) as executor:
        future_to_url = {executor.submit(get_data, _id): _id for _id in ids}
        for future in futures.as_completed(future_to_url):
            row = future.result()
            if row:
                out.append(row)

    return out


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
