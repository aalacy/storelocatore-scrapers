from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("carrossier")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    locator_domain = "https://carrossier-procolor.com/"
    base_url = "https://carrossier-procolor.com/wp-content/plugins/Pro-Color-Locations/templates/results.json"
    with SgRequests() as session:
        locations = session.get(base_url, headers=_headers).json()
        logger.info(f"{len(locations)} found")
        for _ in locations:
            logger.info(_["web"])
            sp1 = bs(session.get(_["web"], headers=_headers).text, "lxml")
            yield SgRecord(
                page_url=_["web"],
                store_number=_["id"],
                location_name=_["name"],
                street_address=_["address"].strip(),
                city=_["city"].strip(),
                state=_["province"].strip(),
                zip_postal=sp1.select_one('div[itemprop="postalCode"]').text.strip(),
                latitude=_["lat"],
                longitude=_["lng"],
                country_code="US",
                phone=_["phone"],
                locator_domain=locator_domain,
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
