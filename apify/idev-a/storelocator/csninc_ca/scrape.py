from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
import json
import re

logger = SgLogSetup().get_logger("csncollision")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    locator_domain = "https://csncollision.com/"
    base_url = "https://csncollision.com/all-locations/"
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        locations = soup.select("div.shopLocal")
        logger.info(f"{len(locations)} found")
        for _ in locations:
            page_url = _.a["href"]
            logger.info(page_url)
            res = session.get(page_url, headers=_headers).text
            sp1 = bs(res, "lxml")
            addr = sp1.select_one("div.holder p").text.split(",")
            hours = (
                sp1.select("div.holder p")[1]
                .text.replace("Shop Hours:", "")
                .replace("|", ":")
                .replace("–", "-")
                .replace("\n", ";")
            )
            loc = json.loads(
                res.split("var csn_location =")[1].split("/*")[0].strip()[:-1]
            )
            phone = ""
            if sp1.find("a", href=re.compile(r"tel:")):
                phone = sp1.find("a", href=re.compile(r"tel:")).text.strip()
            yield SgRecord(
                page_url=page_url,
                location_name=loc["name"],
                street_address=" ".join(addr[:-3]),
                city=addr[-3],
                state=addr[-2],
                zip_postal=addr[-1],
                country_code="CA",
                phone=phone,
                locator_domain=locator_domain,
                latitude=loc["latitude"],
                longitude=loc["longitude"],
                hours_of_operation=hours.strip(),
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
