import json
import usaddress
from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "youthlandacademy_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

DOMAIN = "https://youthlandacademy.com/"
MISSING = "<MISSING>"


def fetch_data(sgw: SgWriter):
    url = "https://www.youthlandacademy.com/location"
    r = session.get(url, headers=headers, verify=False)
    r = r.text.split("MapifyPro.Google(center")[1].split(", zoom,")[1]
    r = r.split(", map_instance,")[0]
    loclist = json.loads(r)
    for loc in loclist:

        location_name = loc["post_title"]
        page_url = (
            "https://www.youthlandacademy.com/locations/"
            + location_name.lower().replace(" ", "-")
            + "?location="
            + location_name
        )

        log.info(page_url)
        latitude = loc["google_coords"][0]
        longitude = loc["google_coords"][1]
        temp = BeautifulSoup(loc["tooltip_content"], "html.parser")
        temp = temp.get_text(separator="|", strip=True).split("|")
        hours_of_operation = temp[-1]
        if "@" in hours_of_operation:
            hours_of_operation = temp[-2]
        phone = temp[3]
        address = temp[1] + " " + temp[2]
        address = address.replace(",", " ")
        address = usaddress.parse(address)
        i = 0
        street_address = ""
        city = ""
        state = ""
        zip_postal = ""
        while i < len(address):
            temp = address[i]
            if (
                temp[1].find("Address") != -1
                or temp[1].find("Street") != -1
                or temp[1].find("Recipient") != -1
                or temp[1].find("Occupancy") != -1
                or temp[1].find("BuildingName") != -1
                or temp[1].find("USPSBoxType") != -1
                or temp[1].find("USPSBoxID") != -1
            ):
                street_address = street_address + " " + temp[0]
            if temp[1].find("PlaceName") != -1:
                city = city + " " + temp[0]
            if temp[1].find("StateName") != -1:
                state = state + " " + temp[0]
            if temp[1].find("ZipCode") != -1:
                zip_postal = zip_postal + " " + temp[0]
            i += 1
        country_code = "USA"
        if phone.find("Opening soon!") == -1:
            sgw.write_row(
                SgRecord(
                    locator_domain=DOMAIN,
                    page_url=page_url,
                    location_name=location_name,
                    street_address=street_address,
                    city=city,
                    state=state,
                    zip_postal=zip_postal,
                    country_code=country_code,
                    store_number=MISSING,
                    phone=phone,
                    location_type=MISSING,
                    latitude=latitude,
                    longitude=longitude,
                    hours_of_operation=hours_of_operation,
                )
            )


with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
    fetch_data(writer)
