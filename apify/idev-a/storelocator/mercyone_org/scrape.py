from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import SgLogSetup
import json
import re

logger = SgLogSetup().get_logger("mercyone")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.mercyone.org"
base_url = "https://www.mercyone.org/find-a-location/"


def fetch_data():
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        links = soup.select("div#site-body div.container p a")
        for link in links:
            loc_url = link["href"] + "/location-results?page=1&count=1000"
            logger.info(loc_url)
            res = session.get(loc_url, headers=_headers)
            if res.status_code != 200:
                loc_url = link["href"] + "/locations-results?page=1&count=1000"
                logger.info(loc_url)
                res = session.get(loc_url, headers=_headers)
            sp1 = bs(res.text, "lxml")
            script = re.split(
                r"var\smoduleInstanceData_IH_PublicDetailView(\w+)\s=",
                sp1.find_all("script", string=re.compile(r"var g_ihApplicationPath"))[
                    -1
                ].string,
            )
            locations = json.loads(
                json.loads(script[2].split("if (")[0].strip()[:-1])["SettingsData"]
            )["MapItems"]
            logger.info(f"[{len(locations)}] {loc_url}")
            for _ in locations:
                addr = _["LocationAddress"].split(",")
                page_url = locator_domain + _["DirectUrl"]
                yield SgRecord(
                    page_url=page_url,
                    location_name=_["Title"],
                    street_address=" ".join(addr[:-2]),
                    city=addr[-2].strip(),
                    state=addr[-1].strip().split(" ")[0].strip(),
                    zip_postal=addr[-1].strip().split(" ")[-1].strip(),
                    country_code="US",
                    phone=_["LocationPhoneNum"],
                    latitude=_["Latitude"],
                    longitude=_["Longitude"],
                    locator_domain=locator_domain,
                    raw_address=_["LocationAddress"],
                )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
