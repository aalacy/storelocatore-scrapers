from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("banzaibowls")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    locator_domain = "https://banzaibowls.com/"
    base_url = "https://banzaibowls.com/locations/"
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        locations = soup.select(
            "div.section_wrapper.mcb-section-inner div.wrap.mcb-wrap.one"
        )
        for _ in locations:
            block = list(_.h4.stripped_strings)
            logger.info(_.h1.text)
            state_zip = " ".join(block[1].split(",")[1:]).strip()
            coord = _.iframe["src"].split("!2d")[1].split("!2m")[0].split("!3d")
            yield SgRecord(
                page_url=base_url,
                location_name=_.h1.text,
                street_address=block[0],
                city=block[1].split(",")[0].strip(),
                state=state_zip.split(" ")[0].strip(),
                zip_postal=state_zip.split(" ")[-1].strip(),
                country_code="US",
                latitude=coord[1],
                longitude=coord[0],
                phone=block[-1],
                locator_domain=locator_domain,
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
