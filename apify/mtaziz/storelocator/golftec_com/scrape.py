from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries, Grain_8
from sglogging import SgLogSetup
from concurrent.futures import ThreadPoolExecutor, as_completed
import ssl
import tenacity
from tenacity import retry, stop_after_attempt
from bs4 import BeautifulSoup as bs


try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification

MAX_WORKERS = 5
logger = SgLogSetup().get_logger("golftec")
headers = {
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.64 Safari/537.36"
}

locator_domain = "https://www.golftec.com"


@retry(stop=stop_after_attempt(5), wait=tenacity.wait_fixed(5))
def get_locs(url, http):
    res = http.get(url, headers=headers)
    return res.json()


def fetch_records(coord, search_us, sgw: SgWriter):
    lat = coord[0]
    lng = coord[1]

    with SgRequests(proxy_country="us") as http:
        url = f"https://wcms.golftec.com/loadmarkers_6.php?thelong={lng}&thelat={lat}&georegion=North+America&pagever=prod&maptype=closest10"
        logger.info(f"PullingContentFrom: {url} | ( {lat}, {lng})")
        try:
            locations = get_locs(url, http)
        except:
            logger.info(f"[{lat}, {lng}] failed")
            locations = {}

        if "centers" in locations:
            for _ in locations["centers"]:
                page_url = f"{locator_domain}{_['link']}"
                res = http.get(page_url, headers=headers)
                if res.status_code != 200:
                    return
                soup = bs(res.text, "lxml")
                street_address = _["street1"]
                if _["street2"]:
                    street_address += " " + _["street2"]
                if street_address and "coming soon" in street_address.lower():
                    continue
                hours = [
                    ": ".join(hh.stripped_strings)
                    for hh in soup.select(
                        "div.center-details__hours div.seg-center-hours ul li"
                    )
                ]
                if not hours:
                    hours = [
                        ": ".join(hh.stripped_strings)
                        for hh in soup.select("div.center-details__hours ul li")
                    ]
                lat_found = _["position"]["thelat"]
                lng_found = _["position"]["thelong"]
                search_us.found_location_at(lat_found, lng_found)
                item = SgRecord(
                    page_url=page_url,
                    store_number=_["cid"],
                    location_name=_["name"],
                    street_address=street_address.replace(
                        "Inside Golf Town", ""
                    ).strip(),
                    city=_["city"],
                    state=_["state"],
                    zip_postal=_["zip"],
                    latitude=lat_found,
                    longitude=lng_found,
                    country_code=_["country"],
                    phone=_["phone"],
                    hours_of_operation="; ".join(hours),
                    locator_domain="golftec.com",
                )
                sgw.write_row(item)


def fetch_data(sgw: SgWriter):
    logger.info("Started")

    search_us = DynamicGeoSearch(
        country_codes=[SearchableCountries.USA],
        expected_search_radius_miles=300,
        granularity=Grain_8(),
        use_state=False,
    )

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        tasks = []
        task_us = [
            executor.submit(fetch_records, latlng, search_us, sgw)
            for latlng in search_us
        ]
        tasks.extend(task_us)
        for future in as_completed(tasks):
            if future.result() is not None:
                future.result()


def scrape():
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.PAGE_URL,
                    SgRecord.Headers.LATITUDE,
                    SgRecord.Headers.LONGITUDE,
                }
            ),
            duplicate_streak_failure_factor=1500,
        )
    ) as writer:
        fetch_data(writer)
    logger.info("Finished")


if __name__ == "__main__":
    scrape()
