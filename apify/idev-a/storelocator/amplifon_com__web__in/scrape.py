from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import SgLogSetup
from bs4 import BeautifulSoup as bs
from datetime import datetime
from dateutil.relativedelta import relativedelta

logger = SgLogSetup().get_logger("")


headers = {
    "accept": " application/json, text/javascript, */*; q=0.01",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "en-US,en;q=0.9",
    "channel": "AmplifonUUXApac",
    "content-type": "application/json",
    "country": "in",
    "origin": "https://www.amplifon.com",
    "referer": "https://www.amplifon.com/",
}

locator_domain = "https://www.amplifon.com"

urls = {
    "in": {
        "locator": "https://www.amplifon.com/in/store-locator/results",
        "base": "https://www.amplifon.com/in/store-locator/hearing-aids-jaipur/{}",
        "latitude": "23.022505",
        "longitude": "72.5713621",
    },
    "hu": {
        "locator": "https://www.amplifon.com/hu/hallaskozpont-kereso/search-results.html",
        "base": "https://www.amplifon.com/hu/hallaskozpont-kereso/hallokeszulekek-baranya-megye/{}",
        "latitude": "46.0727345",
        "longitude": "18.232266",
    },
    "pl": {
        "locator": "https://www.amplifon.com/pl/nasze-gabinety/search-results",
        "base": "https://www.amplifon.com/pl/nasze-gabinety/aparaty-sluchowe-podkarpackie/{}",
        "latitude": "50.0411867",
        "longitude": "21.9991196",
    },
}

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
        for country, cc in urls.items():
            bb = bs(session.get(cc["locator"]).text, "lxml").select_one(
                "div.store-locator-results"
            )
            headers["x-api-key"] = bb["data-client-api-key"]
            headers["channel"] = bb["data-channel"]
            payload = {
                "countryCode": bb["data-country-code"],
                "latitude": cc["latitude"],
                "longitude": cc["longitude"],
                "locale": bb["data-locale"],
                "limit": 1500,
                "radius": 10000,
                "type": "",
            }
            locations = session.post(
                bb["data-getstore-service-url"], headers=headers, json=payload
            ).json()
            logger.info(f"[{country}] {len(locations)}")
            for _ in locations:
                page_url = cc["base"].format(
                    f"{_['shortName'].lower()}-{_['type'].lower()}{_['shopNumber']}"
                )
                hours = []
                logger.info(f"[{country}] {_['shopNumber']}")
                start_date = datetime.now().strftime("%Y-%m-%d")
                end_date = (datetime.now() + relativedelta(months=1)).strftime(
                    "%Y-%m-%d"
                )
                payload1 = {
                    "countryCode": bb["data-country-code"],
                    "type": _["type"],
                    "shopNumber": _["shopNumber"],
                    "locale": bb["data-locale"],
                    "startDate": start_date,
                    "endDate": end_date,
                }
                hr = session.post(
                    bb["data-getopeninghours-service-url"],
                    headers=headers,
                    json=payload1,
                ).json()
                for hh in hr["openingTimes"]:
                    hours.append(
                        f"{hr_obj[str(hh['dayOfWeek'])]}: {hh['startTime']} - {hh['endTime']}"
                    )
                yield SgRecord(
                    page_url=page_url,
                    store_number=_["shopNumber"],
                    location_name=_["shopName"],
                    street_address=_["address"],
                    city=_["city"],
                    state=_.get("province"),
                    zip_postal=_.get("cap"),
                    latitude=_["latitude"],
                    longitude=_["longitude"],
                    country_code=country,
                    phone=_.get("phoneNumber1"),
                    locator_domain=locator_domain,
                    hours_of_operation="; ".join(hours),
                )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
