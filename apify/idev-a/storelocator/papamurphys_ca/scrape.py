from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import parse_address_intl

logger = SgLogSetup().get_logger("papamurphys")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "http://papamurphys.ca/"
base_url = "https://papamurphys.ca/locations-list/"


def _p(val):
    if (
        val
        and val.replace("(", "")
        .replace(")", "")
        .replace("+", "")
        .replace("-", "")
        .replace(".", " ")
        .replace("to", "")
        .replace(" ", "")
        .strip()
        .isdigit()
    ):
        return val
    else:
        return ""


def fetch_data():
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        links = soup.select("div.container div.grid div.row-span-2.p-8")
        logger.info(f"{len(links)} found")
        for link in links:
            _addr = list(link.select_one("div.mt-6").stripped_strings)
            raw_address = " ".join(_addr)
            addr = parse_address_intl(raw_address + ", Canada")
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += " " + addr.street_address_2
            phone = ""
            if link.p.a and _p(link.p.a.text):
                phone = link.p.a.text.strip()
            hours = []
            for hh in link.select("h4.location_time"):
                if "delivery" in hh.text.lower():
                    break
                hours.append(hh.text.strip())

            coord = link.script.text.split("location_y+'/")[1].split('"')[0].split(",")
            state = link.find_parent().find_previous_sibling().text.strip()
            yield SgRecord(
                page_url=base_url,
                location_name=link.h2.text.strip(),
                street_address=street_address,
                city=addr.city,
                state=state,
                zip_postal=addr.postcode,
                country_code="CA",
                phone=phone,
                latitude=coord[0],
                longitude=coord[1],
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours).replace("–", "-"),
                raw_address=raw_address,
            )


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.RAW_ADDRESS}))
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
