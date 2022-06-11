import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgzip.static import static_zipcode_list, SearchableCountries

local = threading.local()


def get_session():
    if not hasattr(local, "session"):
        local.session = SgRequests()

    return local.session


def fetch_locations(code, session):
    start_url = "https://www.moleskine.com/on/demandware.store/Sites-Moleskine_NAM-Site/en_US/Stores-SearchResults"
    domain = "moleskine.com"

    frm = {"dwfrm_storelocator_country": "US", "dwfrm_storelocator_query": code}
    data = get_session().post(start_url, data=frm)
    if data.status_code != 200:
        return []
    data = data.json()
    if not data.get("stores"):
        return []

    locations = []
    for poi in data["stores"]:
        item = SgRecord(
            locator_domain=domain,
            page_url="https://us.moleskine.com/en/store-locator",
            location_name=poi["name"],
            street_address=", ".join(poi["address"]["lines"]),
            city=poi["address"]["city"],
            state="",
            zip_postal=poi["address"]["zip"],
            country_code="US",
            store_number="",
            phone=poi["phone"],
            location_type=poi["type"],
            latitude=poi["coords"][0],
            longitude=poi["coords"][-1],
            hours_of_operation="",
        )

        locations.append(item)

    return locations


def fetch_data():
    search = static_zipcode_list(5, SearchableCountries.USA)

    with SgRequests() as session, ThreadPoolExecutor(max_workers=1) as executor:
        futures = [executor.submit(fetch_locations, code, session) for code in search]
        for future in as_completed(futures):
            yield from future.result()


def scrape():
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {SgRecord.Headers.LOCATION_NAME, SgRecord.Headers.STREET_ADDRESS}
            ),
            duplicate_streak_failure_factor=-1,
        )
    ) as writer:
        for item in fetch_data():
            writer.write_row(item)


if __name__ == "__main__":
    scrape()
