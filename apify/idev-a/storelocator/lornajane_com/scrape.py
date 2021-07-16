from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests.sgrequests import SgRequests
import us
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("lornajane")


_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    with SgRequests() as session:
        for ss in us.states.STATES:
            url = f"https://www.lornajane.com/on/demandware.store/Sites-LJUS-Site/en_US/Stores-FindStores?country=US&state={ss.name}"
            logger.info(url)
            # here you use the requests session to fetch the location from the requests
            locations = bs(session.get(url, headers=_headers).text, "lxml").select(
                "div.results div.store-item"
            )
            for _ in locations:
                addr = list(_.select_one("div.store-address").stripped_strings)
                phone = ""
                if _.select_one("a.storelocator-phone"):
                    phone = _.select_one("a.storelocator-phone").text.strip()
                try:
                    coord = (
                        _.select_one("a.store-map")["href"].split("addr=")[1].split(",")
                    )
                except:
                    coord = ["", ""]
                page_url = _.select_one("div.store-name a")["href"]
                sp1 = bs(session.get(page_url, headers=_headers).text, "lxml")
                hours = list(sp1.select_one("div.store-hours").stripped_strings)
                if hours:
                    hours = hours[1:]
                yield SgRecord(
                    page_url=page_url,
                    street_address=" ".join(addr[:-1]),
                    city=addr[-1].split(",")[0].strip(),
                    state=addr[-1].split(",")[1].strip(),
                    zip_postal=addr[-1].split(",")[2].strip(),
                    store_number=_["data-store-id"],
                    location_name=_["data-store-name"],
                    phone=phone,
                    latitude=coord[0],
                    longitude=coord[1],
                    hours_of_operation="; ".join(hours),
                    raw_address=" ".join(addr),
                )


if __name__ == "__main__":
    with SgWriter(
        deduper=SgRecordDeduper(RecommendedRecordIds.StoreNumberId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
