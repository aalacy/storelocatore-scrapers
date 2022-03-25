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

    base_link = "https://www.mysodalicious.com/loc"

    req = session.get(base_link, headers=headers)

    base = BeautifulSoup(req.text, "lxml")

    items = base.find_all(class_="index-section")[1:]

    for item in items:
        locator_domain = "mysodalicious.com"
        location_name = item.find("h2").text.title().strip()
        raw_address = list(item.find("p").stripped_strings)
        street_address = raw_address[0].strip()
        city_line = raw_address[1].strip().split(",")
        if "," not in raw_address[1]:
            city_line = raw_address[2].strip().split(",")
        city = city_line[0].strip()
        state = city_line[-1].strip().split()[0].strip()
        zip_code = city_line[-1].strip().split()[1].strip()
        country_code = "US"
        store_number = item["data-collection-id"]
        phone = ""
        try:
            phone = item.find("a", {"href": re.compile(r"tel:")}).text.strip()
            if phone:
                if len(phone) < 6:
                    phone = "".join(raw_address[2:])
        except:
            try:
                phone = raw_address[2]
            except:
                pass

        if "@" in phone or "," in phone:
            phone = ""

        location_type = "<MISSING>"

        try:
            latitude = re.findall(r'mapLat":[0-9]{2}\.[0-9]+', str(item))[0].split(":")[
                1
            ]
            longitude = re.findall(r'mapLng":-[0-9]{2,3}\.[0-9]+', str(item))[0].split(
                ":"
            )[1]
        except:
            latitude = ""
            longitude = ""

        if "temporarily closed" in item.text.lower():
            hours_of_operation = "Temporarily Closed"
        else:
            try:
                raw_hours = (
                    item.find_all("h3")[-2].text + " " + item.find_all("h3")[-1].text
                )
                if "hours:" not in raw_hours:
                    try:
                        raw_hours = (
                            item.find_all("h3")[-3].text
                            + " "
                            + item.find_all("h3")[-2].text
                            + " "
                            + item.find_all("h3")[-1].text
                        )
                    except:
                        raw_hours = (
                            item.find_all("h3")[-2].text
                            + " "
                            + item.find_all("h3")[-1].text
                        )
            except:
                hours_of_operation = (
                    item.find("strong", string="Hours:").find_previous().text
                )
            hours_of_operation = (
                (raw_hours).replace("Hours:", "hours:").split("hours:")[-1].strip()
            )
        if "closed closed" in hours_of_operation:
            hours_of_operation = "Lobby Closed"

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


with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
    fetch_data(writer)
