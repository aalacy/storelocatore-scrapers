import re

from bs4 import BeautifulSoup

from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests

session = SgRequests()


def fetch_data(sgw: SgWriter):
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36"
    }
    r = session.get("https://www.theshuckinshack.com/locations/", headers=headers)
    soup = BeautifulSoup(r.text, "lxml")

    for state in soup.find_all("div", {"class": "location-wrapper"}):
        current_state = state.find("h2").text.strip()
        for location in state.find_all("a"):
            page_url = location["href"]
            if "coming-soon" in page_url:
                continue
            location_name = location.text.strip()
            if "coming soon" in location_name.lower():
                continue
            location_request = session.get(location["href"], headers=headers)
            location_soup = BeautifulSoup(location_request.text, "lxml")
            if (
                list(
                    location_soup.find("div", {"class": "flex-column-30"})
                    .find_all("p")[0]
                    .stripped_strings
                )
                == []
            ):
                continue
            address = list(
                location_soup.find("div", {"class": "flex-column-30"})
                .find_all("p")[0]
                .stripped_strings
            )
            if "," not in address[1]:
                city = address[1]
                zipp = "<MISSING>"
            else:
                city = address[1].split(",")[0]
                if len(address[1].split(",")[1].split(" ")) == 3:
                    zipp = address[1].split(",")[1].split(" ")[2]
                else:
                    zipp = "<MISSING>"
            phone = list(
                location_soup.find("div", {"class": "flex-column-30"})
                .find_all("p")[1]
                .stripped_strings
            )[0]
            hours = " ".join(
                list(
                    location_soup.find("div", {"class": "flex-column-30"})
                    .find_all("div")[-1]
                    .stripped_strings
                )
            ).replace("\xa0", "")
            hours = (re.sub(" +", " ", hours)).strip()
            geo_location = location_soup.find("a", text=re.compile("Get Directions"))
            if geo_location is not None:
                geo_location1 = location_soup.find(
                    "a", text=re.compile("Get Directions")
                )["href"]

            latitude = (
                geo_location1.split("/@")[1].split(",")[0]
                if "/@" in geo_location1
                else "<MISSING>"
            )
            longitude = (
                geo_location1.split("/@")[1].split(",")[1]
                if "/@" in geo_location1
                else "<MISSING>"
            )
            location_type = ""

            sgw.write_row(
                SgRecord(
                    locator_domain="http://www.theshuckinshack.com",
                    page_url=page_url,
                    location_name=location_name,
                    street_address=address[0].strip(),
                    city=city,
                    state=current_state,
                    zip_postal=zipp,
                    country_code="US",
                    store_number="<MISSING>",
                    phone=phone,
                    location_type=location_type,
                    latitude=latitude,
                    longitude=longitude,
                    hours_of_operation=hours,
                )
            )


with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
    fetch_data(writer)
