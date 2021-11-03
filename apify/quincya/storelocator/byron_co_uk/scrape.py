from bs4 import BeautifulSoup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests


def fetch_data(sgw: SgWriter):

    base_link = "https://www.byron.co.uk/locations"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    items = base.find_all(class_="Locations-item")
    locator_domain = "byron.co.uk"

    for item in items:
        location_name = item.h2.text.strip()
        link = item.find(class_="Locations-itemLink")["href"]

        raw_address = list(item.find(class_="Address-physical").stripped_strings)

        zip_code = raw_address[-1].split()[-1]
        if len(zip_code) < 5:
            zip_code = " ".join(raw_address[-1].split()[-2:])
        addr_text = " ".join(raw_address)
        addr_text = addr_text[: addr_text.rfind(zip_code)].strip()
        city = addr_text.split()[-1]
        street_address = addr_text[: addr_text.rfind(city)].strip()

        if city == "Edmunds":
            city = "Bury St Edmunds"
            street_address = street_address.replace("Bury St", "").strip()

        if city == "Keynes":
            city = "Milton Keynes"
            street_address = street_address.replace("Milton", "").strip()

        if street_address[-1:] == ",":
            street_address = street_address[:-1].strip()
        if " " not in zip_code:
            street_address = street_address + " " + city
            city = zip_code
            zip_code = "<MISSING>"

        if "Road" in zip_code:
            street_address = street_address + " " + city + " " + zip_code
            city = location_name.split("-")[0].strip()
            zip_code = "<MISSING>"
        if city == "Mall" or ":" in city:
            street_address = street_address + " " + city
            city = location_name.split("-")[0].strip()

        city = city.replace(",", "")
        state = "<MISSING>"
        store_number = "<MISSING>"
        country_code = "GB"
        location_type = "<MISSING>"

        try:
            phone = item.find(class_="Address-phone").text.strip()
        except:
            phone = "<MISSING>"

        if "locations" in link:
            req = session.get(link, headers=headers)
            base = BeautifulSoup(req.text, "lxml")
            hours_of_operation = " ".join(
                list(base.find(class_="OpeningHours").ul.stripped_strings)
            )
        else:
            link = base_link
            hours_of_operation = "<MISSING>"

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


with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))) as writer:
    fetch_data(writer)
