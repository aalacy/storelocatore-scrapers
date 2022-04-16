from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import parse_address_intl

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.marieblachere.com/"
base_url = "https://boulangeries.marieblachere.com/wp-content/plugins/superstorefinder-wp/ssf-wp-xml.php?wpml_lang=&t=1648892710978"


def fetch_data():
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        locations = soup.select("item")
        for _ in locations:
            raw_address = _.address.text.strip()
            addr = parse_address_intl(raw_address + ", France")
            street_address = addr.street_address_1 or ""
            if addr.street_address_2:
                street_address += " " + addr.street_address_2
            if "Ouvre bientôt" in _.operatinghours.text:
                continue
            city = addr.city
            if addr.city:
                city = " ".join([cc for cc in addr.city.split() if not cc.isdigit()])
            yield SgRecord(
                page_url="https://boulangeries.marieblachere.com",
                store_number=_.storeid.text.strip(),
                location_name=_.location.text.strip(),
                street_address=street_address,
                city=city,
                state=addr.state,
                zip_postal=raw_address.split(",")[-1],
                country_code=_.country.text.strip() or "FR",
                latitude=_.latitude.text.strip(),
                longitude=_.longitude.text.strip(),
                locator_domain=locator_domain,
                raw_address=raw_address,
            )


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.RAW_ADDRESS}))
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
