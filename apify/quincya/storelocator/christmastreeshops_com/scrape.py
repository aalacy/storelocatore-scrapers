import re

from bs4 import BeautifulSoup

from sgrequests import SgRequests

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    base_link = "https://stores.christmastreeshops.com/"

    url = "https://stores.christmastreeshops.com/index.html"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"
    HEADERS = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(url, headers=HEADERS)
    base = BeautifulSoup(req.text, "lxml")

    final_links = []
    main_links = []

    main_items = base.find_all(class_="Directory-listLink")
    for main_item in main_items:
        main_link = base_link + main_item["href"]
        if "/" in main_item["href"]:
            final_links.append(main_link)
        else:
            main_links.append(main_link)

    for next_link in main_links:
        req = session.get(next_link, headers=HEADERS)
        base = BeautifulSoup(req.text, "lxml")

        next_items = base.find_all(class_="Directory-listItem")
        for next_item in next_items:
            link = base_link + next_item.find(class_="Directory-listLink")["href"]
            final_links.append(link)

    for final_link in final_links:
        final_req = session.get(final_link, headers=HEADERS)
        item = BeautifulSoup(final_req.text, "lxml")

        locator_domain = "christmastreeshops.com"

        location_name = item.find(class_="LocationName").text.split(",")[0].strip()

        street_address = (
            item.find(class_="c-address-street-1").text.replace("\u200b", "").strip()
        )
        try:
            street_address = (
                street_address
                + " "
                + item.find(class_="Core-address")
                .find(class_="c-address-street-2")
                .text.replace("\u200b", "")
                .strip()
            )
            street_address = street_address.strip()
        except:
            pass
        street_address = street_address.replace("  ", " ").strip()

        city = item.find(class_="c-address-city").text.strip()
        state = item.find(class_="c-address-state").text.strip()
        zip_code = item.find(class_="c-address-postal-code").text.strip()
        country_code = "US"
        store_number = "<MISSING>"
        location_type = "<MISSING>"

        try:
            phone = item.find(id="phone-main").text.strip()
        except:
            phone = "<MISSING>"

        latitude = item.find("meta", attrs={"itemprop": "latitude"})["content"]
        longitude = item.find("meta", attrs={"itemprop": "longitude"})["content"]

        hours_of_operation = ""
        raw_hours = item.find(class_="c-hours-details")
        raw_hours = raw_hours.find_all("td")

        hours = ""
        hours_of_operation = ""

        try:
            for hour in raw_hours:
                hours = hours + " " + hour.text.strip()
            hours_of_operation = (re.sub(" +", " ", hours)).strip()
        except:
            pass
        if not hours_of_operation:
            hours_of_operation = "<MISSING>"

        sgw.write_row(
            SgRecord(
                locator_domain=locator_domain,
                page_url=final_link,
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
