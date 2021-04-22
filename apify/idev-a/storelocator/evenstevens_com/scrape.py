from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("evenstevens")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    locator_domain = "https://evenstevens.com/"
    base_url = "https://evenstevens.com/places/"
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        locations = soup.select(
            "section#utah div.l-section-h .g-cols > .vc_column_container > .vc_column-inner  .g-cols.wpb_row > .wpb_column"
        )
        logger.info(f"{len(locations)} found")
        for _ in locations:
            if not _.p:
                logger.info("skip")
                continue
            block = list(_.p.stripped_strings)
            sp1 = bs(session.get(_.a["href"], headers=_headers).text, "lxml")
            logger.info(_.a["href"])
            hours = list(sp1.select("div.wpb_wrapper p")[2].stripped_strings)
            yield SgRecord(
                page_url=_.a["href"],
                location_name=block[0],
                street_address=block[1],
                city=block[2].split(",")[0].strip(),
                state=block[2].split(",")[-1].strip(),
                country_code="US",
                phone=block[-1],
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours).replace("–", "-"),
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
