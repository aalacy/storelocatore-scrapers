from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "http://www.carrefour.do"
base_url = "http://www.carrefour.do/nuestras-tiendras-carrefour/"


def fetch_data():
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        locations = soup.select("div.main-column div.vce-text-block div.row > div")
        for _ in locations:
            raw_address = _.p.text.strip()
            addr = raw_address.split(",")
            coord = _.iframe["src"].split("!2d")[1].split("!2m")[0].split("!3d")
            yield SgRecord(
                page_url=base_url,
                location_name=_.h3.text.strip(),
                street_address=" ".join(addr[:-1]),
                city=addr[-1].strip(),
                country_code="Domican Republic",
                phone=list(_.select("p")[-1].stripped_strings)[-1].replace(":", ""),
                latitude=coord[1],
                longitude=coord[0],
                locator_domain=locator_domain,
                raw_address=raw_address,
                hours_of_operation=list(_.select("p")[1].stripped_strings)[-1],
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.GeoSpatialId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
