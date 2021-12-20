from sgrequests import SgRequests
from sglogging import SgLogSetup
from concurrent.futures import ThreadPoolExecutor, as_completed
from tenacity import retry, stop_after_attempt
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

logger = SgLogSetup().get_logger("walgreens_com__pharmacy")


def write_output(data):
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        for row in data:
            writer.write_row(row)


MISSING = "<MISSING>"


def get(obj, key, default=MISSING):
    return obj.get(key, default) or default


@retry(stop=stop_after_attempt(3), reraise=True)
def fetch_stores():
    data = {
        "apiKey": "kBzrBap6mSlwPNQbX5uNbl4JiQRf7yJz",
        "act": "storenumber",
        "appVer": "2.0",
    }

    session = SgRequests()
    response = session.post(
        "https://services-qa.walgreens.com/api/util/storenumber/v1", json=data
    ).json()
    return [int(number) for number in response["store"]]


@retry(stop=stop_after_attempt(3), reraise=True)
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

    if not len(data):
        logger.info(f"no data: {page_url}")
        return None

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
        ",".join([f'{hr["day"]}: {hr["open"]}-{hr["close"]}' for hr in hours])
        if len(hours)
        else MISSING
    )

    return SgRecord(
        locator_domain=locator_domain,
        page_url=page_url,
        location_name=location_name,
        street_address=street_address,
        city=city,
        state=state,
        zip_postal=postal,
        country_code=country_code,
        store_number=store_number,
        phone=phone_number,
        location_type=location_type,
        latitude=latitude,
        longitude=longitude,
        hours_of_operation=hours_of_operation,
    )


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


if __name__ == "__main__":
    scrape()
