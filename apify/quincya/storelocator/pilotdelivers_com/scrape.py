import re

from bs4 import BeautifulSoup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests


def fetch_data(sgw: SgWriter):

    base_links = [
        "https://www.pilotdelivers.com/global-network/domestic/",
        "https://www.pilotdelivers.com/global-network/international/",
    ]

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    locator_domain = "pilotdelivers.com"

    for base_link in base_links:

        session = SgRequests()
        req = session.get(base_link, headers=headers)
        base = BeautifulSoup(req.text, "lxml")

        items = base.find_all(class_="locations-link")

        for item in items:
            location_name = item.find(class_="station-title").text
            street_address = item.find_all("h6")[1].text.replace("66265", "").strip()
            city_line = item.find_all("h6")[2].text.split(",")
            if "domestic" in base_link:
                city = city_line[0].strip()
                state = city_line[-1].strip().split()[0].strip()
                zip_code = city_line[-1].strip().split()[1].strip()
                country_code = "US"
                store_number = "<MISSING>"
                location_type = "<MISSING>"
            else:
                if "Dusseldorf" in location_name:
                    country_code = "Germany"
                else:
                    country_code = location_name.split(",")[1].strip()
                city = location_name.split(",")[0].strip()
                if country_code == "Canada":
                    city = city_line[0].strip()
                    state = city_line[-1].strip().split()[0].strip()
                    zip_code = " ".join(city_line[-1].strip().split()[1:]).strip()
                else:
                    if len(city_line) == 3:
                        city = city_line[0].strip()
                        state = city_line[1].strip()
                        zip_code = city_line[-1].strip()
                    elif len(city_line) == 2:
                        state = "<MISSING>"
                        zip_code = city_line[-1].strip()
                        if city != city_line[0].strip():
                            street_address = street_address + " " + city_line[0].strip()
            street_address = (re.sub(" +", " ", street_address)).strip()
            if street_address[-1:] == ",":
                street_address = street_address[:-1]

            zip_code = zip_code.replace("--", "").strip()
            if city == zip_code:
                city = state
                state = ""

            phone = (
                item.find(class_="station-contact")
                .a.text.replace("Main Phone:", "")
                .strip()
            )
            hours_of_operation = "<MISSING>"
            latitude = "<INACCESSIBLE>"
            longitude = "<INACCESSIBLE>"
            link = item["data-href"]

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
