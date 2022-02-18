import re

from bs4 import BeautifulSoup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests


def fetch_data(sgw: SgWriter):

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()

    base_link = "https://graulsmarket.com/locations/"

    req = session.get(base_link, headers=headers)

    base = BeautifulSoup(req.text, "lxml")

    items = base.find(class_="landing-main").find_all(class_="row")

    for item in items:
        locator_domain = "graulsmarket.com"
        try:
            location_name = item.find("h2").text.title().strip()
        except:
            continue
        raw_address = item.find(class_="landing-block-card-address-link").text
        city = raw_address[: raw_address.find(",")].split()[-1]
        if city == "Michaels":
            city = "St. Michaels"
        street_address = raw_address[: raw_address.rfind(city)].strip()
        state = raw_address[raw_address.rfind(",") + 1 : raw_address.rfind(" ")].strip()
        zip_code = raw_address[raw_address.rfind(" ") + 1 :].strip()
        country_code = "US"
        store_number = "<MISSING>"
        try:
            phone = item.find(string="PHONE:").find_next().text.strip()
        except:
            try:
                phone = item.find(string="phone:").find_next().text.strip()
            except:
                phone = item.find(string="Phone:").find_next().text.strip()
        location_type = "<MISSING>"
        raw_item = str(item).replace("&quot;", '"')
        latitude = re.findall(r'lat":[0-9]{2}\.[0-9]+', raw_item)[0].split(":")[1]
        longitude = re.findall(r'lng":-[0-9]{2,3}\.[0-9]+', raw_item)[0].split(":")[1]
        hours_of_operation = item.find_all(class_="landing-block-card-address-link")[
            1
        ].text

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


with SgWriter(SgRecordDeduper(RecommendedRecordIds.PhoneNumberId)) as writer:
    fetch_data(writer)
