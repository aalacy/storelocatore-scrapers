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

locator_domain = "https://www.calendarclub.co.uk"
base_url = "https://em1.calendarclub.co.uk/StoreLocator.json?v=456137"
days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


def fetch_data():
    with SgRequests(verify_ssl=False) as session:
        locations = session.get(base_url, headers=_headers).json()
        for _ in locations:
            slug = (
                _["name"].replace(",", "").replace(" ", "-").replace(":", "")
                + f'-{_["storeid"]}'
            )
            page_url = "https://www.calendarclub.co.uk/our-stores/" + slug.lower()
            logger.info(page_url)
            sp1 = bs(session.get(page_url, headers=_headers).text, "lxml")
            phone = ""
            if sp1.select_one("div.storepage__opening.center h2"):
                phone = sp1.select_one("div.storepage__opening.center h2").text.strip()

            hours = []
            for day in days:
                day = day.lower()
                if _.get(day):
                    hours.append(f"{day}: {_[day]}")
            yield SgRecord(
                page_url=page_url,
                store_number=_["storeid"],
                location_name=_["name"],
                street_address=_["address"],
                city=_["city"],
                state=_["state"],
                zip_postal=_["postcode"],
                latitude=_["lat"],
                longitude=_["lng"],
                country_code=_["country"],
                phone=phone,
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
                raw_address=sp1.select_one("div#map")["data-address"],
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
