from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgpostal.sgpostal import parse_address_intl
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "http://www.sneakypetes.com/"
base_url = "http://www.sneakypetes.com/wp-json/wpgmza/v1/features/base64eJyrVkrLzClJLVKyUqqOUcpNLIjPTIlRsopRMopR0gEJFGeUFni6FAPFomOBAsmlxSX5uW6ZqTkpELFapVoABXgWuw"


def fetch_data():
    with SgRequests() as session:
        store_list = session.get(base_url, headers=_headers).json()
        for store in store_list["markers"]:
            logger.info(store["link"])
            addr = parse_address_intl(store["address"])
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += " " + addr.street_address_2
            res = session.get(store["link"], headers=_headers)
            phone = hours_of_operation = ""
            if res.status_code == 200:
                soup = bs(res.text, "lxml")
                raw_address = phone = (
                    soup.select_one("h1.single-title small").text.split("•")[0].strip()
                )
                phone = (
                    soup.select_one("h1.single-title small")
                    .text.split("P:")[-1]
                    .split("or")[0]
                    .split("•")[0]
                    .strip()
                )
                addr = parse_address_intl(raw_address)
                street_address = addr.street_address_1
                if addr.street_address_2:
                    street_address += " " + addr.street_address_2
                hours_of_operation = soup.select_one("div.location-top h3").text
                hours_of_operation = (
                    "<MISSING>"
                    if "Contact" in hours_of_operation
                    else hours_of_operation.replace("Hours of Operations", "").replace(
                        "•", ""
                    )
                )
            yield SgRecord(
                page_url=store["link"],
                store_number=store["id"],
                location_name=store["title"],
                street_address=street_address,
                city=addr.city,
                state=addr.state,
                zip_postal=addr.postcode,
                country_code="US",
                latitude=store["lat"],
                longitude=store["lng"],
                phone=phone,
                locator_domain=locator_domain,
                hours_of_operation=hours_of_operation,
                raw_address=store["address"],
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
