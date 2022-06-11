from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import parse_address_intl

logger = SgLogSetup().get_logger("gratergrilledcheese")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    locator_domain = "https://gratergrilledcheese.com"
    base_url = "https://gratergrilledcheese.com/locations/"
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        links = soup.select("div.et_pb_row_1 a")
        logger.info(f"{len(links)} found")
        for link in links:
            page_url = locator_domain + link["href"]
            logger.info(page_url)
            sp1 = bs(session.get(page_url, headers=_headers).text, "lxml")
            _addr = list(sp1.select("div.et_pb_text_inner p")[1].stripped_strings)
            raw_address = " ".join(_addr)
            addr = parse_address_intl(raw_address)
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += " " + addr.street_address_2
            hours = [
                hh.text.replace("|", "")
                for hh in sp1.select("div.et_pb_text_inner p")[3:]
            ]
            try:
                coord = (
                    sp1.select("div.et_pb_text_inner p")[1]
                    .a["href"]
                    .split("/@")[1]
                    .split("/data")[0]
                    .split(",")
                )
            except:
                coord = ["", ""]
            yield SgRecord(
                page_url=page_url,
                location_name=sp1.select_one("div.et_pb_text_inner p").text.strip(),
                street_address=street_address,
                city=addr.city,
                state=addr.state,
                zip_postal=addr.postcode,
                country_code="US",
                phone=sp1.select("div.et_pb_text_inner p")[2]
                .text.split(":")[-1]
                .replace("Tel", "")
                .strip(),
                locator_domain=locator_domain,
                latitude=coord[0],
                longitude=coord[1],
                hours_of_operation="; ".join(hours).replace("–", "-"),
                raw_address=raw_address,
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
