import re

from bs4 import BeautifulSoup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests


def fetch_data(sgw: SgWriter):

    base_link = "https://www.localiyours.com"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)

    base = BeautifulSoup(req.text, "lxml")

    content = base.find(class_="pm-map-wrap pm-location-search-list")
    items = content.find_all("section")

    js = base.find(id="popmenu-apollo-state").contents[0]
    lats = re.findall(r'lat":[0-9]{2}\.[0-9]+', str(js))
    lngs = re.findall(r'lng":-[0-9]{2,3}\.[0-9]+', str(js))

    if len(lats) > len(items):
        lats.pop(0)
        lngs.pop(0)

    for i, item in enumerate(items):
        locator_domain = "localiyours.com"
        location_name = item.h4.text

        raw_data = list(item.a.stripped_strings)

        street_address = " ".join(raw_data[:-1]).split("1st Floor")[0].strip()
        city = raw_data[-1][: raw_data[-1].find(",")].strip()
        state = raw_data[-1][
            raw_data[-1].find(",") + 1 : raw_data[-1].rfind(" ")
        ].strip()
        zip_code = (
            raw_data[-1].replace("</a>", "")[raw_data[-1].rfind(" ") + 1 :].strip()
        )
        country_code = "US"
        store_number = "<MISSING>"
        phone = item.findAll("p")[1].text.strip()
        location_type = "<MISSING>"

        hours_of_operation = (
            (
                item.find("div", attrs={"class": "hours"})
                .text.replace("\xa0", " ")
                .replace("pmF", "pm F")
                .replace("pmS", "pm S")
            )
            .split("Open for")[0]
            .strip()
        )
        hours_of_operation = re.sub(" +", " ", hours_of_operation)

        latitude = lats[i].split(":")[1]
        longitude = lngs[i].split(":")[1]

        link = base_link + item.find("a", string="More Info")["href"]

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


with SgWriter(SgRecordDeduper(RecommendedRecordIds.PhoneNumberId)) as writer:
    fetch_data(writer)
