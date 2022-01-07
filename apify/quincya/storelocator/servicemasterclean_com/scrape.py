import re

from bs4 import BeautifulSoup

from sglogging import SgLogSetup

from sgrequests import SgRequests

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

logger = SgLogSetup().get_logger("servicemasterclean_com")


def fetch_data(sgw: SgWriter):

    base_link = "https://www.servicemasterclean.com/locations/location-list/"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    all_links = []
    found_poi = []

    items = base.find(id="LocationList_HDR0_State").find_all("option")[1:]
    locator_domain = "servicemasterclean.com"

    for item in items:
        all_links.append(
            "https://www.servicemasterclean.com/locations/"
            + item.text.replace(" ", "-").lower()
        )

    for link in all_links:
        logger.info(link)
        req = session.get(link, headers=headers)
        base = BeautifulSoup(req.text, "lxml")

        items = base.find_all(class_="third")
        for item in items:

            location_name = item.strong.text.strip()

            raw_address = list(item.address.stripped_strings)
            street_address = (
                " ".join(raw_address[:-1])
                .replace("\r\n", "")
                .replace("\n", " ")
                .replace("\t", "")
                .replace("\xa0", " ")
                .strip()
            )
            if not street_address:
                street_address = "<MISSING>"
            street_address = (re.sub(" +", " ", street_address)).strip()
            city = raw_address[-1].split(",")[0].strip()
            state = raw_address[-1].split(",")[1][:-6].strip()
            zip_code = raw_address[-1][-6:].strip()
            country_code = "US"
            location_type = "<MISSING>"
            phone = item.find(class_="flex phone-contact").text.strip()
            hours_of_operation = "<MISSING>"
            latitude = "<MISSING>"
            longitude = "<MISSING>"
            final_link = (
                "https://www.servicemasterclean.com"
                + item.find(class_="text-btn")["href"]
            )

            if final_link in found_poi:
                continue
            req = session.get(final_link, headers=headers)
            base = BeautifulSoup(req.text, "lxml")

            if "COMING SOON" in base.h1.text.upper():
                continue

            try:
                store_number = base.find(class_="box")["data-key"]
            except:
                store_number = "<MISSING>"

            hours_of_operation = "<MISSING>"
            try:
                if base.find(id="HoursContainer").text.strip():
                    try:
                        payload = {
                            "_m_": "HoursPopup",
                            "HoursPopup$_edit_": store_number,
                        }

                        response = session.post(
                            final_link, headers=headers, data=payload
                        )
                        hr_base = BeautifulSoup(response.text, "lxml")
                        hours_of_operation = " ".join(
                            list(hr_base.table.stripped_strings)
                        )
                    except:
                        hours_of_operation = "<MISSING>"
            except:
                pass

            found_poi.append(final_link)

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
