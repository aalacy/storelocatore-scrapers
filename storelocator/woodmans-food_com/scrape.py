from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("woodmans")

locator_domain = "https://www.woodmans-food.com/"
base_url = "https://www.woodmans-food.com/"


def _p(val):
    return (
        val.replace("(", "")
        .replace(")", "")
        .replace("-", "")
        .replace(" ", "")
        .strip()
        .isdigit()
    )


def fetch_data():
    with SgRequests() as session:
        res = session.get(base_url)
        soup = bs(res.text, "lxml")
        _tag = soup.find("span", string="Locations")
        links = _tag.next_sibling.next_sibling.findChildren("a")
        for link in links:
            page_url = link["href"]
            logger.info(page_url)
            r1 = session.get(page_url)
            soup1 = bs(r1.text, "lxml")
            block = [
                _.strip()
                for _ in soup1.select_one("div.store-content h4")
                .text.strip()
                .split("|")
            ]
            _split = block[1].split(",")
            hours_of_operation = ""
            if soup1.select_one("div.store-content p").text.strip():
                hours_of_operation = "; ".join(
                    soup1.select_one("div.store-content p")
                    .text.strip()
                    .split("|")[0]
                    .split(": ")[1]
                    .replace("++", "")
                    .replace("*", "")
                    .split(",")
                )
            coord = soup1.iframe["src"].split("!2d")[1].split("!2m")[0].split("!3d")
            phone = ""
            if _p(block[-1]):
                phone = block[-1]
            yield SgRecord(
                page_url=page_url,
                location_name=link.text,
                street_address=block[0].strip(),
                city=_split[0].strip(),
                state=_split[1].strip().split(" ")[0].strip(),
                zip_postal=_split[1].strip().split(" ")[1].strip(),
                country_code="US",
                phone=phone,
                latitude=coord[1],
                longitude=coord[0],
                locator_domain=locator_domain,
                hours_of_operation=hours_of_operation,
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
