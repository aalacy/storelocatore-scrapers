from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries
from sglogging import SgLogSetup
from bs4 import BeautifulSoup as bs
from sgselenium import SgChrome
import ssl
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification

logger = SgLogSetup().get_logger("roundtablepizza")

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

locator_domain = "https://roundtablepizza.com/"


def _p(val):
    if (
        val
        and val.replace("(", "")
        .replace(")", "")
        .replace("+", "")
        .replace("-", "")
        .replace(".", " ")
        .replace("to", "")
        .replace(" ", "")
        .strip()
        .isdigit()
    ):
        return val
    else:
        return ""


def fetch_records(search):
    # Need to add dedupe. Added it in pipeline.
    with SgRequests() as session:
        maxZ = search.items_remaining()
        total = 0
        with SgChrome() as driver:
            for lat, lng in search:
                if search.items_remaining() > maxZ:
                    maxZ = search.items_remaining()
                logger.info(("Pulling Geo Code %s..." % lat, lng))
                url = f"https://ordering.roundtablepizza.com/Site/rtp/Locations?isFrame=False&lat={lat}&lon={lng}&IsInit=false"
                locations = bs(session.get(url, headers=headers).text, "lxml").select(
                    "section > div.locationInfo"
                )
                total += len(locations)
                for _ in locations:
                    page_url = (
                        _.select_one("a.locationName")["href"]
                        if _.select_one("a.locationName")
                        else ""
                    )
                    addr = list(
                        _.select("div.locationInfoBox > div")[1].stripped_strings
                    )
                    zip_postal = addr[1].split(",")[1].strip().split(" ")[-1].strip()
                    phone = _p(addr[-1])
                    hours = []
                    if page_url and page_url != "https://pinol03.intouchposonline.com":
                        logger.info(f"[url] {page_url}")
                        try:
                            sp1 = bs(
                                session.get(page_url, headers=headers, timeout=15).text,
                                "lxml",
                            )
                            hours = [
                                ": ".join(hh.stripped_strings)
                                for hh in sp1.select("#openHours ul li")
                            ]
                            if sp1.select_one("span.phone"):
                                phone = sp1.select_one("span.phone").text.strip()
                            if not hours:
                                driver.get(page_url)
                                sp1 = bs(driver.page_source, "lxml")
                                zip_postal = sp1.select_one("span.zip").text.strip()
                                for hh in sp1.select(
                                    "div.dayHoursContainer div.dayHours"
                                ):
                                    hours.append(
                                        f"{hh.select_one('span.startDayContainer').text.strip()}: {''.join(hh.select_one('span.timeContainer').stripped_strings)}"
                                    )
                        except:
                            pass

                    coord = (
                        _.select_one("a.locationCenter")["onclick"]
                        .split("(")[1]
                        .split(")")[0]
                        .split(",")
                    )
                    latitude = float(coord[0].strip()[1:-1])
                    longitude = float(coord[1].strip()[1:-1])
                    search.found_location_at(
                        latitude,
                        longitude,
                    )
                    yield SgRecord(
                        page_url=page_url,
                        store_number=_["data-companyseq"],
                        location_name=_.select_one(".locationName").text.strip(),
                        street_address=addr[0],
                        city=addr[1].split(",")[0].strip(),
                        state=addr[1].split(",")[1].strip().split(" ")[0].strip(),
                        zip_postal=zip_postal,
                        phone=phone,
                        locator_domain=locator_domain,
                        country_code="us",
                        hours_of_operation="; ".join(hours).replace("–", "-"),
                        raw_address=" ".join(addr),
                    )
                progress = (
                    str(round(100 - (search.items_remaining() / maxZ * 100), 2)) + "%"
                )

                if len(locations):
                    logger.info(
                        f"found: {len(locations)} | total: {total} | progress: {progress}"
                    )


if __name__ == "__main__":
    search = DynamicGeoSearch(country_codes=[SearchableCountries.USA])
    with SgWriter(
        SgRecordDeduper(
            RecommendedRecordIds.StoreNumberId, duplicate_streak_failure_factor=100
        )
    ) as writer:
        for rec in fetch_records(search):
            writer.write_row(rec)
