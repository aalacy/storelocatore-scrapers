from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgpostal import parse_address_intl
import calendar
import time
import re

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def _valid(val):
    return val.replace("&#39;", "'").replace("NOW OPEN:", "")


def _hour(hh):
    return hh.replace(
        '<span style="font-family: inherit; font-weight: inherit;">', ""
    ).replace("</span>", "")


def fetch_data():
    locator_domain = "https://madisonsresto.com/"
    page_url = "https://madisonsresto.com/locations/"
    base_url = f"https://madisonsresto.com/wp-content/plugins/superstorefinder-wp/ssf-wp-xml.php?wpml_lang=en&t={calendar.timegm(time.gmtime())}"
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        locations = soup.select("locator store item")
        for _ in locations:
            addr = parse_address_intl(_.address.text)
            hours = []
            if _.operatinghours:
                hours = list(bs(_hour(_.operatinghours.text), "lxml").stripped_strings)
            if _.operatingHours:
                hours = list(bs(_hour(_.operatingHours.text), "lxml").stripped_strings)
            hours_of_operation = "; ".join(hours)
            location_name = _valid(_.location.text).split(":")[-1]
            if re.search(r"CLOSED TEMPORARILY", _.location.text, re.IGNORECASE):
                hours_of_operation = "CLOSED TEMPORARILY"
            elif _.location.text.startswith("CLOSED"):
                continue
            street_address = addr.street_address_1
            if "Auotroute Chomedey" in _.address.text:
                street_address = _.address.text.split("(13)")[0] + "(13)"
            yield SgRecord(
                page_url=page_url,
                store_number=_.sortord.text,
                location_name=location_name,
                street_address=street_address,
                city=addr.city,
                state=addr.state,
                zip_postal=addr.postcode,
                country_code="Canada",
                phone=_.telephone.text.replace("Tel:", ""),
                latitude=_.latitude.text,
                longitude=_.longitude.text,
                locator_domain=locator_domain,
                hours_of_operation=hours_of_operation,
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
