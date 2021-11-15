import json
import re

from bs4 import BeautifulSoup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests

import os

os.environ[
    "PROXY_URL"
] = "http://groups-RESIDENTIAL,country-gb:{}@proxy.apify.com:8000/"


def fetch_data(sgw: SgWriter):

    base_link = "https://www.curzon.com/venues/"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    all_scripts = base.find_all("script")
    for script in all_scripts:
        if '"postcode"' in str(script):
            script = str(script)
    raw_data = script.split('"cinemas":')[1].split('}],"curzonHome')[0] + "}]"

    stores = json.loads(raw_data)
    locator_domain = "curzon.com"

    for store in stores:

        link = "https://www.curzon.com" + store["findMoreLink"]
        location_name = store["name"]
        street_address = store["address"]
        city = store["city"]
        state = "<MISSING>"
        zip_code = store["postcode"].strip()
        country_code = "GB"
        store_number = store["id"]
        location_type = "<MISSING>"
        phone = "<MISSING>"
        hours_of_operation = "<MISSING>"

        req = session.get(link, headers=headers)
        base = BeautifulSoup(req.text, "lxml")

        map_link = base.find(class_="getting-here-info__link")["href"]
        try:
            try:
                geo = re.findall(r"[0-9]{2}\.[0-9]+,[0-9]{1,3}\.[0-9]+", map_link)[
                    0
                ].split(",")
            except:
                geo = re.findall(r"[0-9]{2}\.[0-9]+,-[0-9]{1,3}\.[0-9]+", map_link)[
                    0
                ].split(",")
            latitude = geo[0]
            longitude = geo[1]
        except:
            latitude = "<MISSING>"
            longitude = "<MISSING>"

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
