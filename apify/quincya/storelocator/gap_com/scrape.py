import re

from bs4 import BeautifulSoup

from sglogging import SgLogSetup

from sgrequests import SgRequests

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

logger = SgLogSetup().get_logger("gap_com")


def fetch_data(sgw: SgWriter):
    base_link = "https://www.gap.com/stores"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    main_links = []
    final_links = []

    locator_domain = "https://www.gap.com"

    main_items = base.find(id="browse-content").find_all(class_="ga-link")
    for main_item in main_items:
        main_link = locator_domain + main_item["href"]
        main_links.append(main_link)

    for main_link in main_links:
        logger.info(main_link)
        req = session.get(main_link, headers=headers)
        base = BeautifulSoup(req.text, "lxml")

        final_items = base.find(class_="map-list").find_all(class_="ga-link")
        for final_item in final_items:
            final_link = locator_domain + final_item["href"]
            final_links.append(final_link)

    total_links = len(final_links)
    logger.info("Processing %s cities .." % (total_links))
    for i, final_link in enumerate(final_links):
        final_req = session.get(final_link, headers=headers)
        base = BeautifulSoup(final_req.text, "lxml")

        items = base.find_all(class_="map-list-item")

        for item in items:
            street_address = item.find(class_="address").div.text.strip()
            city_line = item.find(class_="address").find_all("div")[1].text.split(",")
            city = city_line[0].strip()
            state = city_line[-1].strip().split()[0].strip()
            zip_code = city_line[-1].strip().split()[1].strip()
            country_code = "US"
            location_type = item.find(class_="store-type").text.strip()
            if "," in location_type:
                location_name = "Gap"
            else:
                location_name = location_type
            phone = item.find(class_="phone ga-link").text.strip()

            map_str = item.find(class_="directions ga-link")["href"]
            geo = re.findall(r"[0-9]{2}\.[0-9]+,-[0-9]{2,3}\.[0-9]+", map_str)[0].split(
                ","
            )
            latitude = geo[0]
            longitude = geo[1]

            link = locator_domain + item.find(class_="view-store ga-link")["href"]

            store_number = link.split("-")[-1].split(".")[0]

            req = session.get(link, headers=headers)
            page_base = BeautifulSoup(req.text, "lxml")

            try:
                hours_of_operation = " ".join(
                    list(page_base.find(class_="hours").stripped_strings)
                )
            except:
                hours_of_operation = "<INACCESSIBLE>"
            if not hours_of_operation:
                hours_of_operation = "<MISSING>"

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


with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
    fetch_data(writer)
