import re

from bs4 import BeautifulSoup

from sgrequests import SgRequests

from sgpostal.sgpostal import parse_address_intl

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("shakeshack.com")


def fetch_data(sgw: SgWriter):

    base_link = "https://shakeshack.com/locations"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"
    HEADERS = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=HEADERS)
    base = BeautifulSoup(req.text, "lxml")

    locator_domain = "https://shakeshack.com"

    items = base.find_all(class_="geolocation-location")

    for item in items:
        location_name = item.find(class_="locations-map--pin--title").text.strip()
        latitude = item["data-lat"]
        longitude = item["data-lng"]

        link = locator_domain + item.a["href"]
        req = session.get(link, headers=HEADERS)

        try:
            base = BeautifulSoup(req.text, "lxml")
        except:
            logger.info("Retrying: " + link)
            session = SgRequests()
            req = session.get(link, headers=HEADERS)
            base = BeautifulSoup(req.text, "lxml")

        final_link = locator_domain + req.url.path
        if "coming-soon" in final_link:
            continue
        logger.info(final_link)

        raw_address = ", ".join(list(base.article.h3.find_next("div").stripped_strings))
        addr = parse_address_intl(raw_address)

        street_address = ""
        streets = base.article.find_all(
            "div", {"class": re.compile(r"field field--name-field-address-line-.")}
        )
        for street in streets:
            street_address = (street_address + " " + street.text).strip()
        city = addr.city
        state = addr.state
        zip_code = addr.postcode
        country_code = addr.country

        try:
            phone = base.article.find_all("a", {"href": re.compile(r"tel:")})[0].text
        except:
            phone = ""

        if phone:
            street_address = street_address.replace(phone, "")

        street_address = (
            street_address.split("Between")[0]
            .split("Inside")[0]
            .split("On the")[0]
            .split("Corner of")[0]
            .split("Located")[0]
            .split("One block")[0]
            .split("Outside")[0]
            .split("Intersection")[0]
            .split("At the")[0]
            .strip()
        )

        if not city:
            city = base.find(id="location-hero--location").text.split(",")[0]

        if city == "Kyoto":
            country_code = "Japan"

        if not country_code:
            if zip_code:
                if len(zip_code) == 5 and state:
                    country_code = "US"
                else:
                    country_code = (
                        base.find(id="location-hero--location")
                        .text.split(",")[-1]
                        .strip()
                    )
            else:
                country_code = (
                    base.find(id="location-hero--location").text.split(",")[-1].strip()
                )

        if zip_code:
            street_address = street_address.replace(zip_code, "").strip()

        if phone:
            country_code = country_code.replace(phone, "").strip()
            if city in phone:
                city = (
                    base.find(id="location-hero--location").text.split(",")[0].strip()
                )

        try:
            if zip_code in phone:
                zip_code = ""
        except:
            pass

        if "New York" in city:
            country_code = "US"

        if ", WC2E 8RD" in street_address:
            street_address = street_address.replace(", WC2E 8RD", "")
            zip_code = "WC2E 8RD"

        location_type = ""
        store_number = item.a["href"].split("/")[-1]

        try:
            hours_of_operation = " ".join(
                list(base.find("h3", string="Hours").find_next("div").stripped_strings)
            )
        except:
            hours_of_operation = ""

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
