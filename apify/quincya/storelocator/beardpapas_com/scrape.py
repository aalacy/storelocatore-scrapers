import json
import re

from bs4 import BeautifulSoup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests


def fetch_data(sgw: SgWriter):

    base_link = "https://www.beardpapas.com/locations"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    items = base.find_all(class_="row sqs-row")[1].find_all(
        class_="sqs-block html-block sqs-block-html"
    )
    locator_domain = "beardpapas.com"

    for item in items:

        try:
            location_name = item.strong.text.strip()
            link = item.a["href"]
        except:
            if "Cucamonga" in location_name:
                link = ""
            pass

        raw_data = list(item.stripped_strings)

        try:
            street_address = raw_data[1].strip()
            if "TX" in street_address:
                street_address = raw_data[0]
        except:
            continue
        if "Located in" in street_address:
            street_address = raw_data[2].strip()
        if street_address[-1:] == ",":
            street_address = street_address[:-1]
        city = raw_data[-1].split(",")[0].strip()
        state = raw_data[-1].split(",")[1].split()[0].strip()
        try:
            zip_code = raw_data[-1].split(",")[1].split()[1].strip()
        except:
            if "2167 Broadway" in street_address:
                street_address = "2167 Broadway"
                city = "New York"
                state = "NY"
                zip_code = "10024"
            else:
                zip_code = raw_data[2].split(",")[2].strip()
        zip_code = zip_code.replace("5542", "55425")
        street_address = street_address.replace("San Tan Village /", "").strip()
        location_type = ""
        country_code = "US"
        store_number = ""

        if link:
            req = session.get(link, headers=headers)
            base = BeautifulSoup(req.text, "lxml")

            store = json.loads(
                base.find(class_="sqs-block map-block sqs-block-map")["data-block-json"]
            )
            try:
                phone = (
                    base.find_all(class_="row sqs-row")[1]
                    .find(string="contact us")
                    .find_next()
                    .text.split(":")[1]
                    .strip()
                )
            except:
                try:
                    phone = (
                        base.find_all(class_="row sqs-row")[1]
                        .find(string="Contact")
                        .find_next()
                        .text.split(":")[1]
                        .strip()
                    )
                except:
                    phone = re.findall(
                        r"[(\d)]{5} [\d]{3}-[\d]{4}",
                        str(base.find_all(class_="row sqs-row")[1]),
                    )[0]
            try:
                hours_of_operation = (
                    base.find_all(class_="row sqs-row")[1]
                    .find(string="Hours")
                    .find_previous("div")
                    .get_text(" ")
                    .replace("Hours", "")
                    .strip()
                )
            except:
                hours_of_operation = (
                    base.find_all(class_="row sqs-row")[1]
                    .find(string="Temporary Hours")
                    .find_previous("div")
                    .get_text(" ")
                    .replace("Temporary Hours", "")
                    .strip()
                )
            if not hours_of_operation:
                hours_of_operation = (
                    base.find_all(class_="row sqs-row")[1]
                    .find(string="Hours")
                    .find_previous(class_="col sqs-col-4 span-4")
                    .get_text(" ")
                    .replace("Hours", "")
                    .replace("\n ", "")
                    .strip()
                )
            latitude = store["location"]["mapLat"]
            longitude = store["location"]["mapLng"]
        else:
            link = base_link
            phone = ""
            hours_of_operation = ""
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
