from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import re

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.pfchangs.co.uk"
base_url = "https://www.pfchangs.co.uk/contact/"


def fetch_data():
    with SgRequests() as session:
        _ = bs(session.get(base_url, headers=_headers).text, "lxml")
        addr = list(_.select_one("div.address p").stripped_strings)
        coord = _.select_one("a.map-img")["href"].split("!3d")[1].split("!4d")
        yield SgRecord(
            page_url=base_url,
            street_address=" ".join(addr[:-2]),
            city=addr[-2].strip(),
            zip_postal=addr[-1].strip(),
            country_code="UK",
            phone=_.find("a", href=re.compile(r"tel:")).text.strip(),
            latitude=coord[0],
            longitude=coord[1],
            locator_domain=locator_domain,
            hours_of_operation=_.find("h3", string=re.compile(r"Opening Times:"))
            .find_next_sibling()
            .text.split(",")[0],
        )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.GeoSpatialId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
