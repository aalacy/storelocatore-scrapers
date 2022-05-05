from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import SgLogSetup
import dirtyjson as json
import re

logger = SgLogSetup().get_logger("warehousestationery")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.warehousestationery.co.nz"
base_url = "https://www.warehousestationery.co.nz/stores/by-region"


def fetch_data():
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        locations = soup.select("div.store-info")
        for _ in locations:
            page_url = locator_domain + _.select_one("table td a")["href"]
            logger.info(page_url)
            res = session.get(page_url, headers=_headers).text
            ss = json.loads(
                res.split("var storeModel =")[1].split("RefApp.Modules")[0].strip()[:-1]
            )
            street_address = ss["Address1"]
            if ss["Address2"]:
                street_address += " " + ss["Address2"]
            if "closed" in street_address:
                continue

            street_address = (
                street_address.replace("WSL - Located inside the Warehouse", "")
                .replace("WSL - Inside the Warehouse", "")
                .replace("WSL - Located inside The Warehouse", "")
                .strip()
            )
            if street_address.startswith("Warehouse Stationery"):
                street_address = street_address.replace(
                    "Warehouse Stationery", ""
                ).strip()
            if street_address.startswith(","):
                street_address = street_address[1:]
            sp1 = bs(res, "lxml")
            hours = [
                ": ".join(hh.stripped_strings)
                for hh in sp1.select("div.opening-hours tr")
            ]
            if not hours:
                _hr = sp1.find("strong", string=re.compile(r"Regular Trading Hours"))
                if _hr:
                    hours = list(_hr.find_parent().find_next_sibling().stripped_strings)

            raw_address = " ".join(
                sp1.select_one("span.store-street-address").stripped_strings
            )
            yield SgRecord(
                page_url=page_url,
                store_number=ss["ID"],
                location_name=ss["Name"],
                street_address=street_address.strip(),
                city=ss["City"],
                state=ss["StateCode"],
                zip_postal=ss["PostalCode"],
                country_code="NZ",
                phone=ss["Phone"],
                latitude=ss["Latitude"],
                longitude=ss["Longitude"],
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
                raw_address=raw_address,
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
