from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgpostal import parse_address_intl
import re


def _valid(val):
    return (
        val.replace("–", "-")
        .encode("unicode-escape")
        .decode("utf8")
        .replace("\\xa0", "")
        .replace("\\xa0\\xa", "")
        .replace("\\xae", "")
        .replace("\\u2022", "")
    )


def fetch_data():
    with SgRequests() as session:
        locator_domain = "https://www.mickeyshorr.com/"
        base_url = "https://www.mickeyshorr.com/AllShops"
        res = session.get(base_url)
        locations = bs(res.text, "lxml").select("ul.shops-list li.shops-item")
        for location in locations:
            try:
                addr = parse_address_intl(
                    [
                        _
                        for _ in location.select_one(
                            "div.short-description a"
                        ).stripped_strings
                    ][-1]
                )
                phone = (
                    location.find("a", href=re.compile("tel"))
                    .text.split(":")[-1]
                    .strip()
                )
                page_url = (
                    "https://www.mickeyshorr.com"
                    + location.select_one("h2.shop-name a")["href"]
                )
                coord = location.select_one("input.shop-coordinates")
                yield SgRecord(
                    page_url=page_url,
                    store_number=location["data-shopid"],
                    location_name=coord["data-shop-title"],
                    street_address=addr.street_address_1,
                    city=addr.city,
                    state=addr.state,
                    zip_postal=addr.postcode,
                    country_code="US",
                    latitude=coord["data-latitude"],
                    longitude=coord["data-longitude"],
                    phone=phone,
                    locator_domain=locator_domain,
                )
            except:
                import pdb

                pdb.set_trace()


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
