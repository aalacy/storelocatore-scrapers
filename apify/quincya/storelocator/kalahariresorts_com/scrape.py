from bs4 import BeautifulSoup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests


def fetch_data(sgw: SgWriter):

    base_link = "https://www.kalahariresorts.com"

    user_agent = (
        "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0"
    )
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    items = base.find_all(class_="home-location col-section")
    locator_domain = "kalahariresorts.com"

    for item in items:
        link = base_link + item.a["href"]
        contact_link = link + "more-info/contact-us/"
        direct_link = link + "more-info/directions/"

        req = session.get(contact_link, headers=headers)
        base = BeautifulSoup(req.text, "lxml")

        location_name = item.h2.text.strip()

        raw_address = list(base.find(id="footer").p.stripped_strings)
        street_address = raw_address[0]
        city = raw_address[1].split(",")[0]
        state = raw_address[1].split(",")[1].split()[0]
        try:
            zip_code = raw_address[1].split(",")[1].split()[1]
        except:
            zip_code = ""
            if "Pocono" in city:
                zip_code = "18349"

        try:
            phone = (
                base.find_all(class_="umb-block-list umb-block-list--columns")[1]
                .find_all("li")[1]
                .text.replace("Local Direct", "")
                .replace("Local", "")
            )
        except:
            phone = (
                base.find_all(class_="umb-block-list umb-block-list--columns")[1]
                .find_all("p")[1]
                .text.replace("Local Direct", "")
                .replace("Local", "")
            )

        country_code = "US"
        store_number = "<MISSING>"
        location_type = "<MISSING>"
        hours_of_operation = "<MISSING>"

        direct_link = link + "more-info/directions/"
        req = session.get(direct_link, headers=headers)
        base = BeautifulSoup(req.text, "lxml")

        try:
            map_link = base.iframe["src"]
            lat_pos = map_link.rfind("!3d")
            latitude = map_link[lat_pos + 3 : map_link.find("!", lat_pos + 5)].strip()
            lng_pos = map_link.find("!2d")
            longitude = map_link[lng_pos + 3 : map_link.find("!", lng_pos + 5)].strip()
        except:
            latitude = "<MISSING>"
            longitude = "<MISSING>"

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
