from bs4 import BeautifulSoup

from sglogging import SgLogSetup

from sgrequests import SgRequests

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

logger = SgLogSetup().get_logger("iguanas_co_uk")


def fetch_data(sgw: SgWriter):

    base_link = "https://cdn.contentful.com/spaces/t0ol6oidcclx/environments/master/entries?content_type=restaurant&include=10"

    headers = {
        "authority": "cdn.contentful.com",
        "method": "GET",
        "path": "/spaces/t0ol6oidcclx/environments/master/entries?content_type=restaurant&include=10",
        "scheme": "https",
        "accept": "application/json, text/plain, */*",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "en-US,en;q=0.9",
        "authorization": "Bearer 9e6d06a269fefbffb5dd45528d4fa993878c7f78babec15a8560717ff1217221",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "cross-site",
        "sec-fetch-user": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36",
    }

    session = SgRequests()
    stores = session.get(base_link, headers=headers).json()["items"]

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    locator_domain = "iguanas.co.uk"

    for store in stores:
        slug = store["fields"]["slug"]
        link = "https://www.iguanas.co.uk/restaurants/" + slug
        logger.info(link)

        location_name = store["fields"]["title"]
        if "coming soon" in location_name.lower():
            continue
        try:
            street_address = (
                store["fields"]["addressLine1"] + " " + store["fields"]["addressLine2"]
            ).strip()
        except:
            street_address = store["fields"]["addressLine1"].strip()
        city = store["fields"]["addressCity"]
        try:
            state = store["fields"]["county"]
        except:
            state = ""
        zip_code = store["fields"]["postcode"]
        country_code = "GB"
        store_number = store["fields"]["storeId"]
        location_type = "<MISSING>"
        phone = store["fields"]["phoneNumber"]
        latitude = store["fields"]["addressLocation"]["lat"]
        longitude = store["fields"]["addressLocation"]["lon"]

        if (
            "will open on" in store["fields"]["description"]
            or "currently closed" in store["fields"]["description"]
        ):
            hours_of_operation = "Temporarily Closed"
        else:
            try:
                req = session.get(link, headers=headers)
                base = BeautifulSoup(req.text, "lxml")
            except:
                if "plymouth" in link:
                    link = "https://www.iguanas.co.uk/restaurants/plymouth/plymouth/"
                    req = session.get(link, headers=headers)
                    base = BeautifulSoup(req.text, "lxml")

            hours_of_operation = ""
            try:
                raw_hours = list(base.find(class_="opening-hours").stripped_strings)
                for hours in raw_hours:
                    if "festive hours" in hours.lower():
                        break
                    hours_of_operation = (
                        hours_of_operation + " " + hours.split("/")[0]
                    ).strip()
                hours_of_operation = hours_of_operation.replace(
                    "Opening Hours", ""
                ).strip()
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


with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
    fetch_data(writer)
