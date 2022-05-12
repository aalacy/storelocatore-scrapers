import json

from bs4 import BeautifulSoup

from sglogging import SgLogSetup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests

logger = SgLogSetup().get_logger("champschicken.com")


def fetch_data(sgw: SgWriter):
    base_link = "https://champschicken.com/locations-list/"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    final_links = []
    locator_domain = "https://champschicken.com"

    states = base.find(class_="sb-directory-list sb-directory-list-states").find_all(
        "a"
    )
    for i in states:
        state_link = locator_domain + i["href"]
        logger.info(state_link)

        req = session.get(state_link, headers=headers)
        base = BeautifulSoup(req.text, "lxml")

        cities = base.find(
            class_="sb-directory-list sb-directory-list-cities"
        ).find_all("a")
        for city in cities:
            if "http" not in city["href"]:
                city_link = locator_domain + city["href"]
            else:
                city_link = city["href"]
            if "/locations/" in city_link:
                final_links.append(city_link)
            elif "/locations-list/" in city_link:
                next_req = session.get(city_link, headers=headers)
                next_base = BeautifulSoup(next_req.text, "lxml")

                next_locs = next_base.find(
                    class_="sb-directory-list sb-directory-list-sites"
                ).find_all("a")

                for loc in next_locs:
                    if "http" not in loc["href"]:
                        fin_link = locator_domain + loc["href"]
                    else:
                        fin_link = loc["href"]
                    if "/locations/" in fin_link:
                        final_links.append(fin_link)

    logger.info("Processing " + str(len(final_links)) + " links ..")
    for final_link in final_links:
        if "location-name-city-state" in final_link:
            continue
        req = session.get(final_link, headers=headers)
        base = BeautifulSoup(req.text, "lxml")
        location_name = base.h1.text.strip()

        script = base.find_all("script", attrs={"type": "application/ld+json"})[
            -1
        ].contents[0]
        store = json.loads(script)

        street_address = store["address"]["streetAddress"]
        city = store["address"]["addressLocality"]
        state = store["address"]["addressRegion"]
        zip_code = store["address"]["postalCode"]
        country_code = store["address"]["addressCountry"]["name"]

        phone = base.find(class_="lp-phone").text.strip()
        store_number = ""
        location_type = ""

        try:
            hours_of_operation = " ".join(
                list(base.find(class_="hours-box").stripped_strings)
            )
        except:
            hours_of_operation = ""

        latitude = store["geo"]["latitude"]
        longitude = store["geo"]["longitude"]

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
