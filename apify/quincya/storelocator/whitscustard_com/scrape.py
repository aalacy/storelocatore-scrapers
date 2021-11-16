import re
import ssl

from bs4 import BeautifulSoup

from sglogging import SgLogSetup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests

from sgselenium import SgChrome

try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification

logger = SgLogSetup().get_logger("whitscustard_com")


def fetch_data(sgw: SgWriter):

    base_link = "https://whitscustard.com/findyourwhits"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    main_links = []
    items = base.find(class_="sqs-gallery").find_all("a")
    for i in items:
        main_link = "https://whitscustard.com" + i["href"]
        if "opening-soon" not in main_link:
            main_links.append(main_link)

    final_links = []
    for main_link in main_links:
        if "ohio" not in main_link:
            req = session.get(main_link, headers=headers)
            base = BeautifulSoup(req.text, "lxml")
        else:
            driver = SgChrome().driver()
            driver.get(main_link)
            base = BeautifulSoup(driver.page_source, "lxml")
            driver.close()
        items = base.find_all(class_="summary-title-link")
        for i in items:
            if "Opening%2Bsoon" not in str(i):
                final_links.append("https://whitscustard.com" + i["href"])

    locator_domain = "whitscustard.com"

    for link in final_links:
        logger.info(link)
        req = session.get(link, headers=headers)
        base = BeautifulSoup(req.text, "lxml")

        if "Opening%2Bsoon" in str(base) or "Coming Soon Website Little" in str(base):
            continue
        location_name = base.find(class_="entry-title").text.strip()

        raw_address = (
            str(base.address)
            .replace("<address>", "")
            .replace("</address>", "")
            .replace("SUITE 101,", "SUITE 101<br/>")
            .replace("HWY HENDER", "HWY<br/>HENDER")
            .replace("#43, Welling", "#43<br/>Welling")
            .replace("\nSUITE", " SUITE")
            .replace("\nSuite", " SUITE")
            .replace("RD.\n", "RD. ")
            .replace("WEST, \n", "WEST, ")
            .split("<br/>")
        )

        street_address = raw_address[0].strip()
        if street_address == "None" or not street_address:
            try:
                raw_address = list(base.find(id="address").stripped_strings)
            except:
                try:
                    raw_address = list(base.find(class_="pslAddress").stripped_strings)
                    if "\n" in raw_address[0]:
                        raw_address = (
                            raw_address[0].replace("\n", "<br/>").split("<br/>")
                        )
                except:
                    raw_address = base.h3.text.replace("NUE ZAN", "NUE<br/>ZAN").split(
                        "<br/>"
                    )
            street_address = " ".join(raw_address[:-1]).strip()
        if "\n" in street_address:
            raw_address = base.address.text.strip().split("\n")
            street_address = " ".join(raw_address[:-1]).strip()
        city_line = raw_address[-1].strip().split(",")
        if len(city_line) == 2:
            city = city_line[0]
            state = city_line[1].split()[0]
            zip_code = city_line[1].split()[1]
        elif len(city_line) == 3:
            city = city_line[0]
            state = city_line[1].strip()
            zip_code = city_line[2].strip()
        elif len(city_line) == 1:
            city_line = city_line[0].split()
            city = city_line[0]
            state = city_line[1]
            zip_code = city_line[2]
        elif "ORANGE PARK" in location_name:
            street_address = "10 Blanding Blvd, Ste A"
            city = "Orange Park"
            state = "FL"
            zip_code = "32073"
        else:
            raise

        if street_address[-1:] == ",":
            street_address = street_address[:-1]

        country_code = "US"
        store_number = "<MISSING>"
        location_type = "<MISSING>"

        try:
            phone = (
                base.find("a", {"href": re.compile(r"tel")})["href"]
                .replace("tel:", "")
                .replace("telto:", "")
                .strip()
            )
        except:
            phone = "<MISSING>"
        if not phone:
            phone = "<MISSING>"

        try:
            hours_of_operation = base.find_all(class_="col sqs-col-3 span-3")[
                -1
            ].text.replace("Hours", "")
        except:
            hours_of_operation = base.h2.find_next("p").text

        hours_of_operation = (
            hours_of_operation.replace("PM", "PM ")
            .replace("Drive-thru only", "")
            .replace("losed", "losed ")
            .replace("LOSED", "LOSED ")
            .replace("HOURS", "")
            .strip()
        )

        if "holiday hours" in hours_of_operation:
            hours_of_operation = hours_of_operation.split("holiday hours")[1].strip()
        hours_of_operation = hours_of_operation.split("(")[0].split("Due to")[0].strip()
        hours_of_operation = (re.sub(" +", " ", hours_of_operation)).strip()

        if not hours_of_operation:
            hours_of_operation = "<MISSING>"

        if "Drive through only" in hours_of_operation:
            hours_of_operation = hours_of_operation.replace("Drive through only", "")
            location_type = "Drive Through Only"

        map_link = ""
        maps = base.find_all("a")
        for i in maps:
            if "Directions" in i.text:
                map_link = i["href"].strip()
                break
        if map_link:
            req = session.get(map_link, headers=headers)
            maps = BeautifulSoup(req.text, "lxml")
            try:
                raw_gps = maps.find("meta", attrs={"itemprop": "image"})["content"]
                latitude = raw_gps[raw_gps.find("=") + 1 : raw_gps.find("%")].strip()
                longitude = raw_gps[raw_gps.find("-") : raw_gps.find("&")].strip()
            except:
                latitude = "<MISSING>"
                longitude = "<MISSING>"
        else:
            latitude = "<MISSING>"
            longitude = "<MISSING>"

        if len(latitude) > 20:
            old_lat = latitude
            latitude = old_lat.split("=")[-1].split(",")[0]
            longitude = old_lat.split("=")[-1].split(",")[1]
        if "11362 SAN JOSE BLVD" in street_address.upper():
            latitude = "30.1677275"
            longitude = "-81.6349426"
        if "200 NE 2nd Avenue" in street_address:
            latitude = "26.4661678"
            longitude = "-80.0735354"
        if not longitude or not latitude[:2].isdigit():
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
