from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
import json
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import us

ca_provinces_codes = {
    "AB",
    "BC",
    "MB",
    "NB",
    "NL",
    "NS",
    "NT",
    "NU",
    "ON",
    "PE",
    "QC",
    "SK",
    "YT",
}

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.lineagelogistics.com"
base_url = "https://www.lineagelogistics.com/facilities"


def get_country_by_code(code=""):
    if us.states.lookup(code):
        return "US"
    elif code in ca_provinces_codes:
        return "CA"
    else:
        return "<MISSING>"


def fetch_data():
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        locations = json.loads(
            soup.select_one(
                'script[data-drupal-selector="drupal-settings-json"]'
            ).string
        )["geofield_google_map"]["geofield-map-view-facilities-attachment-1"]["data"][
            "features"
        ]
        for loc in locations:
            _ = loc["properties"]
            info = bs(_["description"], "lxml")
            if not info.select_one("p.map-card__address"):
                continue
            addr = list(info.select_one("p.map-card__address").stripped_strings)
            phone = ""
            if info.select_one("a.map-card__phone"):
                phone = info.select_one("a.map-card__phone").text.strip()
            street_address = info.select_one("span.address-line1").text.strip()
            if info.select_one("span.address-line2"):
                street_address += (
                    " " + info.select_one("span.address-line2").text.strip()
                )

            city = state = zip_postal = ""
            if info.select_one("span.locality"):
                city = info.select_one("span.locality").text.strip()
            if info.select_one("span.administrative-area"):
                state = info.select_one("span.administrative-area").text.strip()
            if info.select_one("span.postal-code"):
                zip_postal = info.select_one("span.postal-code").text.strip()

            yield SgRecord(
                page_url=locator_domain + info.select_one("a.link__link")["href"],
                store_number=_["entity_id"],
                location_name=bs(_["data"]["title"], "lxml").text.strip(),
                street_address=street_address.split("(")[0].strip(),
                city=city,
                state=state,
                zip_postal=zip_postal,
                country_code=get_country_by_code(state),
                phone=phone,
                locator_domain=locator_domain,
                latitude=loc["geometry"]["coordinates"][1],
                longitude=loc["geometry"]["coordinates"][0],
                raw_address=" ".join(addr),
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
