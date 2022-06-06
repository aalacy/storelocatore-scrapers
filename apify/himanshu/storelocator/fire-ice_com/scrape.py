import re

from bs4 import BeautifulSoup
from sgrequests import SgRequests

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()


def fetch_data(sgw: SgWriter):
    base_url = "https://fire-ice.com"
    req = session.get(
        base_url,
        headers={
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36"
        },
    )
    soup = BeautifulSoup(req.text, "lxml")
    locationMenu = soup.find("li", {"id": "menu-item-5881"})
    locations = locationMenu.find("ul").findAll("li")
    locator_domain = base_url
    location_type = ""

    for location in locations:
        link_location = location.find("a")["href"]
        req2 = session.get(
            link_location,
            headers={
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36"
            },
        )
        soup2 = BeautifulSoup(req2.text, "lxml")
        locationName = soup2.title.text
        city = soup2.title.text.split("-")[0]
        phoneNo = (
            soup2.findAll("a", href=re.compile("tel"))[0]["href"]
            .strip()
            .split("tel:")[1]
        )
        address = list(
            soup2.find_all(class_="mk-text-block jupiter-donut-")[-2].stripped_strings
        )
        if "," not in str(address):
            address = list(
                soup2.find_all(class_="mk-text-block jupiter-donut-")[
                    -3
                ].stripped_strings
            )
        zipcode = ""
        streetAddr = address[0].split("•")[0].strip()
        try:
            state = address[0].split("•")[1].split(",")[1].strip()
        except:
            state = address[1].split(",")[1].strip()
        storeNo = "<MISSING>"
        country_code = "US"

        try:
            map_link = soup2.iframe["src"]
            lat_pos = map_link.rfind("!3d")
            latitude = map_link[lat_pos + 3 : map_link.find("!", lat_pos + 5)].strip()
            lng_pos = map_link.find("!2d")
            longitude = map_link[lng_pos + 3 : map_link.find("!", lng_pos + 5)].strip()
        except:
            latitude = "<MISSING>"
            longitude = "<MISSING>"

        hoursOfOp = ""
        if soup2.find("h2", text="Breakfast"):
            hours = (
                soup2.find("h2", text="Breakfast").find_next("p").text.split("Adul")[0]
            )
            if ":" not in hours:
                hours = (
                    soup2.find("h2", text="Breakfast")
                    .find_next("p")
                    .find_next("p")
                    .text.split("Adul")[0]
                )
            hoursOfOp = (hoursOfOp + " Breakfast " + hours).strip()

        if soup2.find("h2", text="Brunch"):
            hours = soup2.find("h2", text="Brunch").find_next("p").text.split("Adul")[0]
            if ":" not in hours:
                hours = (
                    soup2.find("h2", text="Brunch")
                    .find_next("p")
                    .find_next("p")
                    .text.split("Adul")[0]
                )
            hoursOfOp = (hoursOfOp + " Brunch " + hours).strip()

        if soup2.find("h2", text="Lunch"):
            hours = soup2.find("h2", text="Lunch").find_next("p").text.split("Adul")[0]
            if ":" not in hours:
                hours = (
                    soup2.find("h2", text="Lunch")
                    .find_next("p")
                    .find_next("p")
                    .text.split("Adul")[0]
                )
            hoursOfOp = (hoursOfOp + " Lunch " + hours).strip()

        if soup2.find("h2", text="Dinner"):
            hours = soup2.find("h2", text="Dinner").find_next("p").text.split("Adul")[0]
            if ":" not in hours:
                hours = (
                    soup2.find("h2", text="Dinner")
                    .find_next("p")
                    .find_next("p")
                    .text.split("Adul")[0]
                )
            hoursOfOp = (hoursOfOp + " Dinner " + hours).strip()
        hoursOfOp = hoursOfOp.replace("\n", " ")

        sgw.write_row(
            SgRecord(
                locator_domain=locator_domain,
                page_url=link_location,
                location_name=locationName,
                street_address=streetAddr,
                city=city,
                state=state,
                zip_postal=zipcode,
                country_code=country_code,
                store_number=storeNo,
                phone=phoneNo,
                location_type=location_type,
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=hoursOfOp,
            )
        )


with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
    fetch_data(writer)
