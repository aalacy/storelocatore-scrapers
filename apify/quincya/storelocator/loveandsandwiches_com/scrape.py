from bs4 import BeautifulSoup

from sglogging import sglog

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests

log = sglog.SgLogSetup().get_logger("ikessandwich.com")


def fetch_data(sgw: SgWriter):

    base_link = "https://locations.ikessandwich.com/"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    locator_domain = "ikessandwich.com"

    items = base.find(id="browse-content").find_all(class_="ga-link")

    for item in items:
        state_link = item["href"]
        req = session.get(state_link, headers=headers)
        base = BeautifulSoup(req.text, "lxml")

        stores = base.find(class_="map-list-wrap map-list-tall").ul.find_all(
            "li", recursive=False
        )
        for store in stores:
            store = store.find(class_="map-list-item")
            location_name = store.a.text.strip()
            link = store.a["href"]
            log.info(link)

            req = session.get(link, headers=headers)
            base = BeautifulSoup(req.text, "lxml")

            if "coming soon" in base.find(class_="map-list").text.lower():
                continue

            street_address = (
                base.find(class_="address").find_all("span")[-2].text.strip()
            )
            city_line = (
                base.find(class_="address").find_all("span")[-1].text.strip().split(",")
            )
            city = city_line[0].strip()
            state = city_line[-1].strip().split()[0].strip()
            zip_code = city_line[-1].strip().split()[1].strip()
            country_code = "US"
            store_number = base.find(class_="map-list").div["data-fid"]
            map_link = base.find(class_="ga-link")["href"]
            latitude = map_link.split("=")[-1].split(",")[0]
            longitude = map_link.split("=")[-1].split(",")[1]
            location_type = ", ".join(
                list(base.find(class_="location-services").stripped_strings)
            )

            phone = base.find(class_="phone ga-link").text.strip()

            if "closed temporarily" in base.find(class_="map-list").text.lower():
                hours_of_operation = "Closed Temporarily"
            else:
                try:
                    hours_of_operation = " ".join(
                        list(base.find(class_="hours").stripped_strings)
                    )
                except:
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


with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
    fetch_data(writer)
