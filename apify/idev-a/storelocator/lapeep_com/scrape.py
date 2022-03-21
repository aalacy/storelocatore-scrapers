from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import SgLogSetup
import re
import json

logger = SgLogSetup().get_logger("lepeep")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://lepeep.com"
base_url = "https://lepeep.com/locations/"


def fetch_data():
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        locations = soup.select("div#wpsl-stores li")
        for _ in locations:
            street_address = _.select_one("span.wpsl-street").text.strip()
            raw_address = [street_address]
            city_state = (
                _.select_one("span.wpsl-street").find_next_sibling().text.strip()
            )
            raw_address.append(city_state)
            name = list(_.select_one("span.store-title").stripped_strings)
            location_type = ""
            if len(name) > 1 and "Indoor" not in name[-1]:
                location_type = name[-1]
            phone = ""
            if _.find("a", href=re.compile(r"tel:")):
                phone = _.find("a", href=re.compile(r"tel:")).text.strip()
            hours = [
                ": ".join(hh.stripped_strings)
                for hh in _.select("table.wpsl-opening-hours tr")
            ]
            page_url = _.select_one("span.store-title a")["href"]
            logger.info(page_url)
            info = json.loads(
                session.get(page_url, headers=_headers)
                .text.split("var wpslMap_0 =")[1]
                .split("/* ]]> */")[0]
                .strip()[:-1]
            )["locations"][0]
            yield SgRecord(
                page_url=page_url,
                location_name=info["store"],
                street_address=street_address,
                city=info["city"],
                state=info["state"],
                zip_postal=info["zip"],
                country_code="US",
                phone=phone,
                latitude=info["lat"],
                longitude=info["lng"],
                locator_domain=locator_domain,
                location_type=location_type,
                hours_of_operation="; ".join(hours),
                raw_address=" ".join(raw_address),
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
