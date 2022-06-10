import re

from bs4 import BeautifulSoup

from sglogging import SgLogSetup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests

logger = SgLogSetup().get_logger("johnnywas_com")


def fetch_data(sgw: SgWriter):

    session = SgRequests()

    base_link = "https://www.johnnywas.com/store_locator/location/searchLocations?&type=by_radius&current_page=cms_page_view&current_products=&search_text=&radius=0&autocomplete%5Blat%5D=&autocomplete%5Blng%5D=&autocomplete%5Bsmall_city%5D=&autocomplete%5Bcity%5D=&autocomplete%5Bregion%5D=&autocomplete%5Bpostcode%5D=&autocomplete%5Bcountry_id%5D="

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    items = base.find_all("a", string="Store Page")
    locator_domain = "johnnywas.com"

    for item in items:
        link = item["href"]

        logger.info(link)
        req = session.get(link, headers=headers)
        base = BeautifulSoup(req.text, "lxml")

        location_name = base.h2.text.strip()

        raw_data = list(
            base.find(
                class_="mw-sl__details__item mw-sl__details__item--location"
            ).stripped_strings
        )

        street_address = " ".join(raw_data[0].split(",")[:-1]).strip()
        street_address = (re.sub(" +", " ", street_address)).strip()

        city = raw_data[0].split(",")[-1].strip()
        state = raw_data[1].split(",")[0].strip().replace("Washington", "WA")
        zip_code = raw_data[1].split(",")[1].strip().split()[0]
        if len(zip_code) == 4:
            zip_code = "0" + zip_code
        country_code = "US"
        store_number = "<MISSING>"
        location_type = "<MISSING>"

        try:
            phone = base.find(
                class_="mw-sl__details__item mw-sl__details__item--tel"
            ).text.strip()
        except:
            if "OPENING" in base.find(class_="description").text.upper():
                continue
            phone = "<MISSING>"

        hours_of_operation = (
            base.find(class_="mw-sl__infotable__table").text.replace("\n", " ").strip()
        )
        hours_of_operation = (re.sub(" +", " ", hours_of_operation)).strip()

        fin_script = ""
        all_scripts = base.find_all("script")
        for script in all_scripts:
            if "var location" in str(script):
                fin_script = str(script)
                break
        try:
            geo = re.findall(
                r"lat: [0-9]{2}\.[0-9]+, lng:.+[0-9]{2,3}\.[0-9]+", fin_script
            )[0].split(",")
            latitude = geo[0].split(":")[1].strip()
            longitude = geo[1].split(":")[1].strip()
            if "-" not in longitude:
                longitude = "-" + longitude
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
