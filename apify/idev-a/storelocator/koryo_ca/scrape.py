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
    locator_domain = "https://koryo.ca/"
    page_url = "https://koryo.ca/stores/"
    base_url = f"https://koryo.ca/wp-content/plugins/superstorefinder-wp/ssf-wp-xml.php?wpml_lang=en&t={calendar.timegm(time.gmtime())}"
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
            temp = []
            for hh in hours:
                temp.append(hh.split("/")[-1])
            location_name = _.location.text
            location_type = ""
            if "FERMÉ / CLOSED" in location_name:
                location_name = location_name.split("-")[-1]
                location_type = "Closed"
            yield SgRecord(
                page_url=page_url,
                store_number=_.sortord.text,
                location_name=_valid(location_name),
                street_address=addr.street_address_1,
                city=addr.city,
                state=addr.state,
                zip_postal=addr.postcode,
                country_code="Canada",
                phone=_.telephone.text,
                latitude=_.latitude.text,
                longitude=_.longitude.text,
                locator_domain=locator_domain,
                location_type=location_type,
                hours_of_operation="; ".join(temp),
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
