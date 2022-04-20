import json

from bs4 import BeautifulSoup

from sglogging import SgLogSetup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests

logger = SgLogSetup().get_logger("bbqgalore_com")


def fetch_data(sgw: SgWriter):

    base_link = "https://www.bbqgalore.com/stores"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    main_links = []
    main_items = base.find_all(class_="store")
    for main_item in main_items:
        main_link = main_item.a["href"]
        if "http" not in main_link:
            main_link = "https://www.bbqgalore.com" + main_link
        main_links.append([main_link, main_item])

    for i in main_links:
        final_link = i[0]
        logger.info(final_link)
        final_req = session.get(final_link, headers=headers)
        item = BeautifulSoup(final_req.text, "lxml")

        locator_domain = "bbqgalore.com"

        location_name = "Barbeques Galore " + item.find("h2").text.strip().title()

        try:
            raw_address = list(item.find(class_="section__content").p.stripped_strings)
            got_page = True
        except:
            final_link = base_link
            raw_address = list(i[1].p.stripped_strings)
            raw_address[-2] = raw_address[-2].replace("Jose CA", "Jose, CA")
            got_page = False

        if (
            "located in" in raw_address[0].lower()
            or "authorized" in raw_address[0].lower()
        ):
            raw_address.pop(0)

        street_address = raw_address[0].strip()
        city = raw_address[1][: raw_address[1].find(",")].strip()
        state = raw_address[1][raw_address[1].find(",") + 1 : -6].strip()
        zip_code = raw_address[1][-6:].strip()
        country_code = "US"
        store_number = "<MISSING>"

        if got_page:
            location_type = ", ".join(
                list(
                    item.find(class_="section__content")
                    .find_all("p")[-2]
                    .stripped_strings
                )
            )
            phone = item.find(class_="section__content").a.text.strip()
            script = (
                item.find(class_="column main")
                .find("script", attrs={"type": "application/ld+json"})
                .contents[0]
            )
            script = script[script.find("{") : script.rfind("}") + 1].strip()
            geo = json.loads(script)

            hours_of_operation = " ".join(geo["openingHours"])

            latitude = geo["geo"]["latitude"]
            longitude = geo["geo"]["longitude"]

        else:
            phone = raw_address[-1].replace("Tel:", "").strip()

            location_type = ""
            raw_types = i[1].find_all("img")
            for row in raw_types:
                location_type = (
                    location_type
                    + ", "
                    + row["title"]
                    .replace("This store location is a", "")
                    .replace("This store location offers", "")
                    .strip()
                )
            location_type = location_type[1:].title().strip()

            hours_of_operation = ""
            latitude = ""
            longitude = ""

        if "showroom" in location_name.lower():
            location_type = "Showroom"

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
