from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgpostal import parse_address_intl
import json


locator_domain = "https://www.starcycleride.com"


def fetch_data():
    with SgRequests() as session:
        res = session.get("https://www.starcycleride.com/studios/")
        stores = bs(res.text, "lxml").select(
            "div.locations div.location-state div.ng-star-inserted"
        )
        for store in stores:
            if "studios" not in store.select_one("a")["href"]:
                continue
            page_url = locator_domain + store.select_one("a")["href"]
            res = session.get(page_url)
            detail = bs(res.text, "lxml")
            location_name = store.select_one("a p.text-uppercase").text
            address = detail.select_one(".address-map").text.replace("\n", " ")
            address = parse_address_intl(address)
            zip = address.postcode
            state = address.state
            city = address.city
            street_address = (
                address.street_address_1
                + " "
                + (
                    address.street_address_2
                    if address.street_address_2 is not None
                    else ""
                )
            )
            if location_name == "Santa Barbara":
                city = location_name
                state = "CA"
            elif location_name == "Yakima":
                location_name += "(Coming Soon)"
            try:
                phone = store.select_one("a div.card-text > p").string
            except:
                phone = "<MISSING>"
            geo = json.loads(res.text.split(".maps(")[1].split(").data")[0])
            latitude = geo["map_options"]["center_lat"]
            longitude = geo["map_options"]["center_lng"]
            record = SgRecord(
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                zip_postal=zip,
                state=state,
                phone=phone,
                locator_domain=locator_domain,
                latitude=latitude,
                longitude=longitude,
            )
            yield record


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
