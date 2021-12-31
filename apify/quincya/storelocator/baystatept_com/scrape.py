import re
import ssl

from bs4 import BeautifulSoup

from sglogging import SgLogSetup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests

from sgselenium.sgselenium import SgChrome

logger = SgLogSetup().get_logger("baystatept.com")

ssl._create_default_https_context = ssl._create_unverified_context


def fetch_data(sgw: SgWriter):

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()

    base_link = "https://baystatept.com/locations/"
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    items = base.find(class_="footer-loc-list").find_all("h4")

    d_user_agent = (
        "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0"
    )

    driver = SgChrome(user_agent=d_user_agent).driver()

    for item in items:

        location_name = item.text
        final_link = item.a["href"]
        if "ocpn" in location_name.lower():
            continue
        if location_name == "Springfield - Cypress PT":
            final_link = "https://cypress-pt.com/location/springfield-ma/"
        logger.info(final_link)
        final_req = session.get(final_link, headers=headers)
        base = BeautifulSoup(final_req.text, "lxml")

        locator_domain = "https://baystatept.com"

        raw_address = list(base.find(class_="address").p.stripped_strings)
        street_address = raw_address[0].strip()
        city_line = raw_address[1].strip().split(",")
        city = city_line[0].strip()
        state = city_line[-1].strip().split()[0].strip()
        zip_code = city_line[-1].strip().split()[1].strip()
        country_code = "US"
        store_number = "<MISSING>"

        try:
            phone = base.find(class_="location-phone-call").text
        except:
            phone = base.find(class_="address").a.text
        location_type = "<MISSING>"

        try:
            geo = re.findall(r"[0-9]{2}\.[0-9]+,-[0-9]{2,3}\.[0-9]+", str(base))[
                0
            ].split(",")
            latitude = geo[0]
            longitude = geo[1]
        except:
            map_link = base.find(class_="location-maps").iframe["data-lazy-src"]
            lat_pos = map_link.rfind("!3d")
            latitude = map_link[lat_pos + 3 : map_link.find("!", lat_pos + 5)].strip()
            lng_pos = map_link.find("!2d")
            longitude = map_link[lng_pos + 3 : map_link.find("!", lng_pos + 5)].strip()

        hours_of_operation = (
            " ".join(list(base.find(class_="business-hours").stripped_strings))
            .replace("Hours of Operation:", "")
            .replace("Hours of Operation", "")
            .strip()
        )

        if not hours_of_operation:
            if "physical-therapy-boston" in final_link:
                driver.get(
                    "https://knowledgetags.yextpages.net/embed?key=Kx4hae1nknsnY6CyWaguQZgdII_PmU48tFNmS2I7AIM0D8O5inYhCudcfI96yx4o&account_id=4978249222002047427&entity_id=0045&locale=en"
                )
                base = BeautifulSoup(driver.page_source, "lxml")

                try:
                    hours_of_operation = (
                        base.text.split('"hours":[')[1].split("],")[0].replace('"', "")
                    )
                except:
                    hours_of_operation = "<INACCESSIBLE>"

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

    driver.close()


with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
    fetch_data(writer)
