from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
import json

logger = SgLogSetup().get_logger("mattressworldnorthwest")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    locator_domain = "https://www.mattressworldnorthwest.com/"
    base_url = "https://www.mattressworldnorthwest.com/store-locations/"
    with SgRequests() as session:
        res = session.get(base_url, headers=_headers).text
        locations = json.loads(
            res.split("var stores =")[1].split("/* ]]> */")[0].strip()[:-1]
        )
        for _ in locations:
            page_url = bs(_["popup_content"], "lxml").a["href"]
            sp1 = bs(session.get(page_url, headers=_headers).text, "lxml")
            block = list(sp1.select_one("div.address").stripped_strings)
            hours = []
            for x, hh in enumerate(block):
                if hh == "Stores are open!":
                    hours = block[x + 1 :]

            for x, hh in enumerate(hours):
                if "Now Open" in hh:
                    del hours[x]
            logger.info(page_url)

            yield SgRecord(
                page_url=page_url,
                location_name=sp1.select_one('h1[itemprop="name"]').text,
                street_address=sp1.select_one(
                    'div[itemprop="address"] span[itemprop="streetAddress"]'
                ).text,
                city=sp1.select_one(
                    'div[itemprop="address"] span[itemprop="addressLocality"]'
                ).text,
                state=sp1.select_one(
                    'div[itemprop="address"] span[itemprop="addressRegion"]'
                ).text,
                zip_postal=sp1.select_one(
                    'div[itemprop="address"] span[itemprop="postalCode"]'
                ).text,
                country_code="US",
                latitude=_["latitude"],
                longitude=_["longitude"],
                locator_domain=locator_domain,
                phone=sp1.select_one('span[itemprop="telephone"]').text,
                hours_of_operation="; ".join(hours).replace("–", "-"),
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
