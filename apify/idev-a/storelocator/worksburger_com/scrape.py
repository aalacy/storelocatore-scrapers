from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgpostal import parse_address_intl
import calendar
import time

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def _valid(val):
    return val.replace("&#39;", "'")


def fetch_data():
    locator_domain = "https://worksburger.com/"
    page_url = "https://worksburger.com/locations/"
    base_url = f"https://worksburger.com/wp-content/plugins/superstorefinder-wp/ssf-wp-xml.php?wpml_lang=&t={calendar.timegm(time.gmtime())}"
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        locations = soup.select("locator store item")
        for _ in locations:
            addr = parse_address_intl(_.address.text)
            hours = []
            if _.operatinghours:
                hours = list(bs(_.operatinghours.text, "lxml").stripped_strings)
            if _.operatingHours:
                hours = list(bs(_.operatingHours.text, "lxml").stripped_strings)
            yield SgRecord(
                page_url=page_url,
                store_number=_.sortord.text,
                location_name=_valid(_.location.text),
                street_address=addr.street_address_1,
                city=addr.city,
                state=addr.state,
                zip_postal=addr.postcode,
                country_code="Canada",
                phone=_.telephone.text,
                latitude=_.latitude.text,
                longitude=_.longitude.text,
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
