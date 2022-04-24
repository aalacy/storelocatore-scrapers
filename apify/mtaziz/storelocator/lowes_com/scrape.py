from sgzip.dynamic import DynamicZipSearch
from sgzip.dynamic import SearchableCountries, Grain_8
from sglogging import SgLogSetup
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgselenium import SgChrome
from webdriver_manager.chrome import ChromeDriverManager
import json
from lxml import html
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


def get_hoo(store):
    hoo = ""
    hours = store["storeHours"]
    hours_detail = []
    for i in hours:
        openclose = i["day"]["day"] + " " + i["day"]["open"] + " - " + i["day"]["close"]
        hours_detail.append(openclose)
    hoo = "; ".join(hours_detail)
    return hoo


def fetch_records(zc, sgw: SgWriter, driver: SgChrome):
    api_url = f"https://www.lowes.com/store/api/search?maxResults=&responseGroup=large&searchTerm={zc}"
    driver.get(api_url)
    driver.implicitly_wait(5)
    pgsrc = driver.page_source
    logger.info(f"[ZIP: {zc}]")
    sel = html.fromstring(pgsrc, "lxml")
    json_raw = sel.xpath("//body//text()")
    json_raw = "".join(json_raw)
    if json_raw:
        api_js = json.loads(json_raw)
        stores = api_js["stores"]
        if isinstance(stores, list):
            logger.info(f"[StoresFound: {len(stores)}] || [PullingFor: {zc}]")
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
        else:
            return


def fetch_data(sgw: SgWriter):
    logger.info("Started")

    # TEST1: Search Radius 1000 miles set for testing purpose on apify
    # TEST2: Search Radius 500 miles set for testing purpose on apify.
    # PROD: Search Radius 200 is found to return the data for all the stores.

    search = DynamicZipSearch(
        country_codes=[SearchableCountries.USA],
        expected_search_radius_miles=200,
        granularity=Grain_8(),
        use_state=False,
    )

    # NOTE: The crawler experiences 403 if sgrequests used.
    # This only happens on Apify env.
    # Using sgrequests, the crawler runs without any issue so far.
    # There is slack chat thread for your note.
    # If needed, can be search using lowes_com on slack.

    with SgChrome(
        executable_path=ChromeDriverManager().install(), is_headless=True
    ) as driver:
        for zipcode in search:
            fetch_records(zipcode, sgw, driver)


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
