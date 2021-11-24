from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgpostal import parse_address_intl

logger = SgLogSetup().get_logger("dunkindonuts")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "http://www.dunkindonuts.com.my"
base_url = "http://www.dunkindonuts.com.my/stores.html"


def fetch_data():
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        links = soup.select("div.panel div.col-md-4")
        logger.info(f"{len(links)} found")
        for link in links:
            block = list(link.p.stripped_strings)
            addr = parse_address_intl(block[1])
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += " " + addr.street_address_2
            phone = block[2].split(":")[-1].strip()
            if phone == "-" or phone == "N/A":
                phone = ""
            hours = []
            for hh in block[3:]:
                if "holiday" in hh.lower():
                    break
                hours.append(hh)
            yield SgRecord(
                page_url=base_url,
                location_name=link.strong.text.strip(),
                street_address=street_address,
                city=addr.city,
                state=addr.state,
                zip_postal=addr.postcode,
                country_code="Malaysia",
                phone=phone,
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours)
                .replace("\x80\x93", "-")
                .replace("â", ""),
            )


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.LOCATION_NAME,
                    SgRecord.Headers.STREET_ADDRESS,
                    SgRecord.Headers.ZIP,
                    SgRecord.Headers.PHONE,
                }
            )
        )
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
