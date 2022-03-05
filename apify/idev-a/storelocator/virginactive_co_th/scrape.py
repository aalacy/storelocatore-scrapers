from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import SgLogSetup
import dirtyjson as json
from sgpostal.sgpostal import parse_address_intl

logger = SgLogSetup().get_logger("virginactive")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.virginactive.co.th"
base_url = "https://www.virginactive.co.th/home/our_clubs.aspx"


def fetch_data():
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        locations = soup.select("div.ClubContainer")
        for _ in locations:
            raw_address = (
                " ".join(_.address.stripped_strings)
                .replace("\n", "")
                .replace("\r", " ")
            )
            addr = parse_address_intl(raw_address + ", Thailand")
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += " " + addr.street_address_2
            page_url = locator_domain + _.select_one("div.buttonRow a")["href"]
            logger.info(page_url)
            res = session.get(page_url, headers=_headers).text
            coord = json.loads(
                res.split("center:")[1].split("scrollwheel")[0].strip()[:-1]
            )
            sp1 = bs(res, "lxml")
            hours = []
            for hh in sp1.select("div.openingHoursContainer > div")[:-1]:
                hr = " ".join(hh.stripped_strings)
                if "Holiday" in hr:
                    break
                hours.append(hr)
            phone = ""
            if _.select_one("a.vaPhoneNumber"):
                phone = _.select_one("a.vaPhoneNumber").text.strip()
            yield SgRecord(
                page_url=page_url,
                location_name=_.h2.text.strip(),
                street_address=street_address,
                city=addr.city,
                state=addr.state,
                zip_postal=addr.postcode,
                country_code="Thailand",
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
