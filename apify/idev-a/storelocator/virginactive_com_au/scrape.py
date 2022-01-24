from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import SgLogSetup
import dirtyjson as json

logger = SgLogSetup().get_logger("virginactive")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.virginactive.com.au"
base_url = "https://www.virginactive.com.au/home/our_clubs.aspx"


def fetch_data():
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        locations = soup.select("div.container div.ClubContainer")
        for _ in locations:
            raw_address = _.address.text.strip()
            addr = raw_address.split(",")
            page_url = locator_domain + _.select_one("div.textColumn a")["href"]
            logger.info(page_url)
            res = session.get(page_url, headers=_headers).text
            sp1 = bs(res, "lxml")
            coord = json.loads(res.split("position:")[1].split("map")[0].strip()[:-1])
            hours = []
            for hh in sp1.select("div.openingHoursContainer > div"):
                hr = ": ".join(hh.stripped_strings)
                if "Holiday" in hr:
                    break
                hours.append(hr)
            yield SgRecord(
                page_url=page_url,
                location_name=_.h2.text.strip(),
                street_address=" ".join(addr[:-1]),
                city=" ".join(addr[-1].strip().split()[:-2]),
                state=addr[-1].strip().split()[-2],
                zip_postal=addr[-1].strip().split()[-1],
                country_code="Australia",
                phone=_.select_one("a.vaPhoneNumber").text.strip(),
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
