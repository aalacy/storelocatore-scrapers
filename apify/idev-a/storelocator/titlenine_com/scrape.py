from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from urllib.parse import urljoin
from sgscrape.sgpostal import parse_address_intl
import json


def fetch_data():
    with SgRequests() as session:
        locator_domain = "https://www.titlenine.com/"
        base_url = "https://www.titlenine.com/all-stores"
        rr = session.get(base_url)
        soup = bs(rr.text, "lxml")
        locations = json.loads(soup.select_one("div.map-canvas")["data-locations"])
        for location in locations:
            location_name = location["name"]
            soup1 = bs(location["infoWindowHtml"], "lxml")
            block = [_ for _ in soup1.select_one(".store-data").stripped_strings]
            page_url = urljoin(
                "https://www.titlenine.com", soup1.select_one("a.store-info")["href"]
            )
            _address = " ".join([_.strip() for _ in block[0].split("\n") if _.strip()])
            if len(_address.split("/")) > 1:
                _address = _address.split("/")[1]
            addr = parse_address_intl(_address)
            street_address = addr.street_address_1.replace(
                "Hilldale Shopping Center", ""
            )
            city = addr.city.replace("Kerrytown", "").replace(",", "")
            latitude = location["latitude"]
            longitude = location["longitude"]
            hours_of_operation = "; ".join(
                [
                    _
                    for _ in soup1.select_one(
                        "div.store-info-section p"
                    ).stripped_strings
                ]
            )

            yield SgRecord(
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=addr.state,
                zip_postal=addr.postcode,
                country_code="US",
                latitude=latitude,
                longitude=longitude,
                phone=block[1],
                locator_domain=locator_domain,
                hours_of_operation=hours_of_operation,
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
