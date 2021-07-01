from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
import json

logger = SgLogSetup().get_logger("fit4less")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    locator_domain = "https://www.fit4less.ca"
    base_url = "https://www.fit4less.ca/memberships/locations"
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        links = soup.select("div#city-dropdown ul li")
        logger.info(f"{len(links)} found")
        for link in links:
            url = f"https://www.fit4less.ca/locations/provinces/{link['data-provname'].replace('.','').replace(' ','-')}/{link['data-cityname'].replace('.','').replace(' ','-')}"
            sp1 = bs(session.get(url, headers=_headers).text, "lxml")
            locations = sp1.select("div#LocationResults div.find-gym__result")
            logger.info(
                f"[{link['data-provname']}, {link['data-cityname']}] {len(locations)} found"
            )
            for _ in locations:
                page_url = locator_domain + _.a["href"]
                logger.info(page_url)
                sp2 = bs(session.get(page_url, headers=_headers).text, "lxml")
                addr = list(
                    _.select_one("p.find-gym__result--address").stripped_strings
                )
                hours = []
                temp = list(
                    sp2.select_one(
                        "div.hours-of-operation span.hours-hours"
                    ).stripped_strings
                )
                for x in range(0, len(temp), 2):
                    hours.append(f"{temp[x]} {temp[x+1]}")
                ss = json.loads(sp2.find("script", type="application/ld+json").string)
                phone = ""
                if _.select_one(".gym-details-info__phone"):
                    phone = _.select_one(".gym-details-info__phone").text.strip()
                yield SgRecord(
                    page_url=page_url,
                    location_name=_.a.text.strip(),
                    street_address=addr[0],
                    city=addr[1].split(",")[0].strip(),
                    state=addr[1].split(",")[1].strip().split("-")[0].strip(),
                    zip_postal=addr[1].split(",")[1].strip().split("-")[1].strip(),
                    country_code="CA",
                    phone=phone,
                    locator_domain=locator_domain,
                    latitude=ss["geo"]["latitude"],
                    longitude=ss["geo"]["longitude"],
                    hours_of_operation="; ".join(hours).replace("–", "-"),
                )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
