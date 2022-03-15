from bs4 import BeautifulSoup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests

from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("wagamama_com")


def fetch_data(sgw: SgWriter):

    base_link = "https://www.wagamama.com/restaurants"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    locator_domain = "wagamama.com"

    main_links = []
    final_links = []

    main_items = base.find_all(class_="Directory-listLink")
    for main_item in main_items:
        main_link = "https://www.wagamama.com/restaurants/" + main_item["href"]
        count = main_item["data-count"].replace("(", "").replace(")", "").strip()
        if count == "1":
            final_links.append(main_link)
        else:
            main_links.append(main_link)

    for main_link in main_links:
        req = session.get(main_link, headers=headers)
        base = BeautifulSoup(req.text, "lxml")

        next_items = base.find_all(class_="Teaser-titleLink")
        for next_item in next_items:
            next_link = "https://www.wagamama.com/restaurants/" + next_item["href"]
            final_links.append(next_link)

    for link in final_links:
        logger.info(link)
        req = session.get(link, headers=headers)
        base = BeautifulSoup(req.text, "lxml")

        if "coming soon" in base.find(class_="Core").text:
            continue

        location_name = "Wagamama " + base.h1.text.title()
        street_address = base.find(itemprop="streetAddress")["content"]
        city = base.find(class_="c-address-city").text.strip()
        state = "<MISSING>"
        zip_code = base.find(itemprop="postalCode").text.strip()
        country_code = "GB"
        store_number = "<MISSING>"
        try:
            phone = base.find(itemprop="telephone").text.strip()
        except:
            continue
        if not phone:
            phone = "<MISSING>"
        latitude = base.find(itemprop="latitude")["content"]
        longitude = base.find(itemprop="longitude")["content"]
        location_type = ""
        feats = base.find_all(itemprop="amenityFeature")
        for feat in feats:
            location_type = location_type + ", " + feat.text
        location_type = location_type[2:].strip()
        if not location_type:
            location_type = "<MISSING>"
        hours_of_operation = " ".join(
            list(base.find(class_="c-hours-details").tbody.stripped_strings)
        )

        try:
            if "back soon" in base.find(class_="Core-eventTitle").text.lower():
                hours_of_operation = "Temporarily Closed"
            if "near" in base.find(class_="Core-eventTitle").text.lower():
                continue
        except:
            pass

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
