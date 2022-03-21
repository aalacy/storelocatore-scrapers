from bs4 import BeautifulSoup

from sgrequests import SgRequests

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    base_links = [
        "https://www.tradewindsmarkets.com/locations/",
        "https://www.tradewindsmarkets.com/energy-north-group-owned-locations/",
    ]

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()

    for base_link in base_links:
        req = session.get(base_link, headers=headers)
        base = BeautifulSoup(req.text, "lxml")

        items = base.find(class_="locations-list").find_all("li")

        for item in items:

            locator_domain = "https://www.tradewindsmarkets.com"
            location_name = item.h2.text
            raw_address = (
                item.find(class_="location-address")
                .text.replace("Street Ellsworth", "Street, Ellsworth")
                .split(",")
            )
            street_address = raw_address[0].strip()
            city = raw_address[1].strip()
            state = raw_address[2].split()[0]
            try:
                zip_code = raw_address[2].split()[1]
            except:
                zip_code = ""
            country_code = "US"
            store_number = "<MISSING>"
            phone = item.find(class_="location-phone").text.strip()
            location_type = "Family-Owned"
            if "group-owned" in base_link:
                location_type = "Energy North Group"

            link = item.a["href"]
            req = session.get(link, headers=headers)
            base = BeautifulSoup(req.text, "lxml")

            latitude = ""
            longitude = ""

            try:
                hours_of_operation = " ".join(
                    list(
                        base.find(
                            "table", attrs={"class": "hours-list"}
                        ).stripped_strings
                    )
                )
            except:
                hours_of_operation = ""

            sgw.write_row(
                SgRecord(
                    locator_domain=locator_domain,
                    page_url=link,
                    location_name=location_name,
                    street_address=street_address,
                    city=city,
                    state=state,
                    zip_postal=zip_code,
                    country_code=country_code,
                    store_number=store_number,
                    phone=phone,
                    location_type=location_type,
                    latitude=latitude,
                    longitude=longitude,
                    hours_of_operation=hours_of_operation,
                )
            )


with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
    fetch_data(writer)
