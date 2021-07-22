import ssl

from bs4 import BeautifulSoup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgselenium import SgChrome

try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification


def fetch_data(sgw: SgWriter):

    base_link = "https://www.mrtire.com/store-search/?redirect=%2F"

    driver = SgChrome().driver()
    driver.get(base_link)

    base = BeautifulSoup(driver.page_source, "lxml")

    items = base.find_all(class_="results-store-container")
    locator_domain = "mrtire.com"

    for item in items:
        location_name = (
            item.find(class_="results-store-header").text.strip()
            + " "
            + item.p.text.strip()
        )
        location_name = location_name[location_name.find(" ") + 1 :].strip()

        street_address = item.find(class_="results-store-info").div.text.strip()
        city_line = (
            item.find(class_="results-store-info")
            .find_all("div")[1]
            .text.strip()
            .split(",")
        )
        city = city_line[0].strip()
        state = city_line[-1].strip().split()[0].strip()
        try:
            zip_code = city_line[-1].strip().split()[1].strip()
        except:
            zip_code = "<MISSING>"

        country_code = "US"
        store_number = item.p.text.split("#")[1]

        location_type = "<MISSING>"
        phone = item.find(class_="results-store-phone").text.strip()
        hours_of_operation = " ".join(
            list(item.find(class_="results-store-hours-list").stripped_strings)
        )

        geo = (
            item.find(class_="results-directions-link")["href"]
            .split("=")[-1]
            .split(",")
        )
        latitude = geo[0]
        longitude = geo[1]
        link = "https://www.mrtire.com/appointment?storeid=" + store_number
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
    driver.close()


with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
    fetch_data(writer)
