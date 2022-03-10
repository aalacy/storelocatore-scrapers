from bs4 import BeautifulSoup

from sglogging import SgLogSetup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests

logger = SgLogSetup().get_logger("fendi.com")


def fetch_data(sgw: SgWriter):

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"
    headers = {"User-Agent": user_agent}

    base_link = "https://www.fendi.com/us-en/store-locator/directory"

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    locator_domain = "fendi.com"

    country_links = []
    final_links = []

    countries = base.find_all(class_="Directory-listLink")

    for country in countries:
        country_link = country["href"]
        count = country["data-count"].replace("(", "").replace(")", "").strip()
        if count == "1":
            final_links.append(country_link)
        else:
            country_links.append(country_link)

    for country_link in country_links:
        logger.info(country_link)
        req = session.get(country_link, headers=headers)
        base = BeautifulSoup(req.text, "lxml")

        final_items = base.find_all(class_="Teaser-titleLink")
        for final_item in final_items:
            final_link = final_item["href"]
            final_links.append(final_link)

    logger.info("Processing " + str(len(final_links)) + " links ..")
    for final_link in final_links:
        req = session.get(final_link, headers=headers)
        base = BeautifulSoup(req.text, "lxml")
        location_name = base.find(id="location-name").text.strip()
        raw_address = base.find(itemprop="streetAddress")["content"].replace(
            "Bejing", "Beijing"
        )
        raw_low = raw_address.lower()
        if "shop " in raw_low:
            loc = raw_low.find("shop")
            street_address = (
                raw_address[:loc] + " " + raw_address[raw_address.find(" ", loc + 6) :]
            ).strip()
        else:
            street_address = raw_address.split(", Florentia")[0].strip()
        city = base.find(class_="Address-field Address-city").text.strip()
        if ", " + city in street_address:
            street_address = street_address.split(", " + city)[0].strip()
        street_address = street_address.replace("   ", " ")
        try:
            state = base.find(itemprop="addressRegion").text.strip()
        except:
            state = ""
        try:
            zip_code = base.find(itemprop="postalCode").text.strip()
        except:
            zip_code = ""

        try:
            country_code = base.find(itemprop="addressCountry").text.strip()
        except:
            country_code = final_link.split("locator/")[1].split("/")[0].title()

        try:
            phone = base.find(id="phone-main").text.strip()
            if not phone:
                phone = ""
        except:
            phone = ""
        store_number = ""
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
                raw_address=raw_address,
            )
        )


with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
    fetch_data(writer)
