from bs4 import BeautifulSoup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests


def fetch_data(sgw: SgWriter):

    session = SgRequests()

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    base_link = "https://planetbeachcanada.com/location-contact/"

    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    items = base.find_all("h3", class_="heading-title")

    for i in items:

        locator_domain = "planetbeachcanada.com"
        location_name = i.span.text.replace("\xa0", " ").strip()
        if "a spa" in location_name.lower():
            continue

        item = i.find_previous(class_="fl-col")

        raw_address = list(item.p.stripped_strings)
        street_address = raw_address[0]
        city_line = raw_address[-1].strip().split(",")
        city = city_line[0].strip()
        state = city_line[1].strip().split()[0]
        zip_code = " ".join(city_line[1].strip().split()[1:])
        country_code = "CA"
        phone = item.find_all("a")[1].text.strip()
        location_type = "<MISSING>"
        hours_of_operation = (
            item.find_all("p")[-1]
            .get_text()
            .replace("\n", " ")
            .replace("PMF", "PM F")
            .replace("PMS", "PM S")
            .split("Stat")[0]
            .strip()
        )
        if not hours_of_operation:
            hours_of_operation = (
                item.find_all("p")[-2]
                .get_text()
                .replace("\n", " ")
                .replace("PMF", "PM F")
                .replace("PMS", "PM S")
                .split("Stat")[0]
                .strip()
            )
        try:
            map_link = item.iframe["src"]
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
                page_url=base_link,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zip_code,
                country_code=country_code,
                store_number="",
                phone=phone,
                location_type=location_type,
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=hours_of_operation,
            )
        )


with SgWriter(SgRecordDeduper(RecommendedRecordIds.PhoneNumberId)) as writer:
    fetch_data(writer)
