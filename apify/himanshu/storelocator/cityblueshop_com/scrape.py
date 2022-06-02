import re

from bs4 import BeautifulSoup

from sgrequests import SgRequests

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

import usaddress


def fetch_data(sgw: SgWriter):

    base_url = "https://www.cityblueshop.com/pages/locations"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    }

    session = SgRequests()

    r = session.get(base_url, headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    for parts in soup.find_all("div", {"class": "rte-content colored-links"}):
        for semi_parts in parts.find_all("h3"):
            siblings = list(semi_parts.find_next_sibling().stripped_strings)
            top_level_address = ", ".join(siblings)
            tagged = usaddress.tag(top_level_address)[0]
            if "StateName" not in tagged:
                continue
            state = tagged["StateName"]
            city = tagged["PlaceName"]
            street_address = top_level_address.split(city)[0].strip(",( ")
            if street_address.lower().endswith("shopping center"):
                street_address = street_address.rsplit(",", 1)[0].strip()
            zipcode = tagged["ZipCode"]
            phone1 = ""
            store_request = session.get(semi_parts.find("a")["href"])
            store_soup = BeautifulSoup(store_request.text, "lxml")
            page_url = semi_parts.find("a")["href"]
            for inner_parts in store_soup.find_all(
                "div", {"class": "rte-content colored-links"}
            ):
                longitude = (
                    inner_parts.find("iframe")["src"].split("!2d")[-1].split("!3d")[0]
                )
                latitude = (
                    inner_parts.find("iframe")["src"]
                    .split("!2d")[-1]
                    .split("!3d")[-1]
                    .split("!2m")[0]
                    .split("!3m")[0]
                )
                temp_storeaddresss = list(inner_parts.stripped_strings)
                location_name = semi_parts.text
                if len(temp_storeaddresss) == 7:
                    phone1 = temp_storeaddresss[2].replace("Ph: ", "")
                    hours = " ".join(temp_storeaddresss[-4:])
                elif len(temp_storeaddresss) == 4:
                    phone1 = temp_storeaddresss[-3]
                    hours = " ".join(temp_storeaddresss[-2:])
                elif len(temp_storeaddresss) == 5:
                    hours = " ".join(temp_storeaddresss[-2:])
                    if "Mon" in temp_storeaddresss[-2]:
                        hours = " ".join(temp_storeaddresss[-2:])
                    if "Mon" in temp_storeaddresss[-3]:
                        hours = " ".join(temp_storeaddresss[-3:])
                    phone_list = re.findall(
                        re.compile(r".?(\(?\d{3}\D{0,3}\d{3}\D{0,3}\d{4}).?"),
                        str(temp_storeaddresss),
                    )
                    if phone_list:
                        phone1 = phone_list[-1]
                    temp_storeaddresss.remove(phone1)
                    new = temp_storeaddresss[:-2]
                    if "Mon" in new[-1]:
                        del new[-1]

            sgw.write_row(
                SgRecord(
                    locator_domain="https://www.cityblueshop.com",
                    page_url=page_url,
                    location_name=location_name,
                    street_address=street_address,
                    city=city.strip(),
                    state=state.strip(),
                    zip_postal=zipcode,
                    country_code="US",
                    store_number="",
                    phone=phone1.replace("Ph:", "").strip(),
                    location_type="",
                    latitude=latitude,
                    longitude=longitude,
                    hours_of_operation=hours.strip(),
                )
            )


with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
    fetch_data(writer)
