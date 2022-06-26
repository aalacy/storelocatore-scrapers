from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgpostal import parse_address_intl

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "http://www.pfchangs.com.ar"
base_url = "http://www.pfchangs.com.ar/contacto/"


def fetch_data():
    with SgRequests() as session:
        _ = bs(session.get(base_url, headers=_headers).text, "lxml")
        h5 = _.select("h5")
        raw_address = " ".join([aa.text.strip() for aa in h5[2:4]])
        addr = parse_address_intl(raw_address)
        street_address = addr.street_address_1
        if addr.street_address_2:
            street_address += " " + addr.street_address_2
        yield SgRecord(
            page_url=base_url,
            location_name=h5[0].text.strip(),
            street_address=street_address,
            city=addr.city,
            state=addr.state,
            zip_postal=addr.postcode,
            country_code="Argentina",
            phone=h5[1].text.strip(),
            latitude=list(h5[-2].stripped_strings)[-1],
            longitude=list(h5[-1].stripped_strings)[-1],
            locator_domain=locator_domain,
            raw_address=raw_address,
        )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.GeoSpatialId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
