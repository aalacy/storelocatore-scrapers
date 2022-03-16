from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
from sgscrape.sgpostal import parse_address_intl

logger = SgLogSetup().get_logger("thedonutanddog")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    locator_domain = "https://www.thedonutanddog.com/"
    base_url = "https://www.thedonutanddog.com/"
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        locations = soup.select("div#new-page-page div.sqs-block.image-block figure")
        logger.info(f"{len(locations)} found")
        for _ in locations:
            if _.img and "coming" in _.img["alt"].lower():
                continue
            if "Relocating" in _.select_one(".image-subtitle").text:
                continue
            block = []
            for tt in _.select_one(".image-subtitle").stripped_strings:
                if "Located in" in tt or "TEMPORARY HOURS" in tt:
                    continue

                block.append(tt)
            addr = parse_address_intl(block[1])
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += " " + addr.street_address_2
            yield SgRecord(
                page_url=base_url,
                location_name=_.select_one(".image-title").text.strip(),
                street_address=street_address,
                city=addr.city,
                state=addr.state,
                zip_postal=addr.postcode,
                country_code="US",
                phone=block[0],
                locator_domain=locator_domain,
                hours_of_operation="; ".join(block[2:]).replace("–", "-"),
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
