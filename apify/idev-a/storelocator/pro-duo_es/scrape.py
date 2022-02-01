from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import dirtyjson as json
from bs4 import BeautifulSoup as bs

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.pro-duo.es"
base_url = "https://www.pro-duo.es/tiendas"


def fetch_data():
    with SgRequests() as session:
        locations = json.loads(
            session.get(base_url, headers=_headers)
            .text.split("jQuery.extend(Drupal.settings,")[1]
            .split(");</script>")[0]
        )["openlayers"]["maps"]["openlayers-map"]["layers"][
            "stores_openlayers_vector_data_stores"
        ][
            "features"
        ]
        for loc in locations:
            _ = loc["attributes"]
            page_url = locator_domain + bs(_["title"], "lxml").a["href"]
            coord = (
                bs(_["field_store_location"], "lxml")
                .text.split("(")[1]
                .split(")")[0]
                .split()
            )
            addr = bs(_["field_store_address"], "lxml")
            hours = [
                " ".join(hh.stripped_strings)
                for hh in bs(_["field_store_opening_hours"], "lxml").select(
                    "span.oh-display"
                )
            ]
            if hours:
                hours.append("Do: cerrado")
            yield SgRecord(
                page_url=page_url,
                location_name=bs(_["title"], "lxml").text.strip(),
                street_address=addr.select_one("div.thoroughfare").text.strip(),
                city=addr.select_one("span.locality").text.strip(),
                state=addr.select_one("span.state").text.strip(),
                zip_postal=addr.select_one("span.postal-code").text.strip(),
                latitude=coord[1],
                longitude=coord[0],
                country_code="Spain",
                phone=bs(_["field_store_description"], "lxml").text.strip(),
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
                raw_address=" ".join(addr.stripped_strings),
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
