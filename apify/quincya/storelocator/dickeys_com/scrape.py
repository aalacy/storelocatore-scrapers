import re

from bs4 import BeautifulSoup

from sglogging import SgLogSetup

from sgrequests import SgRequests

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

logger = SgLogSetup().get_logger("dickeys_com")


def fetch_data(sgw: SgWriter):

    base_link = "https://www.dickeys.com/locations"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    locator_domain = "https://www.dickeys.com/"

    all_links = []

    main_items = base.find(
        "div", {"class": re.compile(r"style__StyledSearchByState.+")}
    ).find_all("a")
    for main_item in main_items:
        main_link = locator_domain + main_item["href"]
        logger.info(main_link)

        main_status = False
        for i in range(10):
            req = session.get(main_link, headers=headers)
            base = BeautifulSoup(req.text, "lxml")
            next_items = base.find_all(class_="state-city__item")
            if len(next_items) > 0:
                main_status = True
                break

        if not main_status:
            logger.info("Unexpected error here!")
            raise

        for next_item in next_items:
            next_link = (locator_domain + next_item.a["href"]).replace("//loc", "/loc")

            next_status = False
            for i in range(10):
                try:
                    next_req = session.get(next_link, headers=headers)
                except:
                    break
                next_base = BeautifulSoup(next_req.text, "lxml")
                final_items = next_base.find_all(class_="store-info__inner")
                if len(final_items) > 0:
                    next_status = True
                    break

            if not next_status:
                continue

            for item in final_items:
                final_link = (locator_domain + item.a["href"]).replace("//loc", "/loc")
                if final_link in all_links:
                    continue
                all_links.append(final_link)

                location_name = item.a.text.strip()
                raw_address = item.find(
                    "p", {"class": re.compile(r".+store-info__address")}
                ).text.split(",")
                street_address = (
                    (" ".join(raw_address[:-2]).strip())
                    .replace("Fairfield OH", "")
                    .replace("  ", " ")
                    .strip()
                )
                city = raw_address[-2].strip()
                state = raw_address[-1].strip()[:-6].strip()
                zip_code = raw_address[-1][-6:].strip()
                country_code = "US"
                store_number = "<MISSING>"
                location_type = "<MISSING>"
                phone = item.find(
                    "p", {"class": re.compile(r".+store-info__telephone")}
                ).a.text.strip()
                if not phone:
                    phone = "<MISSING>"

                try:
                    hours_of_operation = " ".join(
                        list(
                            item.find(class_="store-info__time")
                            .find_previous("div")
                            .stripped_strings
                        )
                    )
                except:
                    hours_of_operation = "<MISSING>"
                latitude = "<INACCESSIBLE>"
                longitude = "<INACCESSIBLE>"

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
