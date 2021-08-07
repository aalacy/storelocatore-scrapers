import time
import ssl

from bs4 import BeautifulSoup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import SgRecordID
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

driver = SgChrome().driver()


def fetch_data(sgw: SgWriter):
    driver.get("https://www.zipsdrivein.com/locations/")
    stores = driver.find_element_by_class_name("sub-menu").find_elements_by_tag_name(
        "a"
    )
    hrefs = []
    for store in stores:
        hrefs.append(store.get_attribute("href"))

    for url in hrefs:

        driver.get(url)
        time.sleep(5)
        soup = BeautifulSoup(driver.page_source, "html.parser")
        divs = soup.find_all("div", {"class": "wpgmaps_blist_row wpgmaps_odd"})
        divs += soup.find_all("div", {"class": "wpgmaps_blist_row wpgmaps_even"})

        while True:
            if driver.find_elements_by_css_selector('[title="Next page"]') == []:
                break

            driver.find_element_by_css_selector('[title="Next page"]').click()
            time.sleep(5)
            soup = BeautifulSoup(driver.page_source, "html.parser")
            divs += soup.find_all("div", {"class": "wpgmaps_blist_row wpgmaps_odd"})
            divs += soup.find_all("div", {"class": "wpgmaps_blist_row wpgmaps_even"})

        for div in divs:
            latlng = div.get("data-latlng").split(", ")
            lat = latlng[0]
            long = latlng[1]
            city = "<MISSING>"
            add = div.get("data-address")
            addr = add.replace(", USA", "")
            addr = addr.split(",")
            state = addr[-1].strip()
            del addr[-1]
            if ", USA" in add:
                city = addr[-1]
                del addr[-1]
            street = (", ".join(addr)).replace("  ", " ")
            loc = (
                div.find("div", {"class": "wpgmza-basic-list-item wpgmza_div_title"})
                .text.split(")")[1]
                .strip()
            )
            if city == "<MISSING>":
                city = loc

            phone = "<MISSING>"
            if loc.count("-") > 2:
                phone = loc.split(" - ")[1].strip()
                loc = loc.split(" - ")[0].strip()

            sgw.write_row(
                SgRecord(
                    locator_domain="https://www.zipsdrivein.com/",
                    page_url=url,
                    location_name=loc,
                    street_address=street,
                    city=city.strip(),
                    state=state,
                    zip_postal="<MISSING>",
                    country_code="US",
                    store_number="<MISSING>",
                    phone=phone,
                    location_type="<MISSING>",
                    latitude=lat,
                    longitude=long,
                    hours_of_operation="<MISSING>",
                )
            )

    driver.close()


with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))) as writer:
    fetch_data(writer)
