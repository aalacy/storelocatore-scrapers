import re

from bs4 import BeautifulSoup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests


def fetch_data(sgw: SgWriter):

    base_link = "https://www.buildabear.com.au/store-locator-babw"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    items = base.find_all(class_="addressind")

    for item in items:
        locator_domain = "buildabear.com.au"
        try:
            location_name = item.find(class_="store-locator-branch-name").text.strip()
        except:
            continue
        raw_address = list(
            item.find(class_="store-locator-branch-address").stripped_strings
        )
        try:
            if "moved " in raw_address[-4]:
                raw_address.pop(-4)
        except:
            pass

        street_address = " ".join(raw_address[:-4])
        if street_address:
            city_line = raw_address[-4].replace("Centre SA", "Centre, SA").split(",")
            if len(city_line) == 1:
                ste = re.findall(r"[A-Z]{3}", str(raw_address[-4]))[0]
                city_line = raw_address[-4].replace(ste, "," + ste).split(",")
        else:
            street_address = raw_address[0]
            city_line = raw_address[1].split(",")
        if street_address[-1:] == ",":
            street_address = street_address[:-1]

        if (
            "Shop" in street_address[:10]
            or "Kiosk" in street_address[:10]
            or "Store" in street_address[:10]
        ):
            street_address = " ".join(street_address.split()[2:])
        if street_address[:1] in [",", "-"]:
            street_address = street_address[1:]

        street_address = (
            street_address.replace("Westfield Miranda,", "")
            .replace(", Broadbeach", "")
            .replace("Westfield Knox", "")
            .replace("Lakeside Joondalup,", "")
            .replace("Westfield Carousel,", "")
            .strip()
        )
        city = city_line[0].strip()
        state = city_line[1].split()[0].strip()
        zip_code = city_line[1].split()[-1].strip()
        country_code = "AU"
        location_type = "<MISSING>"
        phone = (
            item.find(class_="store-locator-phone").text.replace("Phone:", "").strip()
        )
        hours_of_operation = (
            item.find(class_="store-locator-branch-hours")
            .text.replace("\xa0", "")
            .strip()
        )
        store_number = ""
        map_link = item.find(class_="store-locator-branch-address").a["href"]
        try:
            geo = re.findall(r"-[0-9]{2}\.[0-9]+,[0-9]{2,3}\.[0-9]+", map_link)[
                0
            ].split(",")
            latitude = geo[0]
            longitude = geo[1]
        except:
            lat_pos = map_link.rfind("!1d")
            latitude = map_link[lat_pos + 3 : map_link.find("!", lat_pos + 5)].strip()
            lng_pos = map_link.find("!2d")
            longitude = map_link[lng_pos + 3 : map_link.find("!", lng_pos + 5)].strip()

        if len(latitude) > 40:
            latitude = ""
            longitude = ""

        sgw.write_row(
            SgRecord(
                locator_domain=locator_domain,
                page_url=base_link,
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
