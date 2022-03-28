import re

from bs4 import BeautifulSoup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests


def fetch_data(sgw: SgWriter):

    base_link = "https://www.swamiscafe.com/our-locations"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    items = base.find(class_="pm-location-search-list").find_all("section")
    locator_domain = "https://www.swamiscafe.com"

    script = base.find(id="popmenu-apollo-state")

    lats = re.findall(r'lat":[0-9]{2}\.[0-9]+', str(script))
    lngs = re.findall(r'lng":-[0-9]{2,3}\.[0-9]+', str(script))
    phones = re.findall(r'displayPhone":"\([0-9]{3}\) [0-9]{3}-[0-9]{4}', str(script))

    for item in items:

        location_name = item.h4.text.strip()
        raw_address = list(item.a.stripped_strings)

        street_address = item.span.text.strip()
        city_line = raw_address[-1].strip().split(",")
        city = city_line[0].strip()
        state = city_line[-1].strip().split()[0].strip()
        zip_code = city_line[-1].strip().split()[1].strip()
        country_code = "US"
        store_number = "<MISSING>"
        location_type = "<MISSING>"

        try:
            phone = re.findall(r"[(\d)]{5} [\d]{3}-[\d]{4}", str(item))[0]
        except:
            phone = "<MISSING>"

        try:
            hours_of_operation = (
                item.find(class_="hours")
                .text.replace("\xa0", " ")
                .replace("pm", "pm ")
                .strip()
            )
        except:
            hours_of_operation = ""

        link = locator_domain + item.find("a", string="View Menu")["href"]

        latitude = ""
        longitude = ""
        for i, ph in enumerate(phones):
            if ph.split(':"')[1] == phone:
                latitude = lats[i].split(":")[1]
                longitude = lngs[i].split(":")[1]

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
