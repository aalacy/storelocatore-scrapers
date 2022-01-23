from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgpostal.sgpostal import parse_address_intl
import demjson
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("")

locator_domain = "https://www.ritters.com/"
base_url = "https://www.ritters.com/locations.php"

_headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36",
}


def fetch_data():
    with SgRequests(verify_ssl=False) as session:
        res = session.get(base_url, headers=_headers)
        stores = demjson.decode(
            res.text.split("values:")[1]
            .split("draggable: false")[0]
            .replace("\t", "")
            .replace("\n", "")
            .strip()[:-10]
            .strip()[:-1]
        )
        for store in stores:
            location_name = bs(store["data"], "lxml").select_one("strong").string
            page_url = (
                locator_domain + bs(store["data"], "lxml").select_one("a")["href"]
            )
            logger.info(page_url)
            detail = bs(
                session.get(page_url, headers=_headers).text, "lxml"
            ).select_one("div.location-info-text")
            detail = detail.select("p")
            detail = [x for x in detail if "preferred delivery" not in x.text]
            if "Coming Soon" == detail[0].text.strip():
                continue
            address = detail[0].contents[1:-1]
            address = [x for x in address if x.string is not None]
            raw_address = ", ".join(address)
            addr = parse_address_intl(raw_address)
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += " " + addr.street_address_2
            try:
                hours_of_operation = detail[2].text
                if (
                    "closed until" in hours_of_operation.lower()
                    or "closed for" in hours_of_operation.lower()
                ):
                    hours_of_operation = "Temporarily_closed"
            except:
                hours_of_operation = ""
            try:
                latitude = store["latLng"][0]
                longitude = store["latLng"][1]
            except:
                latitude = ""
                longitude = ""
            yield SgRecord(
                page_url=page_url,
                store_number=page_url.split("id=")[1],
                location_name=location_name,
                street_address=street_address.strip(),
                zip_postal=addr.postcode,
                state=addr.state,
                city=addr.city,
                phone=detail[1].text.replace("Phone: ", "").strip(),
                locator_domain=locator_domain,
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=hours_of_operation.replace("\r\n", " ")
                .replace("\n", " ")
                .replace("Store Hours:", "")
                .split("Call us")[0]
                .split("Except")[0],
                raw_address=raw_address,
            )


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.PAGE_URL,
                }
            )
        )
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
