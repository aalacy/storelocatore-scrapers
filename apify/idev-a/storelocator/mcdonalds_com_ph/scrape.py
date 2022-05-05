from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import json
from bs4 import BeautifulSoup as bs
from sgscrape.sgpostal import parse_address_intl

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://mcdonalds.com.ph"
base_url = "https://mcdonalds.com.ph/store-locator"


def fetch_data():
    with SgRequests() as session:
        locations = json.loads(
            bs(session.get(base_url, headers=_headers).text, "lxml")
            .select_one("store-locator")[":stores"]
            .replace("&quot;", '"')
        )
        for _ in locations:
            addr = parse_address_intl(_["address"] + ", Philippines")
            street_address = addr.street_address_1 or ""
            if addr.street_address_2:
                street_address += " " + addr.street_address_2
            if street_address:
                street_address = street_address.replace("Sm City", "")
            if street_address == "Juan":
                street_address = ", ".join(_["address"].split(",")[:2])

            yield SgRecord(
                page_url=base_url,
                store_number=_["id"],
                location_name=_["name"],
                street_address=street_address,
                city=_["city_name"],
                state=_["province_name"],
                country_code="Philippines",
                latitude=_["latitude"],
                longitude=_["longitude"],
                locator_domain=locator_domain,
                hours_of_operation=_["preview_description"]
                .split("):")[-1]
                .split("14:")[-1]
                .replace("Clo...", "Closed")
                .replace("P...", "PM")
                .replace("30...", "30PM"),
                raw_address=_["address"],
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
