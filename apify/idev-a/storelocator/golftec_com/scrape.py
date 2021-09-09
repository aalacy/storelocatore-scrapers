from sgrequests.sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries
from sglogging import SgLogSetup
from bs4 import BeautifulSoup as bs

logger = SgLogSetup().get_logger("golftec")
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}
locator_domain = "https://www.golftec.com"


def _p(val):
    if (
        val.replace("(", "")
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


def fetch_records(http, search):
    # Need to add dedupe. Added it in pipeline.
    maxZ = search.items_remaining()
    for lat, lng in search:
        if search.items_remaining() > maxZ:
            maxZ = search.items_remaining()
        url = f"https://wcms.golftec.com/loadmarkers_6.php?thelong={lng}&thelat={lat}&georegion=North+America&pagever=prod&maptype=closest10"
        locations = http.get(url, headers=headers).json()
        if "centers" in locations:
            for _ in locations["centers"]:
                page_url = f"{locator_domain}{_['link']}"
                res = http.get(page_url, headers=headers)
                if res.status_code != 200:
                    continue
                soup = bs(res.text, "lxml")
                street_address = _["street1"]
                if _["street2"]:
                    street_address += " " + _["street1"]
                hours = [
                    ": ".join(hh.stripped_strings)
                    for hh in soup.select(
                        "div.center-details__hours div.seg-center-hours ul li"
                    )
                ]
                yield SgRecord(
                    page_url=page_url,
                    store_number=_["cid"],
                    location_name=_["name"],
                    street_address=street_address,
                    city=_["city"],
                    state=_["state"],
                    zip_postal=_["zip"],
                    country_code=_["country"],
                    phone=_["phone"],
                    hours_of_operation="; ".join(hours),
                    locator_domain=locator_domain,
                )

            progress = (
                str(round(100 - (search.items_remaining() / maxZ * 100), 2)) + "%"
            )

            logger.info(f"[{lat}, {lng}] [{len(locations)}] | [{progress}]")


if __name__ == "__main__":
    search = DynamicGeoSearch(
        country_codes=[SearchableCountries.USA, SearchableCountries.CANADA],
        expected_search_radius_miles=100,
    )
    with SgWriter(
        deduper=SgRecordDeduper(
            RecommendedRecordIds.PageUrlId, duplicate_streak_failure_factor=3
        )
    ) as writer:
        with SgRequests() as http:
            for rec in fetch_records(http, search):
                writer.write_row(rec)
