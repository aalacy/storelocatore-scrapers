from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgpostal import parse_address_intl

_headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36",
}

locator_domain = "http://sukiyaki-restaurants.com"
base_url = "https://sukiyaki-restaurants.com/wp-content/plugins/superstorefinder-wp/ssf-wp-xml.php?wpml_lang=en&t=1633933453974"


def fetch_data():
    with SgRequests() as session:
        locations = bs(
            session.get(base_url, headers=_headers)
            .text.replace("&gt;", ">")
            .replace("&lt;", "<")
            .replace("&amp;", ";")
            .replace(";#44;", ","),
            "lxml",
        ).select("store item")
        for _ in locations:
            raw_address = _.address.text.strip()
            addr = parse_address_intl(raw_address)
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += " " + addr.street_address_2
            yield SgRecord(
                page_url="https://sukiyaki-restaurants.com/locations/",
                store_number=_.storeid.text.strip(),
                location_name=_.location.text.strip(),
                street_address=street_address,
                city=addr.city,
                state=addr.state,
                zip_postal=addr.postcode,
                country_code="CA",
                latitude=_.latitude.text.strip(),
                longitude=_.longitude.text.strip(),
                locator_domain=locator_domain,
                raw_address=raw_address,
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.GeoSpatialId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
