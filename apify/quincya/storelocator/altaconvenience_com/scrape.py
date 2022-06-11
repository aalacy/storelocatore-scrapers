import re

from bs4 import BeautifulSoup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sglogging import SgLogSetup

from sgrequests import SgRequests

log = SgLogSetup().get_logger("altaconvenience.com")


def fetch_data(sgw: SgWriter):

    base_link = "https://altaconvenience.com/home#map"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base_str = str(BeautifulSoup(req.text, "lxml"))

    raw_data = base_str.split("markerLocations =")[1].split("var ")[0].split("],")

    locator_domain = "altaconvenience.com"

    for item in raw_data:
        if 'href="/Alta' not in item:
            continue
        link = "http://altaconvenience.com" + item.split('href="')[1].split('">')[0]
        log.info(link)
        req = session.get(link, headers=headers)
        base = BeautifulSoup(req.text, "lxml")

        location_name = base.h1.text.split("\n")[0].strip()
        raw_address = list(base.find(class_="d-inline-block address").stripped_strings)[
            -1
        ].split(",")
        street_address = " ".join(raw_address[:-2])
        city = raw_address[-2].strip()
        state = raw_address[-1].split()[0]
        zip_code = raw_address[-1].split()[1]
        country_code = "US"
        phone = list(base.find(class_="d-block phone").stripped_strings)[-1]
        store_number = location_name.split("#")[1].strip()
        location_type = "<MISSING>"

        try:
            hours_of_operation = list(
                base.find(class_="d-block hours").stripped_strings
            )[-1]
        except:
            hours_of_operation = "<MISSING>"

        geo = (
            re.findall(r"[0-9]{2}\.[0-9]+, -[0-9]{2,3}\.[0-9]+", str(item))[0]
            .replace("[", "")
            .replace("]", "")
            .split(",")
        )
        latitude = geo[0].strip()
        longitude = geo[1].strip()

        sgw.write_row(
            SgRecord(
                locator_domain=locator_domain,
                page_url=link,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state.replace(",", ""),
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
