from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("americanmattress")

locator_domain = "https://www.americanmattress.com/"
base_url = "https://cdn.shopify.com/s/files/1/0027/4474/6102/t/42/assets/sca.storelocatordata.json?v=1610452736&formattedAddress=&boundsNorthEast=&boundsSouthWest="

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    with SgRequests() as http:
        store_list = http.get(base_url, headers=_headers).json()
        for store in store_list:
            page_url = store["web"] if "web" in store.keys() else ""
            hours_of_operation = (
                store["schedule"]
                .replace("<br>", "")
                .replace("\r", " ")
                .replace("<br>", "")
                .replace("–", "-")
                if "schedule" in store.keys()
                else ""
            )
            if not hours_of_operation and page_url:
                logger.info(page_url)
                res = http.get(page_url)
                if res.status_code == 200:
                    soup = bs(res.text, "lxml")
                    try:
                        hours_of_operation = (
                            soup.select_one("div.bounceInLeft div.rte")
                            .text.split("Hours")
                            .pop()
                            .replace("\n", " ")
                            .replace("–", "-")
                            .strip()
                        )
                    except:
                        pass

            yield SgRecord(
                page_url=page_url,
                store_number=store["id"],
                location_name=store["name"],
                street_address=store["address"],
                city=store["city"],
                state=store.get("state"),
                zip_postal=store["postal"],
                country_code=store.get("country") or "USA",
                phone=store.get("phone"),
                latitude=store["lat"],
                longitude=store["lng"],
                locator_domain=locator_domain,
                hours_of_operation=hours_of_operation,
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
