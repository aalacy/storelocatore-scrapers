from sgrequests import SgRequests
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries, Grain_8
from sglogging import SgLogSetup
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
import ssl
from lxml import html

try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification

logger = SgLogSetup().get_logger("badgercoin_com")

headers = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.164 Safari/537.36",
}

search = DynamicGeoSearch(
    country_codes=[SearchableCountries.CANADA],
    expected_search_radius_miles=100,
    granularity=Grain_8(),
    use_state=False,
)


def get_hours(_):
    rawhoo = _["hours"]
    selh = html.fromstring(rawhoo, "lxml")
    trs = selh.xpath("//tr")
    hours = []
    for tr in trs:
        dt = " ".join(tr.xpath(".//text()"))
        hours.append(dt)
    hours_str = "; ".join(hours)
    return hours_str


def fetch_records():
    total = 0
    s_dedupe = set()
    for latlng in search:
        lats, lngs = latlng
        apiep = f"https://www.badgercoin.com/wp-admin/admin-ajax.php?action=store_search&lat={lats}&lng={lngs}&max_results=100&search_radius=100"
        s = SgRequests()
        js = s.get(apiep, headers=headers).json()
        logger.info(f"[Number of Stores] [{len(js)}] at [({lats}, {lngs})]")
        total += len(js)
        if js:
            for _ in js:
                snum = _["id"]
                search.found_location_at(_["lat"], _["lng"])
                if snum not in s_dedupe:
                    s_dedupe.add(snum)
                    add1 = _["address"]
                    add2 = _["address2"]
                    sta = ""
                    if add1 and not add2:
                        sta = add1
                    elif add1 and add2:
                        sta = add1 + ", " + add2
                    elif not add1 and add2:
                        sta = add2
                    else:
                        sta = ""
                    locname = ""
                    locname = _["store"]
                    locname = (
                        locname.replace("&#8217;", "'")
                        .replace("&#038;", "&")
                        .replace("&#8211;", "-")
                    )
                    item = SgRecord(
                        locator_domain="badgercoin.com",
                        page_url="https://www.badgercoin.com/find-a-location/",
                        location_name=locname,
                        street_address=sta,
                        city=_["city"],
                        state=_["state"],
                        zip_postal=_["zip"],
                        country_code=_["country"],
                        store_number=_["id"],
                        phone=_["phone"],
                        location_type="",
                        latitude=_["lat"],
                        longitude=_["lng"],
                        hours_of_operation=get_hours(_),
                        raw_address=sta,
                    )
                    yield item
    logger.info(f"Total Stores Found: {total}")


def scrape():
    logger.info("Scraping Started")
    count = 0
    deduper = SgRecordDeduper(
        SgRecordID(
            {
                SgRecord.Headers.STORE_NUMBER,
                SgRecord.Headers.STREET_ADDRESS,
                SgRecord.Headers.LATITUDE,
                SgRecord.Headers.LONGITUDE,
            }
        )
    )
    with SgWriter(deduper) as writer:
        results = fetch_records()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    logger.info(f"No of Unique Records Being Processed: {count}")
    logger.info("Finished")


if __name__ == "__main__":
    scrape()
