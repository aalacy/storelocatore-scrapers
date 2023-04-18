from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sglogging import SgLogSetup
from bs4 import BeautifulSoup as bs
from sgscrape.sgpostal import parse_address_intl

logger = SgLogSetup().get_logger("cevalogistics")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

header1 = {
    "Accept": "application/json, text/plain, */*",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "en-US,en;q=0.9,ko;q=0.8",
    "Host": "www.cevalogistics.com",
    "Referer": "https://www.cevalogistics.com/en/contact-us",
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    locator_domain = "https://www.cevalogistics.com/"
    base_url = "https://www.cevalogistics.com/en/contact-us"
    with SgRequests() as session:
        countries = bs(session.get(base_url, headers=_headers).text, "lxml").select(
            'select#region optgroup[label="Country"] option'
        )
        for country in countries:
            url = f"https://www.cevalogistics.com/api/en/contact/locations/{country['value']}?activities=ALL&services=ALL"
            locations = session.get(url, headers=header1).json()["Locations"]
            logger.info(f"[{country['value']}] {len(locations)} found")
            for _ in locations:
                street_address = _["address_1"] and _["address_1"].strip() or ""
                if _["address_2"] and _["address_2"].strip():
                    street_address += " " + _["address_2"]
                state = ""
                zip_postal = _["zip_code"] or ""
                if zip_postal and zip_postal.lower() == "n/a" or zip_postal == "0000":
                    zip_postal = ""
                if zip_postal:
                    _zip = parse_address_intl(f"{zip_postal} {_['country']}")
                    zip_postal = _zip.postcode
                    state = _zip.state
                if street_address:
                    addr = parse_address_intl(street_address)
                    _ss = street_address.lower()
                    if (
                        "ghaha" in _ss
                        or "india" in _ss
                        or "china" in _ss
                        or "france" in _ss
                        or "myanmar" in _ss
                        or "UAE" in _ss
                        or "United Arab Emirates" in _ss
                    ):
                        street_address = addr.street_address_1
                        if addr.street_address_2:
                            street_address += " " + addr.street_address_2
                    if zip_postal and zip_postal in street_address:
                        street_address = addr.street_address_1
                        if addr.street_address_2:
                            street_address += " " + addr.street_address_2
                        state = addr.state

                yield SgRecord(
                    page_url=base_url,
                    store_number=_["nid"],
                    location_name=_["title"],
                    street_address=street_address,
                    city=_["city"],
                    state=state,
                    zip_postal=zip_postal,
                    latitude=_["latitude"],
                    longitude=_["longitude"],
                    country_code=country["value"],
                    phone=_["phone"],
                    locator_domain=locator_domain,
                )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
