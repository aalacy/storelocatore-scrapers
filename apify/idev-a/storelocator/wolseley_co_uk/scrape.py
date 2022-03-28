import dirtyjson as json
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import re
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


base_url = "https://www.wolseley.co.uk/branch/#accordianContainer"
locator_domain = "https://www.wolseley.co.uk/"


def request_with_retries(url):
    with SgRequests() as session:
        return session.get(url, headers=_headers)


def fetch_data():
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        links = soup.select("div.branchList div.storeDetail a")
        logger.info(f"{len(links)} found")
        for link in links:
            page_url = link["href"]
            res = request_with_retries(page_url)
            if res.url.__str__() == locator_domain:
                continue
            sp1 = bs(res.text, "lxml")
            logger.info(page_url)
            _ = json.loads(sp1.find("script", type="application/ld+json").string)
            ss = json.loads(
                sp1.find("script", string=re.compile(r"var storeLocationsJson"))
                .string.split("var storeLocationsJson =")[1]
                .strip()[:-1]
            )[0]
            addr = _["address"]
            hours = []
            temp = list(sp1.select_one("dl.openingHoursList").stripped_strings)
            for x in range(0, len(temp), 2):
                hours.append(f"{temp[x]} {temp[x+1]}")
            street_address = " ".join(
                [
                    aa
                    for aa in addr["streetAddress"].replace("\n", "").strip().split()
                    if aa.strip()
                ]
            )
            yield SgRecord(
                page_url=page_url,
                location_name=_["name"],
                street_address=street_address,
                city=addr["addressLocality"],
                state=addr["addressRegion"],
                zip_postal=ss["postalCode"],
                country_code=addr["addressCountry"],
                phone=_["telephone"],
                locator_domain=locator_domain,
                latitude=ss["latitude"],
                longitude=ss["longitude"],
                hours_of_operation="; ".join(hours).replace("–", "-"),
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
