from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from bs4 import BeautifulSoup as bs
import json
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.torrancememorial.org"
base_url = "https://www.torrancememorial.org/locations/"


def fetch_data():
    with SgRequests(proxy_country="us") as session:
        options = bs(session.get(base_url, headers=_headers).text, "lxml").select(
            "select#VsMasterPage_MainContent_LocationList_TopPaging_InternalDropDownList option"
        )
        for option in options:
            url = locator_domain + option["value"].replace("~", "")
            logger.info(url)
            locations = bs(session.get(url, headers=_headers).text, "lxml").select(
                "div.LocationsList li"
            )
            with SgRequests(proxy_country="us") as http:
                for loc in locations:
                    page_url = locator_domain + loc.a["href"]
                    logger.info(page_url)
                    sp1 = bs(http.get(page_url, headers=_headers).text, "lxml")
                    _ = json.loads(
                        sp1.select_one('script[type="application/ld+json"]').text
                    )
                    addr = _["address"]
                    hours = [
                        " ".join(hh.stripped_strings)
                        for hh in sp1.select("div.Hours div.DaySchedule")
                    ]
                    yield SgRecord(
                        page_url=page_url,
                        location_name=_["name"],
                        street_address=addr["streetAddress"],
                        city=addr["addressLocality"],
                        state=addr["addressRegion"],
                        zip_postal=addr["postalCode"],
                        latitude=_["geo"]["latitude"],
                        longitude=_["geo"]["longitude"],
                        country_code="US",
                        phone=_.get("telephone"),
                        locator_domain=locator_domain,
                        hours_of_operation="; ".join(hours),
                        raw_address=" ".join(
                            loc.select_one("div.adr").stripped_strings
                        ),
                    )


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(
            SgRecordID({SgRecord.Headers.LOCATION_NAME, SgRecord.Headers.RAW_ADDRESS})
        )
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
