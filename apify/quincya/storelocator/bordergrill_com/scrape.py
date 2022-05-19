import re

from bs4 import BeautifulSoup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests


def fetch_data(sgw: SgWriter):

    base_link = "https://www.bordergrill.com/locations/"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    locator_domain = "https://www.bordergrill.com"

    items = base.find_all(class_="col-md-6")

    for item in items:
        if "Directions" not in item.text:
            continue
        link = (
            locator_domain
            + item.find(string="Directions & Info").find_previous("p").a["href"]
        )

        location_name = item.h2.text
        raw_address = list(item.p.stripped_strings)
        street_address = raw_address[0]
        if street_address[-1:] == ",":
            street_address = street_address[:-1]
        city_line = raw_address[1].split(",")
        city = city_line[0].strip()
        state = city_line[-1].strip().split()[0].strip()
        zip_code = city_line[-1].strip().split()[1].strip()
        country_code = "US"
        store_number = ""
        location_type = ""
        try:
            phone = item.find("a", {"href": re.compile(r"tel:")}).text
        except:
            phone = ""

        latitude = ""
        longitude = ""
        map_link = item.a["href"]
        if "@" in map_link:
            latitude = map_link.split("@")[1].split(",")[0]
            longitude = map_link.split("@")[1].split(",")[1]

        hours_of_operation = ""
        try:
            raw_hour = item.find(string="Hours").find_next("p")
            if "temporarily closed" in raw_hour.text.lower():
                hours_of_operation = "Closed Temporarily"
            else:
                for i in range(5):
                    if "pm" in raw_hour.text.lower():
                        hours_of_operation = (
                            hours_of_operation + " " + raw_hour.text.lower()
                        ).strip()
                        raw_hour = raw_hour.find_next("p")
                    else:
                        break
        except:
            pass

        req = session.get(link, headers=headers)

        try:
            page = BeautifulSoup(req.text, "lxml")
            got_page = True
        except:
            got_page = False

        if got_page:
            if not latitude:
                try:
                    latitude = page.find(class_="gmaps")["data-gmaps-lat"]
                    longitude = page.find(class_="gmaps")["data-gmaps-lng"]
                except:
                    pass
            if not hours_of_operation:
                try:
                    raw_hour = page.find(string="Hours").find_next("p")
                except:
                    try:
                        raw_hour = page.find(string="Lunch & Dinner").find_next("p")
                    except:
                        raw_hour = ""
                if "temporarily closed" in raw_hour.text.lower():
                    hours_of_operation = "Closed Temporarily"
                else:
                    for i in range(5):
                        if "pm" in raw_hour.text.lower():
                            hours_of_operation = (
                                hours_of_operation + " " + raw_hour.text.lower()
                            ).strip()
                            raw_hour = raw_hour.find_next("p")
                        else:
                            break

        hours_of_operation = hours_of_operation.split("weekend")[0].strip()

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
