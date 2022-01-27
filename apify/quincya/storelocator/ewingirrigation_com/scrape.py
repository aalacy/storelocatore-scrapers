import re
from bs4 import BeautifulSoup

from sgrequests import SgRequests

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    base_link = "https://store.ewingirrigation.com/locations/"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    items = base.find(id="storeslist").find_all(class_="liststores")

    for item in items:

        locator_domain = "ewingirrigation.com"
        location_name = "Ewing " + item.find(class_="store_content").a.text.strip()

        if "coming soon" in location_name.lower():
            continue

        link = item.a["data-url"]

        raw_address = (
            item.find(class_="address")
            .text.replace(" CO 80", " CO, 80")
            .replace(" CO. 80", " CO, 80")
            .replace("Knoxville TN 3792", "Knoxville, TN, 3792")
            .replace(", TN ", ", TN, ")
            .replace("\r\n\r\n", "\n")
            .split("\n")
        )
        street_address = raw_address[0].strip()
        city_line = raw_address[-1].strip().split(",")
        city = city_line[0].strip()
        state = city_line[1].strip()
        zip_code = city_line[2].strip()
        if len(zip_code) > 5:
            if "-" not in zip_code:
                zip_code = zip_code[:5] + "-" + zip_code[5:]
        country_code = "US"

        store_number = item.find(class_="number").text.strip()
        try:
            phone = item.find(class_="phone").text.strip()
        except:
            phone = "<MISSING>"

        location_type = "<MISSING>"

        geo = re.findall(r"[0-9]{2}\.[0-9]+,-[0-9]{2,3}\.[0-9]+", str(item))[0].split(
            ","
        )
        latitude = geo[0]
        longitude = geo[1]
        if longitude == "-111.9":
            longitude = "-111.9000"

        hours = (
            " ".join(list(item.find(class_="opening_hours_block").stripped_strings))
            .replace("\xa0", "")
            .replace("\n", " ")
            .replace("AM", "AM ")
            .replace("day", "day ")
            .strip()
        )
        hours_of_operation = (re.sub(" +", " ", hours)).strip()

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


with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
    fetch_data(writer)
