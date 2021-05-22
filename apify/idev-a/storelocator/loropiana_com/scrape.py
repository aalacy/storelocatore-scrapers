from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
import json

logger = SgLogSetup().get_logger("loropiana")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    locator_domain = "https://us.loropiana.com"
    base_url = "https://us.loropiana.com/en/stores"
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        links = soup.select("p.t-product-copy a")
        logger.info(f"{len(links)} found")
        for link in links:
            page_url = locator_domain + link["href"]
            logger.info(page_url)
            sp1 = bs(session.get(page_url, headers=_headers).text, "lxml")
            for script in sp1.find_all("script", type="application/ld+json"):
                _ = json.loads(script.string.strip())
                hours = []
                for hh in _.get("openingHoursSpecification", []):
                    hours.append(
                        f"{','.join(hh['dayOfWeek'])}: {hh['opens']}-{hh['closes']}"
                    )
                yield SgRecord(
                    page_url=page_url,
                    location_name=_["name"],
                    street_address=_["address"]["streetAddress"],
                    city=_["address"]["addressLocality"],
                    state=_["address"]["addressRegion"],
                    zip_postal=_["address"]["postalCode"],
                    country_code=_["address"]["addressCountry"],
                    phone=_.get("telephone", "").strip(),
                    locator_domain=locator_domain,
                    latitude=_["geo"]["latitude"],
                    longitude=_["geo"]["longitude"],
                    location_type=_["@type"],
                    hours_of_operation="; ".join(hours).replace("–", "-"),
                )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
