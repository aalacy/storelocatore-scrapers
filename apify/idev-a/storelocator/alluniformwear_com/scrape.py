from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from bs4 import BeautifulSoup as bs

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.alluniformwear.com"
base_url = "https://viewer.blipstar.com/searchdbnew?uid=3066804&lat=34.04302978515625&lng=-118.25227355957031&type=all"

days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


def fetch_data():
    with SgRequests() as session:
        locations = session.get(base_url, headers=_headers).json()[1:]
        for _ in locations:
            hours = []
            for day in days:
                if _.get(day.lower()):
                    hours.append(f"{day}: {_[day.lower()]}")
            info = bs(_["a"], "lxml")
            yield SgRecord(
                page_url=_["w"],
                store_number=_["bpid"],
                location_name=_["n"],
                street_address=_["ad"].split(",")[0].strip(),
                city=info.select_one(".storecity").text.strip(),
                state=_["s"],
                zip_postal=_.get("pc"),
                country_code="US",
                phone=_["p"],
                latitude=_["lat"],
                longitude=_["lng"],
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
                raw_address=_["ad"],
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
