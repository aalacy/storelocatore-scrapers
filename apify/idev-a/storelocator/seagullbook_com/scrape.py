from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
from sgscrape.sgpostal import parse_address_intl
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

logger = SgLogSetup().get_logger("seagullbook")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.seagullbook.com"
base_url = "https://www.seagullbook.com/our-stores.html"


def _d(location_name, _addr, coord, hours):
    addr = parse_address_intl(list(_addr.stripped_strings)[0].replace("|", "").strip())
    street_address = addr.street_address_1
    if addr.street_address_2:
        street_address += " " + addr.street_address_2
    return SgRecord(
        page_url=base_url,
        location_name=location_name,
        street_address=street_address,
        city=addr.city,
        state=addr.state,
        zip_postal=addr.postcode,
        country_code="US",
        phone=_addr.a.text.strip(),
        locator_domain=locator_domain,
        latitude=coord[0],
        longitude=coord[1],
        hours_of_operation=hours.replace("–", "-"),
    )


def fetch_data():
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        links = soup.select("div#STORES li")
        logger.info(f"{len(links)} found")
        location_name = soup.select_one("div#STORES a").text.strip()
        try:
            coord = (
                soup.select_one("div#STORES a")["href"]
                .split("/@")[1]
                .split("/data")[0]
                .split(",")
            )
        except:
            coord = ["", ""]
        _addr = soup.select_one("div#STORES a").find_next_sibling("p")
        hours = (
            _addr.find_next_sibling("p").text.replace("Hours:", "").replace("Hours", "")
        )
        yield _d(location_name, _addr, coord, hours)
        for link in links:
            hours = (
                "; ".join(link.select("p")[-1].stripped_strings)
                .replace("Hours:", "")
                .replace("Hours", "")
            )
            try:
                coord = link.a["href"].split("/@")[1].split("/data")[0].split(",")
            except:
                coord = ["", ""]
            yield _d(link.a.text.strip(), link.p, coord, hours)


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.CITY,
                    SgRecord.Headers.PHONE,
                    SgRecord.Headers.STREET_ADDRESS,
                }
            )
        )
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
