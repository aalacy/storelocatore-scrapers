from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgpostal import parse_address_intl
from bs4 import BeautifulSoup as bs

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    locator_domain = "https://yumyumdonuts.com/"
    base_url = "https://yumyumdonuts.com/maps_xml"
    page_url = "https://yumyumdonuts.com/locations"
    with SgRequests() as session:
        locs = bs(session.get(base_url, headers=_headers).text, "lxml").select("marker")
        for _ in locs:
            addr = parse_address_intl(_["address"])
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += " " + addr.street_address_2

            yield SgRecord(
                page_url=page_url,
                store_number=_["uuid"],
                location_name=_["location"],
                street_address=street_address,
                city=addr.city,
                state=addr.state,
                zip_postal=addr.postcode,
                latitude=_["ycoord"],
                longitude=_["xcoord"],
                country_code="US",
                phone=_["phone"],
                hours_of_operation=list(bs(_["desc"], "lxml").stripped_strings)[0],
                locator_domain=locator_domain,
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
