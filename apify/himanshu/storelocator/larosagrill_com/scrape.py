from bs4 import BeautifulSoup as bs

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests
import re


DOMAIN = "larosagrill.com"
LOCATION_URL = "https://larosagrill.com/menu-locations"
HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
}

session = SgRequests()


def pull_content(url):
    soup = bs(session.get(url, headers=HEADERS).content, "lxml")
    return soup


def handle_missing(field):
    if field is None or (isinstance(field, str) and len(field.strip()) == 0):
        return "<MISSING>"
    return field


def fetch_data(sgw: SgWriter):
    soup = pull_content(LOCATION_URL)
    content = (
        soup.find_all("div", {"class": "blog"})[1]
        .find("div", {"class": "container"})
        .find_all("div", {"class": "marginall-5"})
    )
    for row in content:
        locator_domain = DOMAIN
        coming_soon = row.find("img", {"src": "images/coming soon.jpg"})
        if not coming_soon:
            location_name = handle_missing(
                row.find("div", {"class": "locationheader"}).text.strip()
            )
            address = (
                row.find(
                    "div", {"style": "margin:5px 0;color:white;text-align:center;"}
                )
                .get_text(strip=True, separator=",")
                .replace(",,", ",")
                .split(",")
            )
            if len(address) > 1:
                street_address = address[0].strip()
                city = address[1].strip()
                state = re.sub(r"\d+", "", address[2]).strip()
                zip_code = re.sub(r"\D+", "", address[2]).strip()
                if len(address) < 4 and "United States" in address[2]:
                    city = "<MISSING>"
                    state = address[1]
                    zip_code = "<MISSING>"
            country_code = "US"
            store_number = "<MISSING>"
            phone = row.find("div", {"class": "locationheader1"})
            if not phone:
                phone = "<MISSING>"
            else:
                phone = phone.find("a", {"style": "border:0px;padding:0;"})[
                    "href"
                ].replace("tel:", "")

            hours_of_operation = "<MISSING>"
            hoo = row.find("a", text=re.compile(r"OPEN\s+HOURS"))
            if hoo:
                hours_of_operation = hoo.find_next("a").text.strip()
            location_type = "<MISSING>"
            latlong = row.find("a", {"href": re.compile(r"www.google.com/maps")})
            latitude = "<MISSING>"
            longitude = "<MISSING>"
            if latlong:
                geo = re.findall(
                    r"[0-9]{2}\.[0-9]+,-[0-9]{2,3}\.[0-9]+", latlong["href"]
                )[0].split(",")
                latitude = geo[0]
                longitude = geo[1]
            link = "https://larosagrill.com/" + row.a["href"]

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
