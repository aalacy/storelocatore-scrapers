from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
import re
import json
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("lionsden")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    locator_domain = "https://www.lionsden.com/"
    base_url = "https://www.lionsden.com/storelocator/"
    with SgRequests() as session:
        res = session.get(base_url, headers=_headers).text
        locations = json.loads(
            res.split("stores      :")[1].split("countLabel  :")[0].strip()[:-1]
        )
        for _ in locations:
            page_url = f"{locator_domain}store-{_['storelocator_id']}/"
            logger.info(page_url)
            sp = bs(session.get(page_url, headers=_headers).text, "lxml")
            hour_block = sp.find("h2", string=re.compile(r"Hours", re.IGNORECASE))
            hours = []
            for hh in hour_block.find_next_sibling("ul").select("li"):
                if "HOLIDAY" in hh.text:
                    continue
                if "**" in hh.text:
                    continue
                hours.append(
                    "-".join([ho.split("(")[0] for ho in hh.text.strip().split("-")])
                )
            yield SgRecord(
                page_url=page_url,
                store_number=_["storelocator_id"],
                location_name=_["name"],
                street_address=_["address"],
                city=_["city"],
                state=_["state"],
                latitude=_["latitude"],
                longitude=_["longtitude"],
                zip_postal=_["zipcode"],
                country_code=_["country"],
                phone=_["phone"],
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
