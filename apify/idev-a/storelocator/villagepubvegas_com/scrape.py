from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
from sgscrape.sgpostal import parse_address_intl

logger = SgLogSetup().get_logger("villagepubvegas")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    locator_domain = "https://www.villagepubvegas.com/"
    base_url = "https://www.villagepubvegas.com/locations"
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        locations = soup.select("#footerBlocksMiddle p")
        logger.info(f"{len(locations)} found")
        for _ in locations:
            block = list(_.stripped_strings)
            addr = parse_address_intl(block[1].split("\xa0 \xa0")[0])
            phone = block[-1]
            if len(block) < 3:
                phone = block[1].split("\xa0 \xa0")[-1]
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += " " + addr.street_address_2
            try:
                coord = _.a["href"].split("/@")[1].split("/data")[0].split(",")
            except:
                coord = ["", ""]
            yield SgRecord(
                page_url=base_url,
                location_name=block[0],
                street_address=street_address,
                city=addr.city,
                state=addr.state,
                zip_postal=addr.postcode,
                country_code="US",
                phone=phone.replace("\xa0", " "),
                locator_domain=locator_domain,
                latitude=coord[0],
                longitude=coord[1],
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
