from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import parse_address_intl

logger = SgLogSetup().get_logger("pirch")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def _c(val):
    if val.startswith(";"):
        val = val[1:]
    return val


locator_domain = "https://www.pirch.com"
base_url = "https://www.pirch.com/showrooms/"


def fetch_data():
    with SgRequests() as session:
        locations = bs(session.get(base_url, headers=_headers).text, "lxml").select(
            "div.elementor-column.elementor-col-14"
        )
        logger.info(f"{len(locations)} found")
        for _ in locations:
            page_url = _.a["href"]
            logger.info(page_url)
            sp1 = bs(session.get(page_url, headers=_headers).text, "lxml")
            note = sp1.select_one("div.elementor-widget-container p strong span")
            if note and "Showroom Opening" in note.text:
                continue
            raw_address = " ".join(_.p.stripped_strings)
            addr = parse_address_intl(raw_address)
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += " " + addr.street_address_2
            hours = []
            for hh in sp1.select("table.uael-table tr"):
                hours.append(": ".join(hh.stripped_strings))
            try:
                coord = (
                    sp1.select(
                        "div#content section.elementor-section-height-default.elementor-section-boxed div.elementor-button-wrapper a"
                    )[1]["href"]
                    .split("/%40")[1]
                    .split("/data")[0]
                    .split(",")
                )
            except:
                coord = ["", ""]
            yield SgRecord(
                page_url=page_url,
                location_name=_.h3.text.replace("\n", " ").strip(),
                street_address=street_address,
                city=addr.city,
                state=addr.state,
                zip_postal=addr.postcode,
                country_code="US",
                phone=_.strong.text.strip(),
                locator_domain=locator_domain,
                latitude=_c(coord[0]),
                longitude=_c(coord[1]),
                hours_of_operation="; ".join(hours).replace("–", "-"),
                raw_address=raw_address,
            )


if __name__ == "__main__":
    with SgWriter(deduper=SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
