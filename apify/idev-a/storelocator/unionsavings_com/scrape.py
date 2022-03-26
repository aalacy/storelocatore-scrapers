from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
import json
from sglogging import SgLogSetup
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
import re

logger = SgLogSetup().get_logger("unionsavings")

locator_domain = "https://www.unionsavings.com/"
base_url = "https://www.unionsavings.com/locations/"
_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        locations = soup.select("div#locations-wrapper div.item")
        for _location in locations:
            location = json.loads(_location["data-info"])
            page_url = location["permalink"]
            logger.info(page_url)
            res = session.get(page_url, headers=_headers)
            phone = ""
            if _location.select_one('a[title="Phone"]'):
                phone = _location.select_one('a[title="Phone"]').text
            hours = []
            if res.status_code == 200:
                soup1 = bs(res.text, "lxml")
                _hr = soup1.find("span", string=re.compile(r"Lobby Hours"))
                if _hr:
                    hours = [
                        ": ".join(hh.stripped_strings)
                        for hh in _hr.find_next_siblings("span")
                    ]
            else:
                page_url = base_url
            yield SgRecord(
                page_url=page_url,
                location_name=location["name"],
                street_address=location["address"],
                city=location["city"],
                state=location["state"],
                zip_postal=location["zip"],
                country_code="US",
                latitude=location["latitude"],
                longitude=location["longitude"],
                phone=phone,
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
            )


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.CITY,
                    SgRecord.Headers.LATITUDE,
                    SgRecord.Headers.LONGITUDE,
                    SgRecord.Headers.PAGE_URL,
                }
            )
        )
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
