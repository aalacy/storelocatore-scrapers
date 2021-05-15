from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
from sgscrape.sgpostal import parse_address_intl
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
        links = soup.select("div.shopProvince div.shopLocal")
        logger.info(f"{len(links)} found")
        for link in links:
            page_url = link.a["href"]
            logger.info(page_url)
            res = session.get(page_url, headers=_headers).text
            sp1 = bs(res, "lxml")
            script = json.loads(
                res.split("var csn_location =")[1].split("/*")[0].strip()[:-1]
            )
            addr = parse_address_intl(script["address"])
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += " " + addr.street_address_2
            temp = (
                sp1.select("div.holder p")[1]
                .text.replace("Shop Hours:", "")
                .replace("(winter only)", "")
                .replace("Shop Hours", "")
                .replace("|", ":")
                .replace("–", "-")
                .split("or")[0]
                .strip()
                .replace("\n", ";")
            )
            hours = []
            for hh in temp.split(";"):
                if "appointment" in hh.lower():
                    continue
                hours.append(hh)
            phone = ""
            if sp1.find("a", href=re.compile(r"tel:")):
                phone = sp1.find("a", href=re.compile(r"tel:")).text
            yield SgRecord(
                page_url=page_url,
                location_name=script["name"].replace("’", "'"),
                street_address=street_address,
                city=addr.city,
                state=addr.state,
                zip_postal=addr.postcode,
                country_code="CA",
                phone=phone,
                locator_domain=locator_domain,
                latitude=script["latitude"],
                longitude=script["longitude"],
                hours_of_operation="; ".join(hours),
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
