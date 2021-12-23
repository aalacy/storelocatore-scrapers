import re
from bs4 import BeautifulSoup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests


def addy_ext(addy):
    address = addy.split(",")
    city = address[0]
    state_zip = address[1].strip().split(" ")
    state = state_zip[0]
    zip_code = state_zip[1]
    return city, state, zip_code


def fetch_data(sgw: SgWriter):
    locator_domain = "https://www.matchboxrestaurants.com"

    base_link = "https://matchboxrestaurants.com/"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    hrefs = base.find(class_="Header-nav-folder").find_all("a")
    link_list = []
    for href in hrefs:
        link_list.append(locator_domain + href["href"])

    for link in link_list:
        req = session.get(link, headers=headers)
        base = BeautifulSoup(req.text, "lxml")

        content = list(
            base.find(class_="Main-content")
            .find(class_="sqs-block html-block sqs-block-html")
            .stripped_strings
        )

        location_name = base.h1.text
        street_address = content[1]
        city_line = content[2]
        if "," not in city_line:
            street_address = street_address + " " + city_line
            city_line = content[3]
        city, state, zip_code = addy_ext(city_line)
        phone_number = (
            base.find(class_="Main-content")
            .find(class_="sqs-block html-block sqs-block-html")
            .a.text.strip()
        )
        if "-" not in phone_number:
            phone_number = content[3].replace("call", "").strip()
        hours = " ".join(
            list(
                base.find(class_="Main-content")
                .find_all(class_="sqs-block html-block sqs-block-html")[2]
                .stripped_strings
            )[1:]
        )
        hours = (
            hours.split("happy")[0]
            .split("Follow")[0]
            .split("milk")[0]
            .split("PRIVATE")[0]
            .replace("\xa0", "")
            .replace("now open!", "")
            .strip()
        )
        hours = (re.sub(" +", " ", hours)).strip()

        map_link = base.find(class_="Main-content").find("a", string="get directions")[
            "href"
        ]
        start_idx = map_link.find("/@")
        if start_idx > 0:
            end_idx = map_link.find("z/data")
            coords = map_link[start_idx + 2 : end_idx].split(",")
            lat = coords[0]
            longit = coords[1]
        else:
            lat = "<MISSING>"
            longit = "<MISSING>"
        country_code = "US"
        store_number = "<MISSING>"
        location_type = "<MISSING>"

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
                phone=phone_number,
                location_type=location_type,
                latitude=lat,
                longitude=longit,
                hours_of_operation=hours,
            )
        )


with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
    fetch_data(writer)
