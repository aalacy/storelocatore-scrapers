from bs4 import BeautifulSoup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests


def fetch_data(sgw: SgWriter):

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"
    headers = {"User-Agent": user_agent}

    base_link = "https://copperbranch.fr/commander-votre-repas-vegetal/"

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    locator_domain = "https://copperbranch.fr"

    items = base.find_all("h2")

    for i in items:

        if i.text.split()[0].isupper():
            item = i.find_previous(
                class_="elementor-widget-wrap elementor-element-populated"
            )
        else:
            continue

        location_name = item.h2.text.replace("\n", " ").strip()

        raw_address = list(
            item.h2.find_next(class_="elementor-widget-container").stripped_strings
        )
        for r, row in enumerate(raw_address):
            if "email" in row:
                raw_address.pop(r)

        street_address = " ".join(raw_address[:-2]).strip()
        city_line = raw_address[-2].split()
        phone = raw_address[-1].strip()
        if not street_address:
            street_address = raw_address[0]
            city_line = raw_address[1].split()
            phone = ""
        street_address = (
            street_address.replace("Shopping Coeur Alsace,", "")
            .replace("CC La Part Dieu,", "")
            .replace("Adresse :", "")
            .strip()
        )
        if street_address[-1:] == ",":
            street_address = street_address[:-1]
        city = city_line[1]
        state = ""
        zip_code = city_line[0]
        country_code = "France"
        if "UTRECHT" in location_name:
            country_code = "Netherlands"
        store_number = item.div["data-id"]
        location_type = "<MISSING>"
        hours_of_operation = ""
        latitude = ""
        longitude = ""

        if "Steenweg 37" in street_address:
            street_address = "Steenweg 37"
            city = ""
            state = ""
            zip_code = ""
            phone = ""
            hours_of_operation = " ".join(list(item.find_all("p")[-1].stripped_strings))

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


with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
    fetch_data(writer)
