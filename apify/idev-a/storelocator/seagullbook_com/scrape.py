from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
import bs4
from sglogging import SgLogSetup
from sgpostal.sgpostal import parse_address_intl
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

logger = SgLogSetup().get_logger("seagullbook")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.seagullbook.com"
base_url = "https://www.seagullbook.com/our-stores.html"


def _d(location_name, raw_address, coord, hours, phone):
    addr = parse_address_intl(raw_address + ", United States")
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
        phone=phone,
        locator_domain=locator_domain,
        latitude=coord[0],
        longitude=coord[1],
        hours_of_operation=hours.replace("–", "-"),
        raw_address=raw_address,
    )


def fetch_data():
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        divs = soup.select("div#STORES div")
        for div in divs:
            location_name = raw_address = phone = hours = ""
            coord = []
            children = div.findChildren(recursive=False)
            blocks = [children[0]] + [aa for aa in children[0].next_siblings]
            for ch in blocks:
                if isinstance(ch, bs4.element.Tag) and ch.name == "a":
                    tt = ch.text.strip()
                    if not tt:
                        continue
                    if "tel" in ch["href"]:
                        phone = tt
                    else:
                        location_name = tt
                        try:
                            coord = (
                                ch["href"].split("/@")[1].split("/data")[0].split(",")
                            )
                        except:
                            coord = ["", ""]
                if isinstance(ch, bs4.element.NavigableString):
                    if not ch.strip():
                        continue
                    if "Hours" in ch:
                        hours = ch.replace("Hours:", "").strip()
                    else:
                        raw_address = ch.replace("|", "").strip()

                if location_name and hours:
                    yield _d(location_name, raw_address, coord, hours, phone)
                    location_name = raw_address = phone = hours = ""
                    coord = []


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.RAW_ADDRESS,
                }
            )
        )
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
