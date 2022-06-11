from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgpostal import parse_address_intl
from bs4 import BeautifulSoup as bs

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    locator_domain = "https://tacotimecanada.com/"
    base_url = "https://tacotimecanada.com/wp-content/plugins/superstorefinder-wp/ssf-wp-xml.php?wpml_lang=&t=1620063384973"
    page_url = "https://tacotimecanada.com/locations/"
    with SgRequests() as session:
        sp1 = bs(session.get(base_url, headers=_headers).text, "lxml")
        locations = sp1.find_all("item")
        for _ in locations:
            _addr = _.address.text.replace("&#44;", ",")
            addr = parse_address_intl(_addr)
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += " " + addr.street_address_2
            if "google" in street_address.lower():
                street_address = ""
            zip_postal = addr.postcode
            state = addr.state
            if not zip_postal:
                zip_postal = " ".join(_addr.split(",")[-1].strip().split(" ")[1:])
            if not state:
                state = _addr.split(",")[-1].strip().split(" ")[0]
            yield SgRecord(
                page_url=page_url,
                store_number=_.storeId.text if _.storeId else _.storeid.text,
                location_name=_.location.text,
                street_address=street_address,
                city=addr.city,
                state=state,
                zip_postal=zip_postal,
                latitude=_.latitude.text,
                longitude=_.longitude.text,
                country_code="CA",
                phone=_.telephone.text,
                locator_domain=locator_domain,
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
