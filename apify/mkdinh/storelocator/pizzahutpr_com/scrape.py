import math
import tabula as tb  # noqa
from io import BytesIO
from datetime import datetime as dt

from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgpostal import International_Parser, parse_address

logger = SgLogSetup().get_logger("pizzahutpr_com")


def write_output(data):
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        for row in data:
            writer.write_row(row)


MISSING = "<MISSING>"
locator_domain = "pizzahutpr.com"
page_url = "https://apisae1.phdvasia.com/v1/product-hut-fe/localizations?location=-66.0702979,18.3586321&order_type=C&limit=100"

headers = {"Client": "df0d826e-d4c3-4c6e-acc5-48e72ef075ea", "Lang": "en"}


def fetch_locations(session):
    response = session.get(
        page_url,
        headers=headers,
    ).json()

    return response["data"]["items"]


def fetch_phone_city_map(session):
    phone_city_map = {}
    response = session.get(
        "https://static.phdvasia.com/pr/pdf/locations_v2.pdf",
        headers=headers,
    )
    file = BytesIO(response.content)

    dfs = tb.read_pdf(
        file,
        pages="all",
    )

    df = dfs[0]
    df.rename(columns={"PUEBLO": "location_name", "Unnamed: 0": "phone"}, inplace=True)

    current_city = None
    for _, row in df.iterrows():
        name = row.location_name
        phone = row.phone

        if name.isupper():
            current_city = name
            if phone and isinstance(phone, float) and not math.isnan(phone):
                phone_city_map[phone] = current_city
        else:
            phone_city_map[phone] = current_city

    return phone_city_map


def fetch_city_by_phone(phone, phone_city_map):
    for loc_phone, city in phone_city_map.items():
        if loc_phone in phone:
            return city


def fetch_hours_of_operation(store_number, session):
    response = session.get(
        f"https://apisae1.phdvasia.com/v2/product-hut-fe/outlets/opening_hours/{store_number}",
        headers=headers,
    ).json()
    item = response["data"]["item"]
    data = item.get("D") or item.get("C")

    hours = []
    for date_str, hours_data in data.items():
        date = dt.strptime(date_str, "%Y-%m-%d")
        weekday = date.strftime("%a")

        business_hours = hours_data["business_date"][0]
        start = business_hours["start"]
        end = business_hours["end"]

        hours.append(f"{weekday}: {start}-{end}")

    return ", ".join(hours)


def fetch_data():
    with SgRequests() as session:
        locations = fetch_locations(session)
        phone_city_map = fetch_phone_city_map(session)

        for location in locations:
            store_number = location["id"]
            location_name = location["name"]

            full_address = location["address"]
            address = parse_address(International_Parser(), full_address)

            street_address = (
                full_address if "Carr" in full_address else address.street_address_1
            )
            city = address.city

            postal = location["zip_code"]
            latitude = location["lat"]
            longitude = location["long"]

            phone = location["phone"]

            if not city:
                city = fetch_city_by_phone(phone, phone_city_map)

            hours_of_operation = fetch_hours_of_operation(store_number, session)

            yield SgRecord(
                locator_domain=locator_domain,
                page_url=page_url,
                location_name=location_name,
                store_number=store_number,
                street_address=street_address,
                city=city,
                state="PR",
                zip_postal=postal,
                country_code="US",
                latitude=latitude,
                longitude=longitude,
                phone=phone,
                hours_of_operation=hours_of_operation,
            )


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
