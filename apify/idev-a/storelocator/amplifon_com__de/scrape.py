from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from bs4 import BeautifulSoup as bs
import json
from sglogging import SgLogSetup

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

logger = SgLogSetup().get_logger("gaes")

locator_domain = "https://www.amplifon.com/de/"
de_base_url = "https://www.amplifon.com/de/filiale-finden"
fr_base_url = "https://www.amplifon.com/fr/nous-trouver"
it_base_url = "https://www.amplifon.com/it/cerca-centro-amplifon"

de_sitemap = "https://www.amplifon.com/de/sitemap.xml"
it_sitemap = "https://www.amplifon.com/it/sitemap.xml"
fr_sitemap = "https://www.amplifon.com/fr/sitemap.xml"

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
    locations = []
    # Germany
    with SgRequests() as http:
        logger.info(" --- Germany ---")
        urls = bs(http.get(de_sitemap).text, "lxml").select("loc")
        for url in urls:
            _url = url.text
            if "de/filiale-finden/" not in _url or len(_url.split("/")) < 7:
                continue
            locations.append(_url)

        # France
        logger.info(" --- France ---")
        urls = bs(http.get(fr_sitemap).text, "lxml").select("loc")
        for url in urls:
            _url = url.text
            if "fr/nous-trouver/" not in _url or len(_url.split("/")) < 7:
                continue
            locations.append(_url)

        # Italy
        logger.info(" --- Italy ---")
        urls = bs(http.get(it_sitemap).text, "lxml").select("loc")
        for url in urls:
            _url = url.text
            if "it/cerca-centro-amplifon/" not in _url or len(_url.split("/")) < 7:
                continue
            locations.append(_url)

        logger.info(f"{len(locations)} locations")
        for page_url in locations:
            logger.info(page_url)
            country = ""
            if "fr/" in page_url:
                country = "FR"
            elif "de/" in page_url:
                country = "DE"
            elif "it/" in page_url:
                country = "IT"

            res = http.get(page_url, headers=_headers)
            if len(res.url.path.split("/")) < 5:
                continue
            sp1 = bs(res.text, "lxml")
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
                times = f"{hh['startTime']} - {hh['endTime']}"
                if times == "00:00 - 00:00":
                    times = "closed"
                hours.append(f"{hr_obj[str(hh['dayOfWeek'])]}: {times}")

            yield SgRecord(
                page_url=page_url,
                store_number=ss["shopNumber"],
                location_name=ss["shopName"],
                street_address=ss["address"],
                city=ss["city"],
                state=ss["province"],
                zip_postal=ss["cap"],
                country_code=country,
                phone=phone,
                latitude=ss["latitude"],
                longitude=ss["longitude"],
                locator_domain=locator_domain,
                raw_address=raw_address,
                hours_of_operation="; ".join(hours),
            )


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(
            RecommendedRecordIds.PageUrlId, duplicate_streak_failure_factor=100
        )
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
