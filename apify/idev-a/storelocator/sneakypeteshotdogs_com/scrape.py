from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgpostal import parse_address_intl
from bs4 import BeautifulSoup as bs


def fetch_data():
    with SgRequests() as session:
        base_url = "http://www.sneakypetes.com/wp-json/wpgmza/v1/features/base64eJyrVkrLzClJLVKyUqqOUcpNLIjPTIlRsopRMopR0gEJFGeUFni6FAPFomOBAsmlxSX5uW6ZqTkpELFapVoABXgWuw"
        locator_domain = "http://www.sneakypetes.com/"
        store_list = session.get(base_url).json()
        for store in store_list["markers"]:
            soup = bs(session.get(store["link"]).text, "lxml")
            addr = parse_address_intl(
                soup.select_one('h1[itemprop="headline"] small')
                .text.split("•")[0]
                .strip()
            )
            phone = soup.select_one("h1.single-title small").text.split("P: ").pop()
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
                street_address=addr.street_address_1,
                city=addr.city,
                state=addr.state,
                zip_postal=addr.postcode,
                country_code="US",
                latitude=store["lat"],
                longitude=store["lng"],
                phone=phone,
                locator_domain=locator_domain,
                hours_of_operation=hours_of_operation,
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
