from bs4 import BeautifulSoup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests


def fetch_data(sgw: SgWriter):

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"
    headers = {"User-Agent": user_agent}

    base_link = "https://www.muvfitness.com/locations/"

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    stores = base.find_all(class_="location")

    locator_domain = "https://www.muvfitness.com/"

    for store in stores:
        street_address = store.find(itemprop="streetAddress")["content"].strip()
        city = store.find(itemprop="addressLocality")["content"].strip()
        state = store.find(itemprop="addressRegion")["content"].strip()
        zip_code = store.find(itemprop="postalCode")["content"].strip()
        country_code = "US"
        location_type = "<MISSING>"
        store_number = "<MISSING>"
        phone = store.find(class_="phone").text.strip()
        link = (
            "https://www.muvfitness.com"
            + store.find(class_="website")["href"].split("?")[0]
        )

        req = session.get(link, headers=headers)
        base = BeautifulSoup(req.text, "lxml")

        location_name = base.find(class_="h-spacer").strong.text
        hours_of_operation = (
            " ".join(list(base.find(class_="gym-hours").stripped_strings))
            .split("Hours")[1]
            .strip()
        )
        if "mon" not in hours_of_operation.lower():
            hours_of_operation = "<MISSING>"

        map_link = base.iframe["src"]
        lat_pos = map_link.rfind("!3d")
        latitude = map_link[lat_pos + 3 : map_link.find("!", lat_pos + 5)].strip()
        lng_pos = map_link.find("!2d")
        longitude = map_link[lng_pos + 3 : map_link.find("!", lng_pos + 5)].strip()

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
