from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgpostal import parse_address_intl
import dirtyjson


locator_domain = "https://www.sunstonefit.com"


def fetch_data():
    with SgRequests() as session:
        res = session.get("https://www.sunstonefit.com/studios")
        stores = dirtyjson.loads(
            res.text.split("var locations = ")[1]
            .split("var infowindow")[0]
            .replace("\n", "")
            .strip()[:-1]
        )
        for store in stores:
            detail = bs(res.text, "lxml").select("#LiveAccordionWrapper5349 > div")[
                store["accordion"] - 1
            ]
            page_url = locator_domain + detail.select_one("a")["href"]
            location_name = store["title"]
            address = store["html"].split("</h5>").pop().replace("<br>", ", ")
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
            phone = " ".join(detail.select_one("span.phone").string.split(" ")[:-1])
            latitude = store["lat"]
            longitude = store["lon"]
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
