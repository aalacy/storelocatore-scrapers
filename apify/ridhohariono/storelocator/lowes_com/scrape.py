from sgrequests import SgRequests
from sgzip.dynamic import DynamicZipSearch
from sgzip.dynamic import SearchableCountries, Grain_8
from sglogging import SgLogSetup
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgselenium import SgSelenium, SgChrome

import ssl

try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification


logger = SgLogSetup().get_logger("lowes_com")
DOMAIN = "lowes.com"
MAX_WORKERS = 1


def get_headers_for(url: str) -> dict:
    with SgChrome() as chrome:
        headers = SgSelenium.get_default_headers_for(chrome, url)
        headers.update(
            {
                "accept": "application/json, text/plain, */*",
                "x-component-location": "store-locator",
                "x-sec-clge-req-type": "ajax",
            }
        )
    return headers  # type: ignore


def get_hoo(store):
    hoo = ""
    hours = store["storeHours"]
    hours_detail = []
    for i in hours:
        openclose = i["day"]["day"] + " " + i["day"]["open"] + " - " + i["day"]["close"]
        hours_detail.append(openclose)
    hoo = "; ".join(hours_detail)
    return hoo


def fetch_records(zc, sgw: SgWriter, session: SgRequests, headers: dict):
    api_url = f"https://www.lowes.com/store/api/search?maxResults=&responseGroup=large&searchTerm={zc}"
    rapi = session.get(api_url, headers=headers)
    if rapi.status_code == 200:
        api_js = rapi.json()
        stores = api_js["stores"]
        logger.info(f"Store Count: [{len(stores)}] || << Pulling data for {zc} >>")
        for idx, i in enumerate(stores[0:]):
            store = i["store"]
            city_f = store["city"] or ""
            if city_f:
                city_f = city_f.lower().replace(" ", "-")
            state_f = store["state"] or ""
            sn_f = store["id"] or ""
            purl = ""
            if city_f and state_f and sn_f:
                purl = f"https://www.lowes.com/store/{state_f}-{city_f}/{sn_f}"
            else:
                purl = ""

            item = SgRecord(
                locator_domain=DOMAIN,
                page_url=purl,
                location_name=store["store_name"] or "",
                street_address=store["address"] or "",
                city=store["city"] or "",
                state=store["state"] or "",
                zip_postal=store["zip"] or "",
                country_code=store["country"] or "",
                store_number=store["id"] or "",
                phone=store["phone"] or "",
                location_type=store["storeFeature"] or "",
                latitude=store["lat"] or "",
                longitude=store["long"] or "",
                hours_of_operation=get_hoo(store),
                raw_address="",
            )

            sgw.write_row(item)


def fetch_data(sgw: SgWriter):
    logger.info("Started")

    # NOTE: Radius 1000 miles for testing purpose on apify
    search = DynamicZipSearch(
        country_codes=[SearchableCountries.USA],
        expected_search_radius_miles=200,
        granularity=Grain_8(),
        use_state=False,
    )

    headers = get_headers_for("https://www.lowes.com/store/")

    with SgRequests() as session:
        for zipcode in search:
            fetch_records(zipcode, sgw, session, headers)


def scrape():
    logger.info("Scrape Started")
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.STORE_NUMBER,
                    SgRecord.Headers.LATITUDE,
                    SgRecord.Headers.LONGITUDE,
                    SgRecord.Headers.STREET_ADDRESS,
                }
            )
        )
    ) as writer:
        fetch_data(writer)
    logger.info("Finished")  # noqa


if __name__ == "__main__":
    scrape()
