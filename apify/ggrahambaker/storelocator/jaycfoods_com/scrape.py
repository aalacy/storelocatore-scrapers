import json
import time

from bs4 import BeautifulSoup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests


def fetch_data(sgw: SgWriter):

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()

    locator_domain = "https://www.jaycfoods.com/"
    ext = "storelocator-sitemap.xml"
    r = session.get(locator_domain + ext, headers=headers)

    soup = BeautifulSoup(r.text, "html.parser")
    loc_urls = soup.find_all("loc")

    link_list = []
    for loc in loc_urls:
        if "/search" in loc.text:
            continue
        link_list.append(loc.text)

    for link in link_list:
        r = session.get(link, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        try:
            loc_json = json.loads(
                soup.find("script", {"type": "application/ld+json"}).contents[0]
            )
        except:
            try:
                session = SgRequests()
                time.sleep(5)
                req = session.get(link, headers=headers)
                time.sleep(4)
                soup = BeautifulSoup(req.text, "lxml")
                loc_json = json.loads(
                    soup.find("script", {"type": "application/ld+json"}).contents[0]
                )
            except:
                session = SgRequests()
                time.sleep(10)
                req = session.get(link, headers=headers)
                time.sleep(10)
                soup = BeautifulSoup(req.text, "lxml")
                loc_json = json.loads(
                    soup.find("script", {"type": "application/ld+json"}).contents[0]
                )

        try:
            addy = loc_json["address"]
            street_address = addy["streetAddress"]
            city = addy["addressLocality"]
            state = addy["addressRegion"]
            zip_code = addy["postalCode"]
        except:
            raw_address = (
                soup.find(class_="StoreAddress-storeAddressGuts")
                .get_text(" ")
                .replace(",", "")
                .replace(" .", ".")
                .replace("..", ".")
                .split("  ")
            )
            street_address = raw_address[0].strip()
            city = raw_address[1].strip()
            state = raw_address[2].strip()
            zip_code = raw_address[3].split("Get")[0].strip()

        coords = loc_json["geo"]

        lat = coords["latitude"]
        longit = coords["longitude"]

        location_name = soup.find("h1", {"class": "StoreDetails-header"}).text

        phone_number = soup.find("span", {"class": "PhoneNumber-phone"}).text
        hours = (
            " ".join(loc_json["openingHours"])
            .replace("Su-Sa", "Sun - Sat:")
            .replace("Su-Fr", "Sun - Fri:")
            .replace("-00:00", " - Midnight")
            .replace("Su ", "Sun ")
            .replace("Mo-Fr", "Mon - Fri")
            .replace("Sa ", "Sat ")
            .replace("  ", " ")
        )
        country_code = "US"

        location_type = "<MISSING>"
        store_number = link.split("/")[-1]

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
