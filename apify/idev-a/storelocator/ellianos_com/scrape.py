from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgpostal import parse_address_intl
from bs4 import BeautifulSoup as bs
import json

locator_domain = "https://www.ellianos.com/"
base_url = "https://www.ellianos.com/locations/"


def _hours(dom_locs, location):
    hours = []
    address = ""
    phone = ""
    for _ in dom_locs:
        if (
            _.select_one("h4.edgtf-team-name")
            and _.select_one("h4.edgtf-team-name").text.strip().lower()
            == location["title"].strip().lower()
        ):
            if _.select_one("div.wpb_text_column"):
                hours = [
                    hour
                    for hour in _.select_one("div.wpb_text_column").stripped_strings
                ]
            try:
                address = _.select_one("div.edgtf-team-description").text
            except:
                pass
            try:
                phone = _.select_one("p.edgtf-team-position").text
            except:
                pass
    return ("; ".join(hours) or "<MISSING>").replace("–", "-"), address, phone


def fetch_data():
    with SgRequests() as session:
        res = session.get(base_url)
        soup = bs(res.text, "lxml")
        dom_locs = soup.select(
            "div.edgtf-section-inner-margin div.wpb_column div.vc_column-inner"
        )
        scripts = [
            _.contents[0]
            for _ in soup.findAll("script")
            if _.contents
            and _.contents[0].startswith("jQuery(document).ready(function($)")
        ]
        locations = json.loads(
            scripts[0].split('$("#map1").maps(')[1].split(').data("wpgmp_maps");')[0]
        )["places"]
        for _ in locations:
            location_type = "<MISSING>"
            title = _["title"]
            if (
                len(_["title"].split("-")) > 1
                and _["title"].split("-")[1].strip() == "COMING SOON!"
            ):
                location_type = "COMING SOON"
                title = _["title"].split("-")[0].strip()
            hours_of_operation, address, phone = _hours(dom_locs, _)
            if not address:
                address = _["address"]
            addr = parse_address_intl(address)
            yield SgRecord(
                store_number=_["id"],
                location_name=title,
                location_type=location_type,
                street_address=addr.street_address_1,
                city=addr.city,
                state=addr.state,
                zip_postal=addr.postcode,
                country_code="US",
                phone=phone,
                latitude=_["location"]["lat"],
                longitude=_["location"]["lng"],
                locator_domain=locator_domain,
                hours_of_operation=hours_of_operation,
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
