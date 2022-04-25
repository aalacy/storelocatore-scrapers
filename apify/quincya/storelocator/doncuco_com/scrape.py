import re

from bs4 import BeautifulSoup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests


def fetch_data(sgw: SgWriter):

    base_link = "https://www.doncuco.com/order-online-1"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    locator_domain = "doncuco.com"

    items = base.find_all(class_="font_2")
    for item in items:
        link = item.a["href"]

        req = session.get(link, headers=headers)
        base = BeautifulSoup(req.text, "lxml")

        location_name = "DON CUCO MEXICAN RESTAURANT: " + base.find_all("h2")[1].text

        raw_address = (
            base.find(id="SITE_PAGES")
            .find("a", attrs={"target": "_blank"})
            .text.replace("ADDRESS", "")
            .replace("Ave.", "Ave.\n")
            .strip()
            .split("\n")
        )
        street_address = raw_address[0]
        try:
            city_line = raw_address[1].strip().split(",")
        except:
            city_line = (
                base.find(id="SITE_PAGES")
                .find_all("a", attrs={"target": "_blank"})[1]
                .text.strip()
                .split(",")
            )
        city = city_line[0].strip()
        state = city_line[-1].strip().split()[0].strip()
        zip_code = city_line[-1].strip().split()[1].strip()
        country_code = "US"
        store_number = "<MISSING>"
        location_type = "<MISSING>"

        phone = base.find("a", {"href": re.compile(r"tel:")}).text
        try:
            hours_of_operation = (
                base.find(id="SITE_PAGES")
                .find_all("div", attrs={"data-testid": "richTextElement"})[1]
                .text.split("\u200b")[0]
                .replace("HOURS", "")
                .replace("\n", " ")
                .strip()
            )
        except:
            hours_of_operation = "<MISSING>"

        map_str = base.find(id="SITE_PAGES").find("a", attrs={"target": "_blank"})[
            "href"
        ]
        geo = re.findall(r"[0-9]{2}\.[0-9]+,-[0-9]{2,3}\.[0-9]+", map_str)[0].split(",")
        latitude = geo[0]
        longitude = geo[1]

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
