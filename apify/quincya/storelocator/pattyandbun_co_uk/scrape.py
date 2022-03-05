import re
from bs4 import BeautifulSoup

from sgrequests import SgRequests

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    base_link = "https://www.pattyandbun.co.uk/locations"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    items = base.find_all(class_="collection-item-23")
    locator_domain = "pattyandbun.co.uk"

    for item in items:
        if "coming soon" in item.text.lower():
            continue

        link = "https://www.pattyandbun.co.uk" + item.a["href"]
        req = session.get(link, headers=headers)
        base = BeautifulSoup(req.text, "lxml")

        location_name = base.find(class_="heading-93").text.strip()

        street_address = base.find(id="address").text.replace("Swingers", "").strip()
        city_line = base.find(class_="heading-41").text.strip().split(" ")
        zip_code = " ".join(city_line[-2:]).strip()
        city = " ".join(city_line[:-2]).strip()
        if "," in city:
            street_address = street_address + " " + city.split(",")[0]
            city = city.split(",")[1].strip()
        if not city_line[0]:
            raw_address = base.find(id="address").text.split(",")
            street_address = raw_address[0].replace("Swingers", "").strip()
            city_line = raw_address[1].strip()
            zip_code = " ".join(city_line.split()[-2:]).strip()
            city = " ".join(city_line.split()[:-2]).strip()

        state = "<MISSING>"
        country_code = "GB"
        store_number = "<MISSING>"
        location_type = "<MISSING>"

        try:
            phone = base.find(class_="rich-text-block-6 w-richtext").a.text.strip()
            if "@" in phone:
                phone = (
                    base.find(class_="rich-text-block-6 w-richtext")
                    .find_all("a")[1]
                    .text.strip()
                )
        except:
            phone = "<MISSING>"

        hours_of_operation = (
            base.find(class_="rich-text-block-3 w-richtext")
            .text.replace("day", "day ")
            .replace("am", "am ")
            .replace("pm", "pm ")
            .replace("PM", "PM ")
            .replace("â\x80\x93", "")
            .replace("â\x80\x8d", "")
            .strip()
        )
        if "*" in hours_of_operation:
            hours_of_operation = hours_of_operation[
                : hours_of_operation.find("*")
            ].strip()
        if "We" in hours_of_operation:
            hours_of_operation = hours_of_operation[
                : hours_of_operation.find("We")
            ].strip()
        if "Please" in hours_of_operation:
            hours_of_operation = hours_of_operation[
                : hours_of_operation.find("Please")
            ].strip()

        hours_of_operation = (re.sub(" +", " ", hours_of_operation)).strip()

        if "closed for now" in base.text:
            hours_of_operation = "Temporarily Closed"

        try:
            map_link = base.find(class_="button-23 w-button")["href"]
            at_pos = map_link.rfind("!3d")
            latitude = map_link[at_pos + 3 : map_link.rfind("!")].strip()
            longitude = map_link[map_link.find("!4d", at_pos) + 3 :].strip()
            if len(latitude) > 30:
                latitude = map_link[map_link.find("=") + 1 : map_link.find(",")].strip()
                longitude = map_link[
                    map_link.find(",") + 1 : map_link.find("&")
                ].strip()
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
