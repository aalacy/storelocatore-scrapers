import re

from bs4 import BeautifulSoup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests


def fetch_data(sgw: SgWriter):

    base_link = "https://www.bplplasma.com/find-a-center?search="

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    items = base.find(id="search-boxes-states").find_all(class_="field-content")
    locator_domain = "bplplasma.com"

    for item in items:

        if "Coming Soon" in str(list(item.stripped_strings)):
            continue
        location_name = "BPL Plasma - " + item.h3.text.strip()

        if "generated location" in location_name.lower():
            continue

        raw_address = item.find_all(class_="field__item")[1].text.strip().split(",")
        street_address = " ".join(raw_address[:-2]).strip()
        city = raw_address[-2].strip()
        state = raw_address[-1].strip()[:-6].strip()
        zip_code = raw_address[-1][-6:].strip()

        if not street_address:
            street_address = city
            city = state.split()[0].strip()
            state = state.split()[1].strip()

        street_address = (re.sub(" +", " ", street_address)).strip()

        country_code = "US"
        store_number = item.h3["nodeid"]
        location_type = "<MISSING>"

        phone = item.find(
            class_="field field--name-field-yext-phone field--type-string field--label-hidden field__item"
        ).text.strip()
        hours_of_operation = " ".join(
            list(item.find(class_="custom-hours-formatter").stripped_strings)[:-1]
        )

        geo = re.findall(r"[0-9]{2}\.[0-9]+, -[0-9]{2,3}\.[0-9]+", str(item))[0].split(
            ","
        )
        latitude = geo[0].strip()
        longitude = geo[1].strip()

        link = item.a["href"]

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
