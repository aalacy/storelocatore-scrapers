from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
import re
from sgpostal.sgpostal import parse_address_intl
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

logger = SgLogSetup().get_logger("fusionacademy")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    locator_domain = "https://www.fusionacademy.com/"
    base_url = "https://www.fusionacademy.com/campuses/"
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        locations = soup.select("div.location-block__card")
        logger.info(f"{len(locations)} found")
        for _ in locations:
            if not _.select_one("a.location-block__card--link"):
                continue
            page_url = (
                locator_domain
                + "campuses"
                + _.select_one("a.location-block__card--link")["href"]
            )
            logger.info(page_url)
            raw_address = " ".join(_.p.stripped_strings)
            if "Coming Soon" in raw_address:
                continue
            addr = parse_address_intl(raw_address)
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += " " + addr.street_address_2
            sp1 = bs(session.get(page_url, headers=_headers).text, "lxml")
            hours = ""
            _hr = sp1.find("label", string=re.compile(r"^Hours:"))
            if _hr:
                hours = _hr.find_next_sibling().text.strip()

            coord = ["", ""]
            try:
                coord = (
                    sp1.find("label", string=re.compile(r"Address"))
                    .find_next_sibling()
                    .a["href"]
                    .split("/@")[1]
                    .split("/data")[0]
                    .split(",")
                )
            except:
                iframe = sp1.select_one("div.map iframe")
                if iframe:
                    if iframe.has_attr("src"):
                        coord = (
                            iframe["src"]
                            .split("!2d")[1]
                            .split("!2m")[0]
                            .split("!3d")[::-1]
                        )
                    elif iframe.has_attr("nitro-lazy-src"):
                        coord = (
                            iframe["nitro-lazy-src"]
                            .split("!2d")[1]
                            .split("!2m")[0]
                            .split("!3d")[::-1]
                        )
            yield SgRecord(
                page_url=page_url,
                location_name=_.h6.text.strip(),
                street_address=street_address,
                city=addr.city,
                state=addr.state,
                zip_postal=addr.postcode,
                country_code="US",
                phone=_.select_one(".location-block__card--telephone a").text.strip(),
                locator_domain=locator_domain,
                latitude=coord[0],
                longitude=coord[1],
                hours_of_operation=hours.replace("–", "-"),
                raw_address=raw_address,
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
