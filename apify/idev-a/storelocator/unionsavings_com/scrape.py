from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
import json


def fetch_data():
    with SgRequests() as session:
        locator_domain = "https://www.unionsavings.com/"
        base_url = "https://www.unionsavings.com/locations/"
        r = session.get(base_url)
        soup = bs(r.text, "lxml")
        locations = soup.select("div#locations-wrapper div.item")
        for _location in locations:
            location = json.loads(_location["data-info"])
            soup1 = bs(session.get(location["permalink"]).text, "lxml")
            phone = ""
            if _location.select_one('a[title="Phone"]'):
                phone = _location.select_one('a[title="Phone"]').text
            hours = list(soup1.select_one("div.column").stripped_strings)
            _hours = []
            if hours:
                _hours = hours[1:][::-1]

            yield SgRecord(
                page_url=location["permalink"],
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
                hours_of_operation="; ".join(_hours),
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
