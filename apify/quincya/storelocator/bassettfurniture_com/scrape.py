import json
import re

from bs4 import BeautifulSoup

from sglogging import SgLogSetup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests

logger = SgLogSetup().get_logger("bassettfurniture.com")


def remove_comments(string):
    pattern = r"(\".*?\"|\'.*?\')|(/\*.*?\*/|//[^\r\n]*$)"
    # first group captures quoted strings (double or single)
    # second group captures comments (//single-line or /* multi-line */)
    regex = re.compile(pattern, re.MULTILINE | re.DOTALL)

    def _replacer(match):
        # if the 2nd group (capturing comments) is not None,
        # it means we have captured a non-quoted (real) comment string.
        if match.group(2) is not None:
            return ""  # so we will return empty to remove the comment
        else:  # otherwise, we will return the 1st group
            return match.group(1)  # captured quoted-string

    return regex.sub(_replacer, string)


def fetch_data(sgw: SgWriter):

    base_link = "https://stores.bassettfurniture.com/"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    final_links = []

    main_items = base.find(class_="stateContainer").ul.find_all("a")
    for main_item in main_items:
        main_link = main_item["href"]

        logger.info(main_link)
        req = session.get(main_link, headers=headers)
        base = BeautifulSoup(req.text, "lxml")

        next_items = base.find_all(class_="itemList")
        for next_item in next_items:
            next_link = next_item["href"]
            next_req = session.get(next_link, headers=headers)
            next_base = BeautifulSoup(next_req.text, "lxml")

            final_items = next_base.find_all("a", string="More Info")
            for final_item in final_items:
                final_link = final_item["href"]
                final_links.append(final_link)

    for link in final_links:
        logger.info(link)
        final_req = session.get(link, headers=headers)
        base = BeautifulSoup(final_req.text, "lxml")

        locator_domain = "bassettfurniture.com"

        script = (
            base.find_all("script", attrs={"type": "application/ld+json"})[-1]
            .contents[0]
            .strip()
        )
        js = remove_comments(script)
        store = json.loads(js)

        location_name = store["name"]
        street_address = store["address"]["streetAddress"]
        city = store["address"]["addressLocality"]
        state = store["address"]["addressRegion"]
        zip_code = store["address"]["postalCode"]
        country_code = store["address"]["addressCountry"]

        store_number = store["@id"]
        location_type = "<MISSING>"
        phone = store["telephone"]

        hours_of_operation = ""
        raw_hours = store["openingHoursSpecification"]
        for hours in raw_hours:
            day = hours["dayOfWeek"]
            if len(day[0]) != 1:
                day = " ".join(hours["dayOfWeek"])
            opens = hours["opens"]
            closes = hours["closes"]
            if opens != "" and closes != "":
                clean_hours = day + " " + opens + "-" + closes
                hours_of_operation = (hours_of_operation + " " + clean_hours).strip()

        latitude = store["geo"]["latitude"]
        longitude = store["geo"]["longitude"]

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
