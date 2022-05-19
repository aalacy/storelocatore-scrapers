from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import SgLogSetup
import json

logger = SgLogSetup().get_logger("minisom")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.minisom.pt"
base_url = "https://www.minisom.pt/sitemap.xml"
hr_obj = {
    "1": "Monday",
    "2": "Tuesday",
    "3": "Wednesday",
    "4": "Thursday",
    "5": "Friday",
    "6": "Saturday",
    "7": "Sunday",
}


def fetch_data():
    with SgRequests() as session:
        locations = bs(session.get(base_url, headers=_headers).text, "lxml").select(
            "loc"
        )

        for loc in locations:
            page_url = loc.text
            if "/centros-minisom/" not in page_url:
                continue
            if len(page_url.split("/")) < 6:
                continue
            logger.info(page_url)
            sp1 = bs(session.get(page_url, headers=_headers).text, "lxml")
            ss = json.loads(
                sp1.select_one("main.store-detail-page")["data-analytics-storedetail"]
            )
            raw_address = " ".join(
                sp1.select_one("div.detail-address").stripped_strings
            )
            phone = ""
            if ss["phones"]:
                phone = ss["phones"][0]["phoneNumber"]
            hours = []
            for hh in ss["openingTimes"]:
                hours.append(
                    f"{hr_obj[str(hh['dayOfWeek'])]}: {hh['startTime']} - {hh['endTime']}"
                )

            yield SgRecord(
                page_url=page_url,
                store_number=ss["shopNumber"],
                location_name=ss["shopName"],
                street_address=ss["address"],
                city=ss["city"],
                state=ss["province"],
                zip_postal=ss["cap"],
                country_code="PT",
                phone=phone,
                latitude=ss["latitude"],
                longitude=ss["longitude"],
                locator_domain=locator_domain,
                raw_address=raw_address,
                hours_of_operation="; ".join(hours),
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
