from bs4 import BeautifulSoup

from sgrequests import SgRequests

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    session = SgRequests()

    base_link = "https://www.mydrdental.com/locations/"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    req = session.get(base_link, headers=headers)

    base = BeautifulSoup(req.text, "lxml")
    items = base.findAll("div", attrs={"class": "address"})

    for item in items:
        locator_domain = "mydrdental.com"
        location_name = item.find("h3").text.strip()
        raw_data = list(item.find_all("p")[-1].stripped_strings)

        if len(raw_data) == 2:
            street_address = raw_data[0].strip()
            zip_code = raw_data[1][raw_data[1].rfind(" ") + 1 :].strip()
            state = raw_data[1][
                raw_data[1].rfind(" ") - 2 : raw_data[1].rfind(" ")
            ].strip()
            city = raw_data[1][: raw_data[1].find(state)].replace(",", "").strip()
        else:
            street_address = base.find("span", attrs={"itemprop": "streetAddress"}).text
            city = base.find("span", attrs={"itemprop": "addressLocality"}).text
            state = base.find("span", attrs={"itemprop": "addressRegion"}).text
            zip_code = base.find("span", attrs={"itemprop": "postalCode"}).text

        if "Lyndhurst" in city:
            city = "Lyndhurst"
            state = "NJ"

        country_code = "US"
        phone = list(item.stripped_strings)[-1]
        link = item.a["href"]
        store_number = "<MISSING>"
        location_type = "<MISSING>"

        req = session.get(link, headers=headers)

        new_base = BeautifulSoup(req.text, "lxml")
        gps_link = new_base.find("a", attrs={"class": "directions"})["href"]
        latitude = gps_link[gps_link.find("=") + 1 : gps_link.find(",")].strip()
        longitude = gps_link[gps_link.find(",") + 1 :].strip()

        raw_hours = list(
            new_base.find("span", class_="elementor-icon-list-text")
            .find_next("section")
            .stripped_strings
        )
        days = raw_hours[:7]
        hours = raw_hours[7:]

        hours_of_operation = ""
        for i, day in enumerate(days):
            hours_of_operation = (
                hours_of_operation + " " + day + " " + hours[i]
            ).strip()

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
