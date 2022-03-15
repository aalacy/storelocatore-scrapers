import json
import re

from bs4 import BeautifulSoup

from sglogging import sglog

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests

log = sglog.SgLogSetup().get_logger(logger_name="realdeals.net")


def fetch_data(sgw: SgWriter):

    base_link = "https://realdeals.net/find-a-store/"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    fin_script = ""
    all_scripts = base.find_all("script")
    for script in all_scripts:
        if "var markLatLng" in str(script):
            fin_script = str(script)
            break

    all_links = re.findall(r"http://realdeals.net/[a-z]+", fin_script)

    locator_domain = "realdeals.net"

    for i, link in enumerate(all_links):
        log.info(link)
        req = session.get(link, headers=headers)
        base = BeautifulSoup(req.text, "lxml")

        latitude = ""
        longitude = ""

        try:
            raw_data = (
                base.find(id="front-address")
                .find(id="text-4")
                .text.replace("Get Directions", "")
                .replace(", Canada |", "")
                .replace("Canada", "")
                .replace("Ankeny", " | Ankeny")
                .replace("Dr Cedar", "Dr | Cedar")
                .replace("Street, ", "Street | ")
                .replace("\r\n", " | ")
                .replace("| 307)", "| (307)")
                .replace("St, Spanish", "St | Spanish")
                .replace("Kearney, Nebraska", "Kearney | Nebraska")
                .replace(" B,", " B |")
                .replace(" C,", " C |")
                .replace("NW Rochester", "NW | Rochester")
                .replace(" 1, ", " 1 | ")
                .replace("102 Powell", "102 | Powell")
                .replace("Ave Butte", "Ave | Butte")
                .replace("Ave La", "Ave | La")
                .replace("V1Y-9T1", "V1Y 9T1")
                .replace("Dr Cedar", "Dr | Cedar")
                .strip()
                .split("|")
            )
            location_name = base.h3.text.strip()
            if location_name.upper() == "REGINA REAL DEALS":
                location_name = "Regina, Saskatchewan"
            phone = raw_data[2].strip()
            if not phone:
                phone = "<MISSING>"
            hours_of_operation = (
                base.find(id="front-hours")
                .div.text.replace("\r\n", " ")
                .replace("\n", " ")
                .replace("–", "-")
                .replace("Shop Online!", "")
            )
            if not hours_of_operation:
                hours_of_operation = (
                    base.find(id="front-hours")
                    .find_all("div")[1]
                    .text.replace("\r\n", " ")
                    .replace("\n", " ")
                    .replace("–", "-")
                    .replace("Shop Online!", "")
                )
            hours_of_operation = (re.sub(" +", " ", hours_of_operation)).strip()
            store = json.loads(base.find(id="wpgmza_map")["data-settings"])
            latitude = store["map_start_lat"]
            longitude = store["map_start_lng"]
        except:
            try:
                raw_data = (
                    base.find_all("h4")[1]
                    .text.replace("\xa0", "")
                    .replace("St.Elko", "St.\nElko")
                    .split("\n")
                )
                if "Kristen & Warren" not in raw_data[0]:
                    map_link = base.find(
                        class_="fusion-button button-flat fusion-button-round button-large button-default button-1"
                    )["href"]
                    at_pos = map_link.rfind("@")
                    latitude = map_link[at_pos + 1 : map_link.find(",", at_pos)].strip()
                    longitude = map_link[
                        map_link.find(",", at_pos) + 1 : map_link.find(",", at_pos + 15)
                    ].strip()
                else:
                    raw_data = (
                        base.h4.text.replace("\xa0", "")
                        .replace("St.Elko", "St.\nElko")
                        .split("\n")
                    )
                location_name = base.h2.text.strip()
                try:
                    phone = re.findall(r"[(\d)]{3}-[\d]{3}-[\d]{4}", str(base))[0]
                except:
                    phone = "<MISSING>"
                hours_of_operation = base.h4.text.replace("\n", " ").strip()
            except:
                try:
                    raw_data = (
                        base.find_all(class_="fusion-text")[4]
                        .p.text.replace("\xa0", "")
                        .split("\n")
                    )
                    location_name = base.h1.text.strip()
                    phone = (
                        base.find_all(class_="fusion-text")[5]
                        .p.a.text.replace("\n", " ")
                        .strip()
                    )
                    hours_of_operation = (
                        base.find_all(class_="fusion-text")[3]
                        .text.replace("\n", " ")
                        .strip()
                    )
                    script = base.text
                    lat_pos = script.find("latitude") + 11
                    latitude = script[lat_pos : script.find(",", lat_pos) - 1]
                    long_pos = script.find("longitude") + 12
                    longitude = script[long_pos : script.find(",", long_pos) - 3]
                except:
                    try:
                        raw_data = (
                            base.h3.find_next("h3")
                            .find_next("h4")
                            .text.replace("\xa0", "")
                            .split("\n")
                        )
                        location_name = base.h2.text.strip()
                        hours_of_operation = ""
                        rows = list(base.h3.find_previous("div").stripped_strings)[1:]
                        for raw_hour in rows:
                            if "LOCATION" not in raw_hour.upper():
                                hours_of_operation = (
                                    hours_of_operation + " " + raw_hour
                                ).strip()
                            else:
                                break
                        if "PHONE" in rows[-2].upper():
                            phone = rows[-1]
                        else:
                            try:
                                phone = re.findall(
                                    r"[(\d)]{3}-[\d]{3}-[\d]{4}", str(base)
                                )[0]
                            except:
                                phone = "<MISSING>"
                    except:
                        raise
        try:
            geo = re.findall(
                r'[0-9]{2}\.[0-9]+","longitude":"-[0-9]{2,3}\.[0-9]+',
                str(base),
            )[0]
            latitude = geo.split('"')[0]
            longitude = geo.split('"')[-1]
        except:
            pass

        if longitude == "240.594345":
            longitude = "-119.405655"

        street_address = (
            raw_data[0].replace("Cedar Falls, IA", "").replace("Kearney", "").strip()
        )
        city = location_name.split(",")[0].strip()
        state = location_name.split(",")[1].strip()
        location_name = "Real Deals on Home Decor - " + location_name
        zip_code = raw_data[1][-7:].strip()
        if "Suite" in zip_code:
            street_address = street_address + " " + zip_code
            zip_code = raw_data[2][-7:].strip()
        country_code = "US"
        if "," in zip_code or zip_code == "ter VA":
            zip_code = "<MISSING>"
        if " " in zip_code:
            if zip_code[-5:].isnumeric():
                zip_code = zip_code[-5:]
            else:
                zip_code = raw_data[1][-8:].strip()
                country_code = "CA"
        if not zip_code:
            zip_code = "<MISSING>"
        if zip_code == "T6A OH9":
            zip_code = "T5H 2T2"
        if "126 Windy Hill Lane" in street_address:
            zip_code = "22602"
        if "532 Main Street" in street_address:
            zip_code = "83467"
        if "3479 N Hwy 126" in street_address:
            latitude = "41.3222502"
            longitude = "-112.03147530000001"
        location_type = "<MISSING>"
        store_number = "<MISSING>"
        hours_of_operation = (
            hours_of_operation.replace("SHOP ONLINE!", "")
            .replace("!", "")
            .replace("HOURS:", "")
            .replace("Hours", "")
            .replace("SHOP ONLINE", "")
            .strip()
        )

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
