from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgpostal import parse_address_intl

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    locator_domain = "https://myfoodgiant.com/"
    page_url = "https://myfoodgiant.com/find-your-store/"
    base_url = "https://myfoodgiant.com/wp-json/wpgmza/v1/markers/base64eJyrVkrLzClJLVKyUqqOUcpNLIjPTIlRsopRMoxR0gEJFGeUgsSKgYLRsbVKtQCV7hBN"
    with SgRequests() as session:
        locations = session.get(base_url, headers=_headers).json()
        for _ in locations:
            addr = parse_address_intl(_["address"])
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += " " + addr.street_address_2
            yield SgRecord(
                page_url=page_url,
                store_number=_["id"],
                location_name=_["title"],
                street_address=street_address,
                city=addr.city,
                state=addr.state,
                zip_postal=addr.postcode,
                latitude=_["lat"],
                longitude=_["lng"],
                country_code="US",
                locator_domain=locator_domain,
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
