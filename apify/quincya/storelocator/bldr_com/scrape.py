from bs4 import BeautifulSoup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests


def fetch_data(sgw: SgWriter):

    base_link = "https://bldr.com/location/all-locations"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    items = base.find(class_="landingLayout2Page all-locations").find_all("a")

    locator_domain = "https://bldr.com"

    for i in items:
        link = locator_domain + i["href"]
        if "/location/" not in link:
            continue

        req = session.get(link, headers=headers)
        base = BeautifulSoup(req.text, "lxml")

        location_name = base.h1.text.strip()
        raw_address = list(base.find(class_="address").a.stripped_strings)
        street_address = (
            " ".join(raw_address[:-1]).replace("\xa0", " ").split("(")[0].strip()
        )
        city_line = raw_address[-1].replace("\xa0", " ").replace("\n", "").split(",")
        city = city_line[0].strip()
        state = city_line[-1].strip().split()[0].strip()
        zip_code = city_line[-1].strip().split()[1].strip()
        country_code = "US"
        store_number = link.split("/")[-1]
        try:
            location_type = (
                ", ".join(list(base.find(class_="facilityType").stripped_strings)[1:])
                .split("Location")[0]
                .strip()
            )
            if location_type[-1:] == ",":
                location_type = location_type[:-1].strip()
        except:
            location_type = ""
        phone = base.find(class_="phone").a.text.strip()
        hours_of_operation = (
            " ".join(list(base.find(class_="hours").stripped_strings))
            .split("Pick-")[0]
            .replace("Hours", "")
            .strip()
        )

        try:
            latitude = base.find(id="location-map")["data-lat"]
            longitude = base.find(id="location-map")["data-lng"]
        except:
            latitude = ""
            longitude = ""

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


with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))) as writer:
    fetch_data(writer)
