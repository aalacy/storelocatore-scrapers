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

locator_domain = "http://dunkindonuts.com.sg"
base_url = "http://dunkindonuts.com.sg/stores/"


def fetch_data():
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        links = soup.select("table td p")
        logger.info(f"{len(links)} found")
        for link in links:
            hours = []
            phone = ""
            _addr = []
            blocks = list(link.stripped_strings)[1:]
            for x, block in enumerate(blocks):
                if "tel" in block.lower():
                    phone = block.lower().split(":")[-1].replace("tel", "")
                    hours = blocks[x + 1 :]
                    _addr = blocks[:x]
            addr = parse_address_intl(" ".join(_addr))
            zip_postal = addr.postcode
            if len(_addr) == 2:
                street_address = _addr[0]
                if "singapore" in _addr[1].split(",")[0].lower():
                    street_address += " " + _addr[1].split(",")[0]
            elif len(_addr) == 3:
                street_address = " ".join(_addr[:-1])
            if not zip_postal:
                zip_postal = _addr[-1].split(" ")[-1]
            yield SgRecord(
                page_url=base_url,
                location_name=link.strong.text.strip(),
                street_address=street_address,
                city="Singapore",
                zip_postal=zip_postal,
                country_code="Singapore",
                phone=phone,
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours).replace("–", "-"),
            )
        links = soup.select("table td")
        logger.info(f"{len(links)} found")
        for td in links:
            second_loc = td.select("p")[0].strong.text.strip()
            blocks = []
            for block in list(td.stripped_strings):
                if second_loc == block.strip():
                    break
                blocks.append(block)
            hours = []
            phone = ""
            _addr = []
            for x, block in enumerate(blocks):
                if "tel" in block.lower():
                    phone = block.lower().split(":")[-1].replace("tel", "")
                    hours = blocks[x + 1 :]
                    _addr = blocks[:x]
            addr = parse_address_intl(" ".join(_addr))
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += " " + addr.street_address_2
            yield SgRecord(
                page_url=base_url,
                location_name=blocks[0],
                street_address=street_address,
                city=addr.city,
                state=addr.state,
                zip_postal=addr.postcode,
                country_code="Singapore",
                phone=phone,
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours).replace("–", "-"),
            )


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {
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
