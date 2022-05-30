import re
import ssl

from bs4 import BeautifulSoup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests

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
    base_link = "https://www.hy-vee.com/aisles-online/stores"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()

    driver = SgChrome().driver()
    driver.get(base_link)
    base = BeautifulSoup(driver.page_source, "lxml")

    driver.close()

    locator_domain = "hy-vee.com"

    items = base.find_all("div", attrs={"data-testid": "store-card"})

    for item in items:
        link = "https://www.hy-vee.com" + item.a["href"]
        raw_address = list(item.stripped_strings)
        location_name = raw_address[0].strip()
        phone = raw_address[-1]
        if "-" not in phone:
            phone = ""
            street_address = raw_address[1].strip()
            city_line = raw_address[2].strip().split(",")
        else:
            street_address = raw_address[-3].strip()
            city_line = raw_address[-2].strip().split(",")
        city = city_line[0].strip()
        state = city_line[-1].strip().split()[0].strip()
        zip_code = city_line[-1].strip().split()[1].strip()

        store_number = link.split("=")[-1]
        country_code = "US"
        location_type = "<MISSING>"
        latitude = "<MISSING>"
        longitude = "<MISSING>"

        try:
            req = session.get(link, headers=headers)
            base = BeautifulSoup(req.text, "lxml")
            got_page = True
        except:
            link = base_link
            got_page = False

        if got_page:
            location_name = " ".join(list(base.h1.stripped_strings))
            if not phone:
                phone = base.find("a", {"href": re.compile(r"tel.+")}).text.strip()

            try:
                hours_of_operation = (
                    base.find(id="page_content")
                    .find_all("p")[1]
                    .text.replace("\n", " ")
                    .replace("\r", " ")
                    .strip()
                )
                if not hours_of_operation:
                    hours_of_operation = (
                        base.find(class_="storeHours table")
                        .find_all("td")[1]
                        .text.replace("\n", "")
                        .replace("\r", " ")
                        .strip()
                    )
                hours_of_operation = (re.sub(" +", " ", hours_of_operation)).strip()
                hours_of_operation = (
                    hours_of_operation.replace("for the general public.", "")
                    .replace("(midnight)", "")
                    .split("If need")[0]
                    .split("Pharmacy")[0]
                    .strip()
                )
            except:
                hours_of_operation = ""
        else:
            hours_of_operation = ""
        if "coming soon" in hours_of_operation.lower():
            continue
        if "Opening 4/23/" in hours_of_operation:
            hours_of_operation = ""

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
