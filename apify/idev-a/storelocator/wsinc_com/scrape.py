from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
from sgscrape.sgpostal import parse_address_intl

logger = SgLogSetup().get_logger("wsinc")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    locator_domain = "https://www.wsinc.com"
    base_url = "https://www.wsinc.com/wp-json/wpgmza/v1/features/base64eJyrVkrLzClJLVKyUqqOUcpNLIjPTIlRsopRMolR0gEJFGeUFni6FAPFomOBAsmlxSX5uW6ZqTkpELFapVoABc4WvQ"
    with SgRequests() as session:
        links = session.get(base_url, headers=_headers).json()["markers"]
        logger.info(f"{len(links)} found")
        for link in links:
            page_url = locator_domain + link["link"]
            addr = parse_address_intl(link["address"])
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += " " + addr.street_address_2
            phone = ""
            for pp in link["custom_field_data"]:
                if pp["name"].lower() == "phone":
                    phone = pp["value"]
                    break
            location_name = f"{link['title']}"
            if link["category"]:
                location_name += f",{link['category']}"
            yield SgRecord(
                page_url=page_url,
                store_number=link["id"],
                location_name=location_name,
                street_address=street_address,
                city=addr.city,
                state=addr.state,
                zip_postal=addr.postcode,
                country_code="US",
                phone=phone,
                locator_domain=locator_domain,
                latitude=link["lat"],
                longitude=link["lng"],
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
