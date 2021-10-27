from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import SgLogSetup
from datetime import datetime

logger = SgLogSetup().get_logger("kuwait")


locator_domain = "https://www.kuwait.kfc.me"
base_url = "https://www.kuwait.kfc.me/WebAPI/v2/Location/Cities"


_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def _p(val):
    return (
        val.replace("(", "")
        .replace(")", "")
        .replace("+", "")
        .replace("-", "")
        .replace(".", " ")
        .replace("to", "")
        .replace(" ", "")
        .strip()
        .isdigit()
    )


def fetch_data():
    with SgRequests() as session:
        cities = session.get(base_url, headers=_headers).json()["data"]["CityList"]
        date = datetime.now().strftime("%m/%d/%Y")
        for city in cities:
            url = f"https://www.kuwait.kfc.me/WebAPI/Location/Search?Channel=W&deliverymode=S&date={date}&city={city['CityId']}&ignoreslot=1&filters=deliverymode-date-slot-city&Format=html&CurrentEvent=Location_Search"
            locations = bs(
                session.get(url, headers=_headers)
                .text.strip()[1:-1]
                .strip()
                .replace("\\r\\n", "")
                .replace("\\t", "")
                .replace('\\"', '"'),
                "lxml",
            ).select("div.store-list ul li")
            logger.info(f"{city['CityName']} {len(locations)}")
            for _ in locations:
                phone = _.select("span")[-1].text.strip()
                if not _p(phone):
                    phone = ""
                yield SgRecord(
                    location_name=_.select_one("div.store-name").text.strip(),
                    street_address=_.select_one("div.store-address").text.strip(),
                    city=city["CityName"],
                    country_code="Kuwait",
                    phone=phone,
                    locator_domain=locator_domain,
                    hours_of_operation=" ".join(
                        list(_.select_one("div.store-time").stripped_strings)[:-1]
                    ),
                )


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.PHONE,
                    SgRecord.Headers.STREET_ADDRESS,
                    SgRecord.Headers.CITY,
                }
            )
        )
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
