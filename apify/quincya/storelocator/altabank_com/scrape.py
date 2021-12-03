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

    session = SgRequests()

    base_link = "https://altabank.com/locations/"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    driver = SgChrome(user_agent=user_agent).driver()

    driver.get(base_link)
    base = BeautifulSoup(driver.page_source, "lxml")

    driver.close()

    locations = base.findAll(class_="location-card")
    locator_domain = "altabank.com"

    for location in locations:

        location_name = location.find(class_="branch-name").text

        raw_address = location.find(class_="branch-address").find_all("p")
        street_address = raw_address[0].text
        city_line = raw_address[1].text
        city = city_line[: city_line.find(",")].strip()
        state = city_line[city_line.find(",") + 1 : city_line.rfind(" ")].strip()
        zip_code = city_line[city_line.rfind(" ") + 1 :].strip()
        country_code = "US"
        store_number = "<MISSING>"
        phone = (
            location.find(class_="branch-numbers")
            .p.text.replace("Phone: ", "")
            .replace("Toll Free:", "")
            .strip()
        )
        location_type = "<MISSING>"

        hours_of_operation = ""
        raw_hours = list(location.find(class_="branch-hours").stripped_strings)
        for hour in raw_hours:
            if "drive" not in hour and "peration" not in hour:
                hours_of_operation = (hours_of_operation + " " + hour).strip()

        link = location.a["href"]
        req = session.get(link, headers=headers)
        base = BeautifulSoup(req.text, "lxml")

        raw_gps = base.find(class_="location-address").find(class_="btn blue")["href"]
        start_point = raw_gps.find("@")
        latitude = raw_gps[start_point + 1 : raw_gps.find(",", start_point)]
        long_start = raw_gps.find(",", start_point) + 1
        longitude = raw_gps[long_start : raw_gps.find(",", long_start)]

        try:
            int(latitude[4:8])
        except:
            latitude = "<MISSING>"
            longitude = "<MISSING>"

        if "2176 N Main" in street_address:
            latitude = "41.771821"
            longitude = "-111.833339"

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
