from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import SgLogSetup
import dirtyjson as json
import re

logger = SgLogSetup().get_logger("virginactive")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.virginactive.com.sg"
base_url = "https://www.virginactive.com.sg/home/our_clubs.aspx"


def fetch_data():
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        locations = soup.select("div.ClubContainer")
        for link in locations:
            page_url = locator_domain + link.select_one("a.vaStyle-Button")["href"]
            logger.info(page_url)
            res = session.get(page_url, headers=_headers).text
            sp1 = bs(res, "lxml")
            raw_address = ", ".join(link.address.stripped_strings)
            addr = raw_address.split("Singapore")
            coord = json.loads(res.split("position:")[1].split("map")[0].strip()[:-1])
            hours = []
            for hh in sp1.select("div.openingHoursContainer div.col-sm-eigth"):
                hr = ": ".join(hh.stripped_strings)
                if "Holiday" in hr:
                    break
                hours.append(hr)
            phone = ""
            if sp1.find("a", href=re.compile(r"tel:")):
                phone = sp1.find("a", href=re.compile(r"tel:")).text.strip()
            if phone == "n/a":
                phone = ""
            yield SgRecord(
                page_url=page_url,
                location_name=sp1.h1.text.strip(),
                street_address=" ".join(addr[0].split(",")[2:])
                .replace(",", "")
                .replace("Marina Bay Sands", "")
                .strip(),
                city="Singapore",
                zip_postal=addr[-1].replace(",", ""),
                country_code="Singapore",
                phone=phone,
                latitude=coord["lat"],
                longitude=coord["lng"],
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
                raw_address=raw_address,
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
