from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgpostal.sgpostal import parse_address_intl
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from bs4 import BeautifulSoup as bs
import json
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://pepco.eu"
base_url = "https://pepco.eu/find-store/"
json_url = "https://pepco.eu/wp-admin/admin-ajax.php"


def fetch_data():
    with SgRequests() as session:
        locations = json.loads(
            bs(session.get(base_url, headers=_headers).text, "lxml")
            .select_one("div#js-shops-map")["shops-map-markers"]
            .replace("&quot;", '"')
        )
        for _ in locations:
            logger.info(_["shop_id"])
            data = {"action": "get_shop", "id": str(_["shop_id"])}
            sp1 = bs(
                session.post(json_url, headers=_headers, data=data)
                .json()["shop"]
                .replace("\n", ""),
                "lxml",
            )
            raw_address = sp1.select_one("p.find-shop-box__text").text.strip()
            addr = parse_address_intl(raw_address)
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += " " + addr.street_address_2
            hours = [
                ": ".join(hh.stripped_strings)
                for hh in sp1.select("table.find-shop-box__open-table tr")
            ]
            latitude = _["coordinates"]["lat"]
            longitude = _["coordinates"]["lng"]
            if latitude == "0E-12":
                latitude = ""
            if longitude == "0E-12":
                longitude = ""
            yield SgRecord(
                page_url=base_url,
                store_number=_["shop_id"],
                location_name=sp1.h3.text.strip(),
                street_address=street_address,
                city=addr.city,
                state=addr.state,
                zip_postal=addr.postcode,
                latitude=latitude,
                longitude=longitude,
                country_code=addr.country,
                locator_domain=locator_domain,
                raw_address=raw_address,
                hours_of_operation="; ".join(hours),
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
