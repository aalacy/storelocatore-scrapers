from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
import json
import re

logger = SgLogSetup().get_logger("era")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    locator_domain = "https://www.era.com"
    base_url = "https://www.era.com/real-estate-agents"
    streets = []
    with SgRequests() as session:
        states = bs(session.get(base_url, headers=_headers).text, "lxml").select(
            "ul.hide-list-bullets a"
        )
        logger.info(f"{len(states)} states found")
        for state in states:
            state_url = locator_domain + state["href"]
            locations = bs(
                session.get(state_url, headers=_headers).text, "lxml"
            ).select("ul.hide-list-bullets a")
            for _ in locations:
                list_url = locator_domain + _["href"]
                logger.info(f"[List] {list_url}")
                sp1 = bs(session.get(list_url, headers=_headers).text, "lxml")
                if not sp1.find("script", string=re.compile(r"LocalBusiness")):
                    continue
                script = json.loads(
                    sp1.find("script", string=re.compile(r"LocalBusiness")).string
                )
                for ss in script["@graph"]:
                    logger.info(f"[{state.text}][page] {ss['url']}")
                    res = session.get(ss["url"], headers=_headers).text
                    latitude = (
                        res.split("window._METRO_LATITUDE =")[1]
                        .split("window._METRO_LONGITUDE =")[0]
                        .strip()[:-1]
                    )
                    longitude = (
                        res.split("window._METRO_LONGITUDE =")[1]
                        .split("var")[0]
                        .strip()[:-1]
                    )

                    street_address = ss["address"]["streetAddress"]
                    if street_address in streets:
                        continue
                    streets.append(street_address)
                    yield SgRecord(
                        page_url=ss["url"],
                        location_name=ss["name"],
                        street_address=street_address,
                        city=ss["address"]["addressLocality"],
                        state=ss["address"]["addressRegion"],
                        zip_postal=ss["address"]["postalCode"],
                        country_code=ss["address"]["addressCountry"],
                        phone=ss["telephone"],
                        locator_domain=locator_domain,
                        latitude=latitude,
                        longitude=longitude,
                    )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
