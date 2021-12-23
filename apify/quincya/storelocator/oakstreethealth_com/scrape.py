import re

from bs4 import BeautifulSoup

from sglogging import SgLogSetup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests

logger = SgLogSetup().get_logger("oakstreethealth_com")


def fetch_data(sgw: SgWriter):

    base_link = "https://www.oakstreethealth.com/locations/all"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    locator_domain = "oakstreethealth.com"

    states = base.find(class_="footer-nav-item__subnav-inner").find_all("a")
    for i in states:
        main_link = i["href"]
        for y in range(1, 10):
            state_link = main_link + "/p" + str(y)
            logger.info(state_link)
            req = session.get(state_link, headers=headers)
            main_base = BeautifulSoup(req.text, "lxml")

            items = main_base.find(class_="space-y-8").find_all("li")
            for item in items:
                if "coming soon" in item.text.lower():
                    continue

                raw_address = list(
                    item.find_all(class_="text-base")[-1].stripped_strings
                )
                street_address = raw_address[0].strip()
                city_line = raw_address[-1].strip().split(",")
                city = city_line[0].strip()
                state = city_line[-1].strip().split()[0].strip()
                zip_code = city_line[-1].strip().split()[1].strip()
                country_code = "US"
                store_number = "<MISSING>"

                link = item.a["href"]
                logger.info(link)

                req = session.get(link, headers=headers)
                base = BeautifulSoup(req.text, "lxml")

                location_name = base.h1.text.strip()
                try:
                    if (
                        "coming soon"
                        in base.find(class_="relative image-label").text.lower()
                    ):
                        continue
                except:
                    pass

                try:
                    zip_code = (
                        base.find("a", string="Get Directions")
                        .find_previous("div")
                        .text.split()[-1]
                    )
                except:
                    zip_code = (
                        base.find("a", string="Get directions")
                        .find_previous("div")
                        .text.split()[-1]
                    )

                if len(zip_code) == 4:
                    zip_code = "0" + zip_code

                try:
                    raw_types = base.find(id="services").find_all(
                        class_="feature-block w-full flex flex-col space-y-6"
                    )
                    location_type = ""
                    for raw_type in raw_types:
                        location_type = (
                            location_type + "," + list(raw_type.stripped_strings)[0]
                        )
                    location_type = location_type[1:].strip()
                except:
                    location_type = "<MISSING>"

                phone = base.find(class_="flex-1 tabular-nums").text.strip()
                try:
                    hours_of_operation = " ".join(
                        list(
                            base.find_all(class_="flex items-start")[
                                -1
                            ].stripped_strings
                        )
                    )
                    if "day" not in hours_of_operation.lower():
                        hours_of_operation = "<MISSING>"
                except:
                    hours_of_operation = "<MISSING>"

                try:
                    latitude = re.findall(r'latitude":"[0-9]{2}\.[0-9]+', str(base))[
                        0
                    ].split(":")[1][1:]
                    longitude = re.findall(
                        r'longitude":"-[0-9]{2,3}\.[0-9]+', str(base)
                    )[0].split(":")[1][1:]
                except:
                    latitude = "<MISSING>"
                    longitude = "<MISSING>"
                if street_address == "2240 East 53rd St":
                    latitude = "39.849198"
                    longitude = "-86.12594"
                if "8923 Flatlands" in street_address:
                    latitude = "40.6401617"
                    longitude = "-73.908619"
                if "1249 Nostrand" in street_address:
                    latitude = "40.6567175"
                    longitude = "-73.9519989"

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

            if not main_base.find(class_="ml-5"):
                break


with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
    fetch_data(writer)
