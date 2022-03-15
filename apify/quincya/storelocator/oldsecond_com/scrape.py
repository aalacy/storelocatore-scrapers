import ssl

from bs4 import BeautifulSoup

from sgselenium.sgselenium import SgChrome

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

ssl._create_default_https_context = ssl._create_unverified_context


def fetch_data(sgw: SgWriter):
    base_link = "https://www.oldsecond.com/resources-services/locations/"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"

    driver = SgChrome(user_agent=user_agent).driver()
    driver.get(base_link)

    base = BeautifulSoup(driver.page_source, "lxml")
    driver.close()

    items = base.find_all(class_="location")

    for item in items:
        locator_domain = "oldsecond.com"
        location_name = item.find(class_="loc-title").text.split("     ")[0].strip()
        street_address = list(
            item.find(class_="col-sm-4 col-xs-6 loc-name").stripped_strings
        )[1]
        city = (
            item.find(class_="loc-title")
            .text.split("     ")[0]
            .split("-")[0]
            .split("(")[0]
            .split("Rt")[0]
            .strip()
        )
        map_link = item.find(class_="ext-link")["href"]
        state = map_link.split("/")[-2].split(",")[-1]
        zip_code = ""
        if "60119" in item.find(class_="loc-title").text:
            zip_code = "60119"
        country_code = "US"
        location_type = item.find(class_="loc-services").text
        store_number = item["id"]
        phone = list(item.find(class_="loc-phone").stripped_strings)[1]
        latitude = map_link.split("/@")[-1].split(",")[0]
        longitude = map_link.split("/@")[-1].split(",")[1]
        hours_of_operation = ""
        raw_hours = item.find(id="loc-hours").tbody.find_all("tr")
        for row in raw_hours:
            day = row.td.text
            hours = row.find_all("td")[1].text.replace("*", "")
            hours_of_operation = (hours_of_operation + " " + day + " " + hours).strip()

        sgw.write_row(
            SgRecord(
                locator_domain=locator_domain,
                page_url=base_link,
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
