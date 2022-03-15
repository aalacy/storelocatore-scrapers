from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import SgLogSetup
from bs4 import BeautifulSoup as bs

logger = SgLogSetup().get_logger("")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.wenzels.co.uk"
base_url = "https://www.wenzels.co.uk/our-stores/"


def fetch_data():
    with SgRequests() as session:
        states = bs(session.get(base_url, headers=_headers).text, "lxml").select(
            "div#accordion-stores div.accordion"
        )
        for state in states:
            locations = state.select("li a")
            for link in locations:
                page_url = link["href"]
                logger.info(page_url)
                res = session.get(page_url, headers=_headers).text
                sp1 = bs(res, "lxml")
                raw_address = sp1.select_one("div.offset-md-2 p").text.strip()
                addr = raw_address.split(",")
                if addr[-1].strip() == "UK":
                    del addr[-1]
                _cc = addr[-1].split()
                street_address = ", ".join(addr[:-1])
                city = " ".join(_cc[:-2])
                if not city and len(addr) > 2:
                    city = addr[-2]
                    street_address = ", ".join(addr[:-2])
                hours = [
                    ": ".join(hh.stripped_strings)
                    for hh in sp1.select("table.table-opening-hours tr")
                ]
                latitude = res.split("lat_center =")[1].split(";")[0].strip()
                longitude = res.split("lng_center =")[1].split(";")[0].strip()
                phone = ""
                if sp1.find("i", {"class", "fa-phone"}):
                    phone = (
                        sp1.find("i", {"class", "fa-phone"}).find_parent().text.strip()
                    )
                yield SgRecord(
                    page_url=page_url,
                    location_name=sp1.h1.text.strip(),
                    street_address=street_address,
                    city=city,
                    state=state.select_one("div.accordion-title").text.strip(),
                    zip_postal=" ".join(_cc[-2:]),
                    latitude=latitude,
                    longitude=longitude,
                    country_code="UK",
                    phone=phone,
                    locator_domain=locator_domain,
                    hours_of_operation="; ".join(hours).replace("\\u2013", "-"),
                    raw_address=raw_address,
                )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
