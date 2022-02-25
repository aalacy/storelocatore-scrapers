from bs4 import BeautifulSoup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests


def fetch_data(sgw: SgWriter):

    base_link = "https://www.kalahariresorts.com/"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    items = base.find_all(class_="blockPromo")
    locator_domain = "kalahariresorts.com"

    for item in items:

        if "bonus" in item["href"] or "holiday" in item["href"]:
            continue

        if "Texas" in item.text:
            link = "https://www.kalahariresorts.com/texas/more-info/kalahari-location/"
            link2 = "https://www.kalahariresorts.com/texas/more-info/contact-us/"
        else:
            link = (
                "https://www.kalahariresorts.com"
                + item["href"]
                + "help/directions-maps-and-hours/"
            )
            link2 = (
                "https://www.kalahariresorts.com" + item["href"] + "help/contact-us/"
            )
        req = session.get(link, headers=headers)
        req2 = session.get(link2, headers=headers)

        base = BeautifulSoup(req.text, "lxml")
        base2 = BeautifulSoup(req2.text, "lxml")

        try:
            phone = (
                base2.find(class_="accordion-open")
                .find_all("p")[1]
                .text.replace("Local", "")
                .replace("Direct", "")
                .strip()
            )
        except:
            continue

        location_name = item.text.strip()

        street_address = base.find(
            class_="footer-primary-container-section-info-address-street"
        ).text.strip()
        city_line = (
            base.find(class_="footer-primary-container-section-info-address-cityState")
            .text.strip()
            .split(",")
        )
        city = city_line[0].strip()
        state = city_line[1].strip()
        zip_code = base.find(
            class_="footer-primary-container-section-info-address-zip"
        ).text.strip()
        country_code = "US"
        store_number = "<MISSING>"
        location_type = "<MISSING>"
        hours_of_operation = "<MISSING>"

        try:
            map_link = base.find(class_="site").iframe["src"]
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
