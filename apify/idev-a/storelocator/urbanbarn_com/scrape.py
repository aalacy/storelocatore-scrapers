from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("urbanbarn")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.urbanbarn.com"
base_url = "https://www.urbanbarn.com/en/all-stores/"


def fetch_data():
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        locations = soup.select("div.stores-detail-block-wrapper")
        for _ in locations:
            page_url = locator_domain + _.select("div.slr-link-block a")[-1]["href"]
            logger.info(page_url)
            sp1 = bs(session.get(page_url, headers=_headers).text, "lxml")
            hours = [
                " ".join(hh.stripped_strings)
                for hh in sp1.select("div.sld-store-hours table tr")
            ]
            addr = list(_.select_one("div.slr-detail-container").stripped_strings)
            coord = _.form.select_one('input[name="daddr"]')["value"].split(",")
            phone = _.select_one("div.sld-tel").text.strip()
            if phone == "-":
                phone = ""
            yield SgRecord(
                page_url=page_url,
                store_number=page_url.split("id=")[-1],
                location_name=_.select_one("p.ms-font--montserrat-bold")
                .text.split("•")[-1]
                .strip(),
                street_address=" ".join(addr[:-1]),
                city=addr[-1].split(",")[0].strip(),
                state=addr[-1].split(",")[1].strip().split()[0].strip(),
                zip_postal=" ".join(addr[-1].split(",")[1].strip().split()[1:]),
                country_code="CA",
                phone=phone,
                latitude=coord[0],
                longitude=coord[1],
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
