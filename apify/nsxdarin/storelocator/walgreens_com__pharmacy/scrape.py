import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup
from concurrent.futures import ThreadPoolExecutor, as_completed
from tenacity import retry, stop_after_attempt

logger = SgLogSetup().get_logger("walgreens_com__pharmacy")


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


MISSING = "<MISSING>"


def get(obj, key, default=MISSING):
    return obj.get(key, default) or default


@retry(stop=stop_after_attempt(3))
def fetch_stores():
    data = {
        "apiKey": "0IILjid96hgTNUwAVKFldgNA4Fe3Cwcr",
        "act": "storenumber",
        "appVer": "2.0",
    }

    session = SgRequests()
    response = session.post(
        "https://services.walgreens.com/api/util/storenumber/v1", json=data
    ).json()
    return [int(number) for number in response["store"]]


@retry(stop=stop_after_attempt(3))
def fetch_location(store_number, session):
    page_url = f"https://www.walgreens.com/locator/v1/stores/{store_number}"
    response = session.get(page_url)

    data = response.json()
    if data.get("messages"):  # invalid store number
        if data["messages"]["type"] == "ERROR":
            return None
        else:
            raise Exception()

    locator_domain = "walgreens.com"
    location_name = MISSING

    address = data["address"]
    street_address = get(address, "street")
    city = get(address, "city")
    postal = get(address, "zip")
    state = get(address, "state")
    country_code = "US"
    latitude = get(data, "latitude")
    longitude = get(data, "longitude")

    phone = get(data, "phone", None)
    phone_number = (
        f"{get(phone, 'areaCode').strip()}{get(phone, 'number').strip()}"
        if phone
        else MISSING
    )

    info = get(data, "storeInfo", {})

    location_type = (
        "TelePharmacy Kiosk"
        if get(data, "storeBrand") != "Walgreens"
        else "Walgreens Pharmacy"
    )

    hours = get(info, "hrs", [])
    hours_of_operation = (
        ','.join([f'{hr["day"]}: {hr["open"]}-{hr["close"]}' for hr in hours])
        if len(hours)
        else MISSING
    )

    return [
        locator_domain,
        page_url,
        location_name,
        street_address,
        city,
        state,
        postal,
        country_code,
        store_number,
        phone_number,
        location_type,
        latitude,
        longitude,
        hours_of_operation,
    ]


def fetch_data():
    store_numbers = fetch_stores()
    all_store_numbers = range(0, max(store_numbers))

    with ThreadPoolExecutor() as executor, SgRequests() as session:
        futures = [
            executor.submit(fetch_location, store_number, session)
            for store_number in all_store_numbers
        ]
        for future in as_completed(futures):
            poi = future.result()
            if poi:
                yield poi


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
