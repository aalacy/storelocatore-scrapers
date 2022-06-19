import re
from bs4 import BeautifulSoup

from sglogging import SgLogSetup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests

logger = SgLogSetup().get_logger("lemacaron-us_com")


def fetch_data(sgw: SgWriter):

    base_link = "https://lemacaron-us.com/locations"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")
    items = base.find(class_="et_pb_row et_pb_row_2").find_all("p")

    locator_domain = "lemacaron-us.com"

    for item in items:
        if "coming" in str(item).lower():
            continue
        link = item.a["href"]
        logger.info(link)
        req = session.get(link, headers=headers)
        base = BeautifulSoup(req.text, "lxml")

        location_name = base.h2.text + " " + base.find_all("h2")[1].text
        try:
            if (
                "COMING SOON" in location_name.upper()
                or "COMING SOON" in base.find(class_="text-fade px-2 mb-2").text.upper()
            ):
                continue
        except:
            pass

        if "Contact" in location_name:
            location_name = (
                base.strong.text.replace("Welcome to", "").replace("!", "").strip()
            )

        try:
            raw_address = list(base.find(class_="text-fade px-2 mb-2").stripped_strings)
        except:
            try:
                raw_address = list(
                    base.find(class_="w-wrapper location-details").p.stripped_strings
                )[1:]
            except:
                raw_address = list(base.p.stripped_strings)
        if not raw_address:
            continue
        try:
            num = re.search(r"\d+", raw_address[0]).group()
        except:
            raw_address.pop(0)

        try:
            street_address = raw_address[0].split(". 2200")[0].strip()
            city = raw_address[1].strip().split(",")[0].strip()

            try:
                state = raw_address[1].strip().split(",")[1].strip().split()[0]
            except:
                state = ""
            try:
                zip_code = raw_address[1].strip().split(",")[1].strip().split()[1]
            except:
                zip_code = ""
        except:
            if len(raw_address) == 1:
                raw_address = raw_address[0].split(",")
                street_address = raw_address[0]
                city = raw_address[-2].strip()
                state = ""
                if "Texas" in street_address:
                    state = "TX"
                zip_code = raw_address[-1].strip()

        if "Suite 120" in city:
            street_address = street_address + " Suite 120"
            city = city.replace("Suite 120", "").strip()
        street_address = (
            street_address.replace("Mayfair mall", "")
            .replace("Westfield Century", "")
            .strip()
        )
        if "Mayfair mall" in city:
            city = "Wauwatosa"
            zip_code = "53226"
        city = city.replace("We3st", "West")
        if state.isdigit():
            zip_code = state
            state = ""
        if city == "Jacksonville":
            state = "FL"
        if "NM" in zip_code:
            zip_code = zip_code.replace("NM", "").strip()
            state = "NM"
        if "STE" in city:
            street_address = street_address + " " + city
        if "10250 Santa" in street_address:
            city = "Los Angeles"
            state = "CA"
            zip_code = "90067"
        if "GA" in city:
            state = city.split()[0]
            zip_code = city.split()[1]
            city = ""

        country_code = "US"
        store_number = "<MISSING>"
        location_type = "<MISSING>"
        try:
            phone = base.find("a", {"href": re.compile(r"tel:")}).text.replace(" ", "")
        except:
            try:
                phone = (
                    base.find(
                        class_="et_pb_button et_pb_button_2 et_pb_bg_layout_light"
                    )
                    .text.replace("Phone", "")
                    .strip()
                )
            except:
                phone = ""
        if "coming" in phone.lower():
            phone = "<MISSING>"

        try:
            map_str = base.find(
                class_="et_pb_button et_pb_button_4 et_pb_bg_layout_light"
            )["href"]
            geo = re.findall(r"[0-9]{2}\.[0-9]+,-[0-9]{2,3}\.[0-9]+", str(map_str))[
                0
            ].split(",")
            latitude = geo[0]
            longitude = geo[1]
        except:
            latitude = "<MISSING>"
            longitude = "<MISSING>"

        try:
            hours_of_operation = (
                base.find(class_="text-fade px-2 mb-3")
                .get_text(" ")
                .split("(")[0]
                .strip()
            )
        except:
            hours_of_operation = ""
            try:
                if "Temporarily Closed" in base.h3.text:
                    hours_of_operation = "Temporarily Closed"
            except:
                pass
            try:
                if (
                    "day"
                    in base.find(class_="text-fade px-2 mb-2")
                    .find_next("p")
                    .get_text(" ")
                    or "pm"
                    in base.find(class_="text-fade px-2 mb-2")
                    .find_next("p")
                    .get_text(" ")
                    .lower()
                ):
                    hours_of_operation = (
                        base.find(class_="text-fade px-2 mb-2")
                        .find_next("p")
                        .get_text(" ")
                    )
            except:
                pass
        if not hours_of_operation:
            try:
                if "day" in base.find_all(class_="w-wrapper")[1].text.strip():
                    hours_of_operation = (
                        base.find_all(class_="w-wrapper")[1].get_text(" ").strip()
                    )
                    try:
                        if (
                            "day"
                            in base.find_all(class_="w-wrapper")[2]
                            .get_text(" ")
                            .strip()
                        ):
                            hours_of_operation = (
                                hours_of_operation
                                + " "
                                + base.find_all(class_="w-wrapper")[2]
                                .get_text(" ")
                                .strip()
                            )
                    except:
                        pass
            except:
                pass

        if "click" in hours_of_operation.lower():
            hours_of_operation = ""

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
