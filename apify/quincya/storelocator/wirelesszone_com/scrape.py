from bs4 import BeautifulSoup

from sglogging import SgLogSetup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests

logger = SgLogSetup().get_logger("wirelesszone.com")


def fetch_data(sgw: SgWriter):
    base_link = "https://shop.wirelesszone.com/index.html"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    final_links = []
    locator_domain = "https://wirelesszone.com/"

    state_links = []
    states = base.find_all(class_="Directory-listLink")
    for state in states:
        state_link = "https://shop.wirelesszone.com/" + state["href"].replace(
            "/memphis", ""
        )
        count = state["data-count"].replace("(", "").replace(")", "").strip()
        if count == "1":
            final_links.append(state_link)
        else:
            state_links.append(state_link)

    for state_link in state_links:
        req = session.get(state_link, headers=headers)
        base = BeautifulSoup(req.text, "lxml")

        cities = base.find_all(class_="Directory-listLink")
        for city in cities:
            city_link = "https://shop.wirelesszone.com/" + city["href"].replace(
                "../", ""
            )
            count = city["data-count"].replace("(", "").replace(")", "").strip()

            if count == "1":
                final_links.append(city_link)
            else:
                next_req = session.get(city_link, headers=headers)
                next_base = BeautifulSoup(next_req.text, "lxml")

                final_items = next_base.find_all(class_="Teaser-titleLink")
                for final_item in final_items:
                    final_link = (
                        "https://shop.wirelesszone.com/" + final_item["href"]
                    ).replace("../", "")
                    final_links.append(final_link)

    logger.info("Processing " + str(len(final_links)) + " links ..")
    for final_link in final_links:
        req = session.get(final_link, headers=headers)
        base = BeautifulSoup(req.text, "lxml")
        location_name = base.find(id="location-name").text.replace("   ", " ").strip()
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
        city = base.find(class_="c-address-city").text.strip()
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
            )
        )


with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
    fetch_data(writer)
