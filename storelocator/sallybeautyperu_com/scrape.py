from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.sallybeautyperu.com"
base_url = "https://www.sallybeautyperu.com/tiendas"


def fetch_data():
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        locations = soup.select("ul.ul-tiendas li.li-tiendas")
        for _ in locations:
            street_address = _.select_one("p.dirección").text.strip()
            city = _.select_one("p.comuna").text.strip()
            raw_address = street_address + " " + city
            phone = ""
            if _.select_one("li.telefono"):
                phone = _.select_one("li.telefono").text.split(":")[-1].strip()
            if phone == "-":
                phone = ""
            hours = [hh.text.strip() for hh in _.select("li.atención")]
            coord = _.select_one("span.ubicacion").text.strip().split(",")
            yield SgRecord(
                page_url=base_url,
                location_name=" ".join(_.h3.stripped_strings),
                street_address=street_address,
                city=city.split("/")[0].strip(),
                state=city.split("/")[-1].strip(),
                country_code="Peru",
                phone=phone,
                latitude=coord[0].split(":")[-1],
                longitude=coord[1].split(":")[-1],
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
                raw_address=raw_address,
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.GeoSpatialId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
