from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import SgLogSetup
import dirtyjson as json
import re

logger = SgLogSetup().get_logger("mcdonalds")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.mcdonalds.si"
base_url = "https://www.mcdonalds.si/restavracije/"
hr_obj = {
    "1": "Monday",
    "2": "Tuesday",
    "3": "Wednesday",
    "4": "Thursday",
    "5": "Friday",
    "6": "Saturday",
    "7": "Sunday",
}


def fetch_data():
    with SgRequests() as session:
        locations = json.loads(
            session.get(base_url, headers=_headers)
            .text.split("const docs =")[1]
            .split(".map")[0]
            .strip()
        )
        for _ in locations:
            page_url = _["slugs"]
            logger.info(page_url)
            sp1 = bs(session.get(page_url, headers=_headers).text, "lxml")
            phone = ""
            if sp1.find("a", href=re.compile(r"tel:")):
                phone = sp1.find("a", href=re.compile(r"tel:")).text.strip()
            raw_address = _["address"]
            addr = raw_address.split(",")
            if "Slovenia" in addr[-1]:
                del addr[-1]

            hours = []
            for hh in _["hours_shop"]:
                hours.append(
                    f"{hr_obj[str(hh['day'])]}: {hh['time_from']} - {hh['time_to']}"
                )

            if hours and "Sunday" not in " ".join(hours):
                hours.append("Sunday: Closed")

            city = _["city"]
            if not city:
                city = " ".join(addr[-1].strip().split()[1:])
            street_address = _["street"]
            if not street_address:
                street_address = ", ".join(addr[:-1])
            yield SgRecord(
                page_url=page_url,
                store_number=_["id"],
                location_name=_["title"],
                street_address=street_address,
                city=city,
                zip_postal=addr[-1].strip().split()[0],
                latitude=_["marker"]["position"]["lat"],
                longitude=_["marker"]["position"]["lng"],
                country_code="Slovenia",
                phone=phone,
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
                raw_address=raw_address,
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
