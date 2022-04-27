from bs4 import BeautifulSoup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests


def fetch_data(sgw: SgWriter):

    base_link = "https://plazaazteca.com/locations/"
    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"

    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    items = base.find_all(class_="elementor-heading-title")

    locator_domain = "https://plazaazteca.com"

    for item in items:
        try:
            link = item.a["href"]
        except:
            continue

        req = session.get(link, headers=headers)
        base = BeautifulSoup(req.text, "lxml")

        location_name = item.text.strip()
        try:
            raw_address = base.find_all(class_="elementor-text-editor")[-1].find_all(
                "p"
            )
            street_address = raw_address[0].text.strip()
            city_line = raw_address[1].text.split(",")
            city = city_line[0].strip()
            state = city_line[1].strip()
            if not state.isdigit():
                zip_code = city_line[2].strip()
            else:
                zip_code = state
                state = city
                city = street_address.split(",")[1].strip()
                street_address = street_address.split(",")[0].strip()
            phone = raw_address[-1].text.strip()
            if "," in phone:
                phone = list(item.a.find_next().stripped_strings)[-1].strip()
        except:
            raw_address = list(item.a.find_next().stripped_strings)
            street_address = raw_address[0].strip()
            city_line = raw_address[1].strip().split(",")
            city = city_line[0].strip()
            state = city_line[1].strip()
            zip_code = city_line[2].strip()
            phone = raw_address[-1].strip()
        if street_address[-1:] == ",":
            street_address = street_address[:-1]
        if "York" in state:
            city = "York"
            state = state.replace("York", "").strip()
        country_code = "US"
        store_number = ""
        location_type = ""
        phone = phone.split("·")[0].strip()
        if "TEMPORARY CLOSED" in location_name.upper():
            hours_of_operation = "TEMPORARY CLOSED".title()
            phone = ""
        else:
            try:
                hours_of_operation = " ".join(
                    list(
                        base.find(class_="elementor-icon-box-wrapper")
                        .find_previous(class_="elementor-widget-wrap")
                        .stripped_strings
                    )
                )
            except:
                try:
                    hours_of_operation = " ".join(
                        list(
                            base.find(class_="hours-of-operation").div.stripped_strings
                        )
                    )
                except:
                    hours_of_operation = ""
        if "," in phone:
            phone = (
                base.find_all(class_="elementor-text-editor")[-1]
                .find_all("p")[-1]
                .text.strip()
            )
        hours_of_operation = hours_of_operation.replace(
            " (Late night menu available - Bar open late 1am)", ""
        )
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


with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
    fetch_data(writer)
