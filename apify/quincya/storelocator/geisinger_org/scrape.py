import re
import json

from lxml import html

from bs4 import BeautifulSoup

from sglogging import SgLogSetup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests

logger = SgLogSetup().get_logger("geisinger.org")


def get_hoo(officehours):
    sel_hoo = html.fromstring(officehours)
    hoo_data = sel_hoo.xpath("//text()")
    hoo_data = [" ".join(i.split()) for i in hoo_data]
    hoo_data = [i for i in hoo_data if i]
    hoo_data = "; ".join(hoo_data).split("We offer")[0].split("; Phone")[0].strip()
    if "office is closed" in hoo_data or "doctors travel" in hoo_data:
        hoo_data = ""
    return hoo_data


def fetch_data(sgw: SgWriter):
    base_link = "https://locations.geisinger.org/index.cfm?clinicName=&distance=300&zip=&searchBtn=FIND+A+LOCATION"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()

    locator_domain = "geisinger.org"

    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    js = str(base).split("var results=")[1].strip().rstrip(";").split("];")[0] + "]"
    json_data = json.loads(js)

    for store in json_data:

        location_name = store["NAME"]
        raw_address = (
            (store["ADDRESS1"] + " " + store["ADDRESS2"]).replace("<br>", " ").strip()
        )

        if re.search(r"\d", raw_address):
            digit = str(re.search(r"\d", raw_address))
            start = int(digit.split("(")[1].split(",")[0])
            street_address = raw_address[start:]
        else:
            street_address = raw_address

        if len(street_address) < 5:
            street_address = raw_address

        street_address = (
            street_address.split("Inside")[0]
            .split("Trader")[0]
            .split("Weis")[0]
            .split("of Gei")[0]
            .split("New")[0]
            .split("within")[0]
            .split("South Gate")[0]
            .split("Best Buy")[0]
            .split(", Wilkes")[0]
            .replace("2:", "")
        ).strip()

        if "Susquehanna" in street_address and "Mall" in street_address[-6:]:
            street_address = street_address.split("Susquehanna")[0].strip()

        city = store["CITY"]
        state = store["STATE"]
        if not state:
            if "Wilkes" in city:
                state = "PA"
        zip_code = store["ZIPCODE"].replace("*", "").strip()
        country_code = "US"
        phone = store["PHONE"]
        if not phone:
            try:
                phone = re.findall(
                    r"[(\d)]{3}-[\d]{3}-[\d]{4}", store["OFFICENUMBERS"]
                )[0]
            except:
                phone = ""
        phone = phone.split("<br>")[0].strip()
        store_number = store["CLINICID"]
        location_type = ""
        hours_of_operation = ""
        latitude = ""
        longitude = ""

        if store["OFFICEHOURS"].strip():
            hours_of_operation = get_hoo(store["OFFICEHOURS"].strip())

        link = "https://locations.geisinger.org/details.cfm?id=" + str(store_number)
        logger.info(link)
        req = session.get(link, headers=headers)
        try:
            base = BeautifulSoup(req.text, "lxml")
            map_link = base.iframe["src"]
            req = session.get(map_link, headers=headers)
            map_str = BeautifulSoup(req.text, "lxml")

            geo = re.findall(r"[0-9]{2}\.[0-9]+,-[0-9]{2,3}\.[0-9]+", str(map_str))[
                0
            ].split(",")
            latitude = geo[0]
            longitude = geo[1]
            if latitude[0] in ["8", "9"]:
                geo = re.findall(r"-[0-9]{2,3}\.[0-9]+,[0-9]{2}\.[0-9]+", str(map_str))[
                    0
                ].split(",")
                latitude = geo[1]
                longitude = geo[0]
        except:
            pass

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
                raw_address=raw_address,
            )
        )


with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
    fetch_data(writer)
