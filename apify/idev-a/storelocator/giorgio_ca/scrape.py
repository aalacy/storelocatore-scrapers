from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
import re

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    locator_domain = "https://giorgio.ca/"
    base_url = "https://giorgio.ca/restaurants/"
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        locations = soup.select(
            "section.elementor-section.elementor-section-content-middle"
        )
        for _ in locations:
            location_name = _.select("h2.elementor-heading-title")[1].text
            block = list(_.select_one("div.elementor-text-editor p").stripped_strings)
            phone = _.find("a", href=re.compile(r"tel:")).text
            hours = []
            for hh in _.find(
                "div", string=re.compile(r"POUR EMPORTER")
            ).find_next_siblings("div"):
                if not hh.text.strip():
                    break

                hours.append(hh.text.strip())
            yield SgRecord(
                page_url=base_url,
                location_name=location_name,
                street_address=block[0],
                city=block[1].split(",")[0].strip(),
                state=block[1].split(",")[1].strip().split(" ")[0],
                zip_postal=" ".join(block[1].split(",")[1].strip().split(" ")[1:]),
                country_code="CA",
                phone=phone,
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
