from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from urllib.parse import urljoin
import json


def fetch_data():
    with SgRequests() as session:
        locator_domain = "https://www.fatface.com/"
        base_url = "https://www.fatface.com/stores"
        r = session.get(base_url)
        soup = bs(r.text, "lxml")
        links = soup.select("a.b-find-a-store-noresult__letter-store")
        for link in links:
            page_url = urljoin(
                "https://www.fatface.com",
                f"{link['href']}",
            )
            r1 = session.get(page_url)
            soup = bs(r1.text, "lxml")
            location = json.loads(
                soup.select_one("div.js-map-wrapper.b-find-a-store-map")[
                    "data-mapconfig"
                ]
            )
            location_name = location["name"]
            store_number = location["id"]
            street_address = location["address1"]
            city = location["city"].strip()
            zip = location["postalCode"].strip()
            state = location["state"]
            country_code = location["countryCode"]
            phone = location["phone"]
            latitude = location["latitude"]
            longitude = location["longitude"]
            hours_of_operation = "; ".join(
                [
                    _["content"]
                    for _ in soup.select("ul.b-store-locator-details__listing li")
                ]
            )

            yield SgRecord(
                page_url=page_url,
                store_number=store_number,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zip,
                country_code=country_code,
                latitude=latitude,
                longitude=longitude,
                phone=phone,
                locator_domain=locator_domain,
                hours_of_operation=hours_of_operation,
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
