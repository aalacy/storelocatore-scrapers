from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgpostal import parse_address_intl

logger = SgLogSetup().get_logger("hastymarketcorp")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://hastymarketcorp.com"
base_url = "https://hastymarketcorp.com/wp-content/plugins/superstorefinder-wp/ssf-wp-xml.php?wpml_lang=&t=1627674043151"


def fetch_data():
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        links = soup.select("store item")
        logger.info(f"{len(links)} found")
        for link in links:
            addr = parse_address_intl(link.address.text)
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += " " + addr.street_address_2
            city = addr.city
            if "Fegus" in street_address:
                street_address = street_address.replace("Fegus", "").strip()
                city = "Fegus"
            phone = link.telephone.text.replace("TBD", "").replace("N/A", "").strip()
            if phone == "0":
                phone = ""
            yield SgRecord(
                page_url="https://hastymarketcorp.com/locations/",
                store_number=link.storeId.text.strip()
                if link.storeId
                else link.storeid.text.strip(),
                location_name=link.location.text.strip(),
                street_address=street_address,
                city=city,
                state=addr.state,
                zip_postal=addr.postcode,
                country_code="Canada",
                phone=phone,
                locator_domain=locator_domain,
                latitude=link.latitude.text.strip(),
                longitude=link.longitude.text.strip(),
                raw_address=link.address.text,
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
