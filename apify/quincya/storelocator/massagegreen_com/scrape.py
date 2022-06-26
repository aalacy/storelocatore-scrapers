from bs4 import BeautifulSoup
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests


def fetch_data(sgw: SgWriter):

    base_link = "https://massagegreenspa.com/locations/?SPA=Locations"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    items = base.find(class_="row cl_row-sortable").find_all("a")
    locs = base.find_all(class_="pum-content popmake-content")
    locator_domain = "massagegreenspa.com"

    for item in items:
        link = item["href"].replace("amp;", "")
        if len(link) < 10:
            link = base_link

        found = False
        if "SPA=Locations" in link:
            city = item.text
            for loc in locs:
                try:
                    city_line = loc.find_all("h4")[1].text.split(",")
                except:
                    continue
                if city in str(city_line).replace("Twp", "Township"):
                    found = True
                    street_address = loc.h4.text
                    phone = list(loc.stripped_strings)[2]
                    hours_of_operation = ""
                    break
            if not found:
                continue
        else:
            req = session.get(link, headers=headers)
            base = BeautifulSoup(req.text, "lxml")

            raw_address = list(base.find(class_="footer-widget").stripped_strings)
            if len(raw_address) == 2:
                raw_address = raw_address[0].split("  ")
            street_address = raw_address[0].strip()
            city_line = raw_address[1].strip().split(",")
            phone = base.find(string="Call Now:").find_next().text.strip()
            hours_of_operation = base.find(string="SPA Hours:").find_next().text.strip()

        city = city_line[0].replace("Twp", "Township").strip()
        state = city_line[-1].strip().split()[0].strip()
        zip_code = city_line[-1].strip().split()[1].strip()
        location_name = "Massage Green SPA - " + item.text
        location_type = ""
        country_code = "US"
        store_number = ""
        latitude = ""
        longitude = ""

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
