from bs4 import BeautifulSoup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests


def fetch_data(sgw: SgWriter):

    base_link = "https://www.thecomfycow.com/contact-us/"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    maps = base.findAll("div", attrs={"class": "map-marker"})
    items = base.find_all(class_="col span_12 left")[1].find_all("p")

    for i, item in enumerate(items):
        locator_domain = "thecomfycow.com"
        try:
            location_name = item.find("span").text.strip()
        except:
            continue
        if "coming soon" in location_name.lower():
            continue

        if (
            "cardinal towne" in location_name.lower()
            or "paddock shops" in location_name.lower()
        ):
            item = items[i + 1]

        raw_data = list(item.stripped_strings)

        street_address = raw_data[-2][: raw_data[-2].find(",")].strip()
        city = raw_data[-2][
            raw_data[-2].find(",") + 1 : raw_data[-2].rfind(",")
        ].strip()
        if not city:
            street_address = raw_data[0]
            city = raw_data[1].split(",")[0].strip()
        state = raw_data[-2][
            raw_data[-2].rfind(",") + 1 : raw_data[-2].rfind(" ")
        ].strip()
        zip_code = raw_data[-2][raw_data[-2].rfind(" ") + 1 :].strip()
        country_code = "US"
        store_number = "<MISSING>"
        phone = raw_data[-1].strip()
        location_type = "<MISSING>"

        latitude = ""
        longitude = ""
        for mp in maps:
            if location_name[5:10] in str(mp):
                latitude = mp["data-lat"]
                longitude = mp["data-lng"]
                try:
                    int(latitude[4:8])
                except:
                    latitude = "<MISSING>"
                    longitude = "<MISSING>"

        hours_of_operation = "<MISSING>"

        sgw.write_row(
            SgRecord(
                locator_domain=locator_domain,
                page_url=base_link,
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
