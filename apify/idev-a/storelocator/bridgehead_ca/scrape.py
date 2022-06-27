from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
import dirtyjson
from sglogging import SgLogSetup
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgpostal import parse_address_intl
import re

logger = SgLogSetup().get_logger("bridgehead")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    locator_domain = "https://www.bridgehead.ca"
    base_url = "https://www.bridgehead.ca/pages/coffeehouses"
    with SgRequests() as session:
        res = session.get(base_url, headers=_headers).text
        locations = dirtyjson.loads(
            res.split("var sites = ")[1]
            .strip()
            .split("function setMarkers")[0]
            .strip()[:-1]
            .replace("\n", "")
            .replace("\t", "")
        )
        logger.info(f"{len(locations)} found")
        for _ in locations:
            mymap = bs(_[4], "lxml")
            block = list(mymap.stripped_strings)
            page_url = locator_domain + mymap.a["href"]
            logger.info(page_url)
            soup1 = bs(session.get(page_url, headers=_headers).text, "lxml")
            _addr = list(soup1.select_one("div.page__content.rte p").stripped_strings)
            raw_address = []
            for aa in _addr:
                if "Ph" in aa or "Hour" in aa:
                    break
                raw_address.append(aa.replace("&nbsp;", " ").replace("\xa0", " "))
            addr = parse_address_intl(" ".join(raw_address))
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += " " + addr.street_address_2

            hours = []
            phone = ""
            for hh in block[:-1][::-1]:
                if hh.startswith("Ph"):
                    phone = hh.split("Ph.")[-1].split("Ph")[-1]
                    break
                hours.append(hh)
            if hours and hours[0].lower() == "closed":
                hours = []
                for hh in (
                    soup1.find_all("", string=re.compile(addr.city))[-1]
                    .find_parent()
                    .find_next_siblings("p")
                ):
                    if not hh.text.replace("\xa0", " ").strip():
                        continue
                    hours += list(hh.stripped_strings)

            if hours and "Hours" in hours[0]:
                del hours[0]
            yield SgRecord(
                page_url=page_url,
                location_name=_[0],
                street_address=street_address,
                city=addr.city,
                state=addr.state,
                zip_postal=addr.postcode,
                country_code="CA",
                latitude=_[1],
                longitude=_[2],
                phone=phone,
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours).replace("\xa0", " "),
                raw_address=" ".join(raw_address),
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
