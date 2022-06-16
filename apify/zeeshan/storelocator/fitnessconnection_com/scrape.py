from bs4 import BeautifulSoup

from sgrequests import SgRequests

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("fitnessconnection_com")


def fetch_data(sgw: SgWriter):

    base_link = "https://fitnessconnection.com/locations/"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    main_links = []
    main_items = base.find_all(class_="club column small-12 medium-4")
    for main_item in main_items:
        main_link = main_item.a["href"]
        raw_address = str(main_item.find(class_="address-wrapper").a)
        raw_address = raw_address[
            raw_address.find('blank">') + 7 : raw_address.rfind("<")
        ]
        main_links.append([main_link, raw_address])

    total_links = len(main_links)
    for i, raw_link in enumerate(main_links):
        logger.info("Link %s of %s" % (i + 1, total_links))

        link = raw_link[0]
        raw_address = raw_link[1]

        req = session.get(link, headers=headers)
        item = BeautifulSoup(req.text, "lxml")
        logger.info(link)

        locator_domain = "fitnessconnection.com"

        try:
            location_name = (
                item.find("h2")
                .text.replace("-", "- ")
                .replace("– NOW OPEN", "")
                .replace("– Now Open!", "")
                .strip()
            )
        except:
            continue

        if "coming soon" in location_name.lower():
            continue

        street_address = (
            raw_address[: raw_address.find("<")].split("Greenspoint")[0].strip()
        )
        if ", Austin" in street_address:
            street_address = street_address[: street_address.find(", Austin")].strip()
        city = raw_address[raw_address.find(">") + 1 : raw_address.rfind(",")].strip()
        state = raw_address[raw_address.rfind(",") + 1 : raw_address.rfind(" ")].strip()
        zip_code = raw_address[raw_address.rfind(" ") + 1 :].strip()
        if not zip_code:
            zip_code = state.split()[1].strip()
            state = state.split()[0].strip()
        country_code = "US"
        store_number = "<MISSING>"
        location_type = "<MISSING>"

        try:
            phone = item.find(class_="phone").text.strip()
        except:
            phone = "<MISSING>"

        try:
            raw_hours = item.find(class_="primary-hours").text
            hours_of_operation = raw_hours.replace("\n", " ").replace("\r", "").strip()
        except:
            continue

        latitude = "<MISSING>"
        longitude = "<MISSING>"

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
