from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("tomford")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.tomford.com"
base_url = "https://www.tomford.com/stores"
json_url = "https://www.tomford.com/on/demandware.store/Sites-tomford-Site/default/Stores-GetJSON"


def fetch_data():
    with SgRequests() as session:
        countries = bs(session.get(base_url, headers=_headers).text, "lxml").select(
            "select.country option"
        )
        for country in countries:
            url = f"{json_url}?dwfrm_storelocator_address_country={country['value']}"
            if country["value"] == "US":
                url += "&dwfrm_storelocator_postalCode=NEW+YORK"
            session.clear_cookies()
            locations = session.get(url, headers=_headers).json()
            logger.info(f"{url} {len(locations)}")
            for _ in locations:
                if "TOM FORD" not in _["lines"]:
                    continue
                street_address = (
                    _["address"].lower().replace(country["value"].lower(), "")
                )
                if _["city"]:
                    street_address = street_address.replace(_["city"].lower(), "")
                if _["state"]:
                    street_address = street_address.replace(_["state"].lower(), "")
                hours = []
                if _["hours"]:
                    days = [
                        hh.text.strip() for hh in bs(_["hours"], "lxml").select("dt")
                    ]
                    times = [
                        hh.text.strip() for hh in bs(_["hours"], "lxml").select("dd")
                    ]
                    for x in range(len(days)):
                        hours.append(f"{days[x]}: {times[x]}")
                yield SgRecord(
                    page_url="",
                    store_number=_["id"],
                    location_name=_["name"],
                    street_address=street_address,
                    city=_["city"],
                    state=_["state"],
                    zip_postal=_["zip"],
                    latitude=_["latLng"][0],
                    longitude=_["latLng"][1],
                    country_code=country["value"],
                    phone=_["phone"],
                    locator_domain=locator_domain,
                    hours_of_operation="; ".join(hours),
                )


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.STORE_NUMBER,
                    SgRecord.Headers.STREET_ADDRESS,
                    SgRecord.Headers.PHONE,
                    SgRecord.Headers.LATITUDE,
                    SgRecord.Headers.LONGITUDE,
                    SgRecord.Headers.CITY,
                    SgRecord.Headers.LOCATION_NAME,
                }
            )
        )
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
