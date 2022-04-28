from bs4 import BeautifulSoup

from sgrequests import SgRequests

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("drafthouse_com")


def fetch_data(sgw: SgWriter):

    base_link = "https://drafthouse.com/markets"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    main_links = []
    main_items = base.find_all(id="markets-page")
    for main_item in main_items:
        main_link = main_item["href"] + "/theaters"
        main_links.append(main_link)

    for main_link in main_links:
        final_req = session.get(main_link, headers=headers)
        base = BeautifulSoup(final_req.text, "lxml")

        locator_domain = "drafthouse.com"

        items = base.find_all(class_="Footer-links no-bullet")[1].find_all("li")

        for item in items:
            location_name = item.a.text.strip()

            if "Coming Soon" in location_name:
                continue

            final_link = item.a["href"]
            logger.info(location_name)
            raw_address = item.find_all("a")[-2].text.strip().split("\n")
            map_link = item.find_all("a")[-2]["href"]
            phone = item.find_all("a")[-1].text
            if len(raw_address) == 1:
                raw_address = item.find_all("a")[-1].text.strip().split("\n")
                map_link = item.find_all("a")[-1]["href"]
                if "28 Liberty Street" in raw_address[0]:
                    phone = "332-216-3200"
            if "3201 Farnam" in phone:
                phone = "402-884-8999"

            street_address = raw_address[0].strip()
            city = raw_address[1].strip().split(",")[0].strip()
            state = raw_address[1].strip().split(",")[1][:-6].strip()
            zip_code = raw_address[1].strip().split(",")[1][-6:].strip()
            country_code = "US"
            store_number = "<MISSING>"
            location_type = "<MISSING>"

            req = session.get(map_link, headers=headers)
            maps = BeautifulSoup(req.text, "lxml")

            try:
                raw_gps = maps.find("meta", attrs={"itemprop": "image"})["content"]
                latitude = raw_gps[raw_gps.find("=") + 1 : raw_gps.find("%")].strip()
                longitude = raw_gps[raw_gps.find("-") : raw_gps.find("&")].strip()
            except:
                latitude = "<MISSING>"
                longitude = "<MISSING>"

            hours_of_operation = "<MISSING>"

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
