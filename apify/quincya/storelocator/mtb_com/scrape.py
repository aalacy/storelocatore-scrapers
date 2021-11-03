import re

from bs4 import BeautifulSoup

from sglogging import SgLogSetup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests

logger = SgLogSetup().get_logger("mtb_com")


def fetch_data(sgw: SgWriter):
    base_link = "https://locations.mtb.com/listings.html"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    final_links = []
    locator_domain = "mtb.com"

    state_links = []
    states = base.find_all(class_="Directory-listLink")
    for state in states:
        state_links.append("https://locations.mtb.com/" + state["href"].split("/")[0])

    for state_link in state_links:
        logger.info(state_link)
        req = session.get(state_link, headers=headers)
        base = BeautifulSoup(req.text, "lxml")

        cities = base.find_all(class_="Directory-listLink")
        for city in cities:
            city_link = "https://locations.mtb.com/" + city["href"]
            count = city["data-count"].replace("(", "").replace(")", "").strip()

            if count == "1":
                final_links.append(city_link)
            else:
                next_req = session.get(city_link, headers=headers)
                next_base = BeautifulSoup(next_req.text, "lxml")

                final_items = next_base.find_all(class_="Teaser-titleLink")
                for final_item in final_items:
                    final_link = (
                        "https://locations.mtb.com/" + final_item["href"]
                    ).replace("../", "")
                    final_links.append(final_link)

    logger.info("Processing " + str(len(final_links)) + " links ..")
    for final_link in final_links:
        req = session.get(final_link, headers=headers)
        base = BeautifulSoup(req.text, "lxml")
        location_name = base.find(id="location-name").text.strip()
        street_address = base.find(itemprop="streetAddress")["content"]
        city = base.find(class_="Address-field Address-city").text.strip()
        state = base.find(itemprop="addressRegion").text.strip()
        zip_code = base.find(itemprop="postalCode").text.strip()
        country_code = "US"

        try:
            phone = base.find(id="phone-main").text.strip()
            if not phone:
                phone = ""
        except:
            phone = ""
        store_number = final_link.split("-")[-1].split(".")[0]

        if "13 & 896" not in street_address and "Route" not in street_address:
            if re.search(r"\d", street_address):
                digit = str(re.search(r"\d", street_address))
                start = int(digit.split("(")[1].split(",")[0])
                street_address = street_address[start:]

        try:
            location_type = ", ".join(
                list(base.find(class_="Core-branchServices").stripped_strings)
            )
        except:
            location_type = ""

        try:
            hours_of_operation = (
                " ".join(list(base.find(class_="c-hours-details").stripped_strings))
                .replace("Day of the Week Hours", "")
                .strip()
            )
        except:
            hours_of_operation = ""

        latitude = base.find(itemprop="latitude")["content"]
        longitude = base.find(itemprop="longitude")["content"]

        sgw.write_row(
            SgRecord(
                locator_domain=locator_domain,
                page_url=final_link,
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
