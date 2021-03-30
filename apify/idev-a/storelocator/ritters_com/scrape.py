from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgpostal import parse_address_intl
import dirtyjson


locator_domain = "https://www.ritters.com/"


def fetch_data():
    with SgRequests() as session:
        res = session.get("https://www.ritters.com/locations.php")
        stores = dirtyjson.loads(
            res.text.split('map").gmap3(')[1]
            .split("marker:")[1]
            .split("draggable: false")[0]
            .replace("\t", "")
            .replace("\n", "")
            .strip()[:-10]
            .strip()[:-1]
            + "}"
        )["values"]
        for store in stores:
            latitude = store["latLng"][0]
            longitude = store["latLng"][1]
            location_name = bs(store["data"], "lxml").select_one("strong").string
            page_url = (
                locator_domain + bs(store["data"], "lxml").select_one("a")["href"]
            )
            res = session.get(page_url)

            detail = bs(res.text, "lxml").select_one("div.location-info-text")
            detail = detail.select("p")
            detail = [x for x in detail if "preferred delivery" not in x.text]
            address = detail[0].contents[1:-1]
            address = [x for x in address if x.string is not None]
            address = ", ".join(address)
            address = parse_address_intl(address)
            zip = address.postcode
            state = address.state
            city = address.city
            street_address = (
                (
                    address.street_address_1
                    if address.street_address_1 is not None
                    else ""
                )
                + " "
                + (
                    address.street_address_2
                    if address.street_address_2 is not None
                    else ""
                )
            )
            phone = detail[1].string or "<MISSING>"
            try:
                hours_of_operation = detail[2].text
            except:
                hours_of_operation = "<MISSING>"
            record = SgRecord(
                page_url=page_url,
                location_name=location_name,
                street_address=street_address.strip(),
                city=city,
                zip_postal=zip,
                state=state,
                phone=phone.replace("Phone: ", ""),
                locator_domain=locator_domain,
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=hours_of_operation.replace("\r\n", " ")
                .replace("\n", " ")
                .split("Call us")[0],
            )
            yield record


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
