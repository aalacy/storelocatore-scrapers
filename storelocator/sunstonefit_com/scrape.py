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
            detail = bs(res.text, "lxml").select(
                "div#LiveAccordionWrapper5349 div.row"
            )[store["accordion"] - 2]
            page_url = locator_domain + detail.select_one("a")["href"]
            address = store["html"].split("</h5>").pop().replace("<br>", ", ")
            address = parse_address_intl(address)
            street_address = (
                address.street_address_1
                + " "
                + (
                    address.street_address_2
                    if address.street_address_2 is not None
                    else ""
                )
            )
            phone = ""
            if detail.select_one("span.phone"):
                phone = " ".join(detail.select_one("span.phone").text.split(" ")[:-1])
            hours_of_operation = ""
            if "[Location Closed]" in detail.select_one('span[itemprop="name"]').text:
                hours_of_operation = "Closed"
            yield SgRecord(
                page_url=page_url,
                location_name=store["title"],
                street_address=street_address,
                city=address.city,
                zip_postal=address.postcode,
                state=address.state,
                phone=phone,
                locator_domain=locator_domain,
                latitude=store["lat"],
                longitude=store["lon"],
                country_code="US",
                hours_of_operation=hours_of_operation,
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
