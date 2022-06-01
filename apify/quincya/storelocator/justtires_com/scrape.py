import json

from bs4 import BeautifulSoup

from sglogging import SgLogSetup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests

logger = SgLogSetup().get_logger("justtires.com")


def fetch_data(sgw: SgWriter):
    base_link = "https://www.justtires.com/en-US/service-center-near-me"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    locator_domain = "https://www.justtires.com"

    states = base.find(class_="browse-by-state-wrapper__list").find_all(
        class_="link-chevron"
    )
    for i in states:
        state_link = locator_domain + i["href"]

        logger.info(state_link)
        req = session.get(state_link, headers=headers)
        base = BeautifulSoup(req.text, "lxml")

        cities = base.find(class_="browse-by-state-wrapper__list").find_all(
            class_="link-chevron"
        )
        for y in cities:
            city_link = locator_domain + y["href"]
            if "/PA/Norristown" in city_link:
                city_link = "https://www.justtires.com/en-US/shop?latitude=40.121497&longitude=-75.3399048&street=&city=Norristown&state=PA&zip=&country=us"
            if "/MD/Rockville" in city_link:
                city_link = "https://www.justtires.com/en-US/shop?latitude=39.0839973&longitude=-77.1527578&street=&city=Rockville&state=MD&zip=&country=us"
            req = session.get(city_link, headers=headers)
            city_base = BeautifulSoup(req.text, "lxml")
            items = city_base.find_all(class_="store-results__results__item")
            for item in items:
                final_link = (
                    locator_domain
                    + item.find(class_="nav-my-store__store-title-name")["href"]
                )
                location_name = item.find(
                    class_="nav-my-store__store-title-name"
                ).text.strip()
                try:
                    street_address = item.find(
                        class_="nav-my-store__location--first"
                    ).text.strip()
                except:
                    continue
                city_line = (
                    item.find(class_="nav-my-store__location--second")
                    .text.strip()
                    .split(",")
                )
                city = city_line[0].strip()
                state = city_line[1].split()[0]
                zip_code = city_line[1].split()[1]
                country_code = "US"
                phone = item.find(class_="nav-my-store__telephone").text.strip()
                location_type = ""
                store_number = item["data-store-id"]
                store = json.loads(
                    item.find(class_="nav-my-store__information-area").p[
                        "data-location"
                    ]
                )
                latitude = store["latitude"]
                longitude = store["longitude"]

                req = session.get(final_link, headers=headers)
                page = BeautifulSoup(req.text, "lxml")
                try:
                    hours_of_operation = " ".join(
                        list(
                            page.find(id="my-store-id")
                            .find(class_="nav-my-store__schedule")
                            .stripped_strings
                        )
                    ).replace("(Holiday Hours, May 30 th ) ", "")
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
