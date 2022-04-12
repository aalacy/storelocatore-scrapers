import re

from bs4 import BeautifulSoup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests


def fetch_data(sgw: SgWriter):

    base_link = "https://www.rebounderz.com/city/"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    items = base.find(
        class_="fl-row fl-row-fixed-width fl-row-bg-none fl-node-5cdf20eadb842"
    ).find_all(class_="fl-rich-text")
    locator_domain = "rebounderz.com"

    all_links = base.find(
        class_="fl-module fl-module-rich-text fl-node-5e67c3c34714e"
    ).find_all("a")

    for item in items:
        location_name = item.h3.text.strip()

        raw_address = item.p.text.split("\n")
        street_address = raw_address[0]
        city = raw_address[1].split(",")[0]
        state = raw_address[1].split(",")[1].split()[0]
        zip_code = raw_address[1].split(",")[1].split()[1]
        country_code = "US"
        store_number = "<MISSING>"
        location_type = "<MISSING>"
        phone = item.find_all("p")[-2].text.replace("Tel:", "").strip()

        for i in all_links:
            if i.text.split(",")[0] in item.text:
                link = "https://www.rebounderz.com" + i["href"]
                if "apopka" in link:
                    link = "https://www.rebounderz.com/city/wekiva-springs"
                break

        req = session.get(link, headers=headers)
        base = BeautifulSoup(req.text, "lxml")

        try:
            hours_of_operation = base.find_all(
                "div",
                {
                    "class": re.compile(
                        r"fl-col-group fl-node-.+fl-col-group-nested fl-col-group-custom-width"
                    )
                },
            )[0].text.replace("\n", " ")
            hours_of_operation = (re.sub(" +", " ", hours_of_operation)).strip()
            hours_of_operation = (
                hours_of_operation.replace("Munchkin and Me UNAVAILABLE", "")
                .replace("*Glow Night from 6PM to 10PM*", "")
                .replace("Munchkin and Me TBD", "")
                .split("Munchkin")[0]
                .strip()
            )
            hours_of_operation = (re.sub(" +", " ", hours_of_operation)).strip()
        except:
            hours_of_operation = ""

        if "coming soon" in hours_of_operation.lower():
            continue

        try:
            map_link = base.find(class_="fl-map").iframe["src"]
            req = session.get(map_link, headers=headers)
            map_str = BeautifulSoup(req.text, "lxml")
            geo = (
                re.findall(r"\[[0-9]{2}\.[0-9]+,-[0-9]{2,3}\.[0-9]+\]", str(map_str))[0]
                .replace("[", "")
                .replace("]", "")
                .split(",")
            )
            latitude = geo[0]
            longitude = geo[1]
        except:
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


with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
    fetch_data(writer)
