from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
from sgscrape.sgpostal import parse_address_intl
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

logger = SgLogSetup().get_logger("joyalukkas")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://eshop.joyalukkas.com"
base_url = "https://eshop.joyalukkas.com/store/"


def fetch_data():
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        links = soup.select("div.store_item a")
        logger.info(f"{len(links)} found")
        for link in links:
            street_address = link["data-store_address_1"]
            _addr = []
            _addr.append(street_address)
            if link["data-store_address_2"]:
                _addr.append(link["data-store_address_2"])
            _addr.append(link["data-store_country"])
            raw_address = ", ".join(_addr).replace("IL60659", "IL 60659")
            addr = parse_address_intl(raw_address)
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += " " + addr.street_address_2
            if street_address:
                street_address = (
                    street_address.replace("Uae", "")
                    .replace("Qatar", "")
                    .replace("Oman", "")
                )
            if street_address and street_address.isdigit():
                street_address = link["data-store_address_1"]
            yield SgRecord(
                page_url=base_url,
                street_address=street_address,
                city=addr.city,
                state=addr.state,
                zip_postal=addr.postcode,
                country_code=link["data-store_country"],
                phone=link["data-store_phone"],
                locator_domain=locator_domain,
                latitude=link["data-longitude"],
                longitude=link["data-latitude"],
                raw_address=raw_address,
            )


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.LATITUDE,
                    SgRecord.Headers.LONGITUDE,
                    SgRecord.Headers.PHONE,
                    SgRecord.Headers.CITY,
                    SgRecord.Headers.STREET_ADDRESS,
                }
            )
        )
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
