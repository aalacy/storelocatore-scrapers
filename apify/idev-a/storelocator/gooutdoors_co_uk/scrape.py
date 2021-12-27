from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import SgLogSetup
import dirtyjson as json

logger = SgLogSetup().get_logger("gooutdoors")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


locator_domain = "https://www.gooutdoors.co.uk"
base_url = "https://www.gooutdoors.co.uk/google/store-locator"
days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


def fetch_data():
    with SgRequests() as session:
        payload = {
            "postcode": "",
            "submit": "Find stores",
            "radius": "500",
            "ac_store_limit": "300",
            "current_view": "list",
            "fascias[]": "GO",
        }
        store_list = bs(
            session.post(
                "https://www.gooutdoors.co.uk/google/store-locator",
                headers=_headers,
                data=payload,
            ).text,
            "lxml",
        ).select("ul.store-list li")
        logger.info(f"{len(store_list)} store_list")
        for store in store_list:
            page_url = (
                locator_domain
                + store.select("div.store-details div.more_info p")[-1].select_one("a")[
                    "href"
                ]
            )
            logger.info(page_url)
            res = session.get(page_url, headers=_headers)
            hours = []
            street_address = city = zip_postal = latitude = longitude = ""
            location_name = store.select_one("div.store-details h3").text.strip()
            phone = store.select_one("a.tel_link").text.strip()
            if phone == "-":
                phone = ""
            if res.status_code == 200:
                sp1 = bs(res.text, "lxml")
                _ = json.loads(sp1.find("script", type="application/ld+json").string)
                addr = _["address"]
                coord = _["hasmap"].split("/@")[1].split(",")
                street_address = addr["streetAddress"]
                city = addr["addressLocality"]
                zip_postal = addr["postalCode"]
                latitude = coord[0]
                longitude = coord[1]
                hours = _["openingHours"]
            else:
                page_url = base_url
                addr = [aa.text.strip() for aa in store.select("p.storeAddress")]
                street_address = addr[0]
                zip_postal = addr[1]
                hours = list(
                    store.select("div.storefinder_opening table tr")[1].stripped_strings
                )

            yield SgRecord(
                page_url=page_url,
                store_number=store["data-id"],
                location_name=location_name,
                street_address=street_address,
                city=city,
                zip_postal=zip_postal,
                country_code="UK",
                phone=phone,
                latitude=latitude,
                longitude=longitude,
                hours_of_operation="; ".join(hours),
                locator_domain=locator_domain,
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
