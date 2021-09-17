import json
import re
from bs4 import BeautifulSoup
from sglogging import SgLogSetup
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

logger = SgLogSetup().get_logger("pokeworks_com")


def fetch_data(sgw: SgWriter):
    global p
    locator_domain = "https://www.pokeworks.com/"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(locator_domain, headers=headers)
    base = BeautifulSoup(req.text, "html.parser")

    link_list = []

    a_tags = base.find(id="preFooter").find_all(class_="row sqs-row")[1].find_all("a")
    for a in a_tags:
        try:
            link_list.append(a["href"])
        except:
            continue

    for link in link_list:
        logger.info(link)
        req = session.get(link, headers=headers)
        base = BeautifulSoup(req.text, "html.parser")

        try:
            map_json_string = base.find(class_="sqs-block map-block sqs-block-map")[
                "data-block-json"
            ]
        except:
            try:
                map_json_string = base.find(class_="col sqs-col-6 span-6").div[
                    "data-block-json"
                ]
            except:
                continue
        map_json = json.loads(map_json_string)["location"]

        location_name = map_json["addressTitle"]
        lat = map_json["markerLat"]
        longit = map_json["markerLng"]
        street_address = map_json["addressLine1"]
        city_line = map_json["addressLine2"].replace(".", ",").split(",")
        city = city_line[0].title()
        if "8041 Walnut Hill" in street_address:
            state = "TX"
            zip_code = "75231"
        else:
            try:
                state = city_line[1].replace("\xa0", " ").upper().strip()
            except:
                state = "<MISSING>"
            if state.isdigit():
                zip_code = state
                state = "<MISSING>"
            elif " " in state:
                zip_code = state.split()[1].strip()
                state = state.split()[0].strip()
            else:
                try:
                    zip_code = city_line[2].strip()
                except:
                    zip_code = "<MISSING>"
        if city == "Laguna Niguel":
            state = "CA"
        if zip_code == "V6E":
            zip_code = "V6E 2E9"

        country_code = map_json["addressCountry"]
        if "MEX" in country_code.upper():
            continue
        if link == "http://www.pokeworks.com/san-luis-2":
            street_address = "C. Palmira 1070"
            zip_code = "78295"
            city = "San Luis"
        if link == "http://www.pokeworks.com/leon":
            street_address = "Eugenio Garza Sada 1109-local 8 Cumbres del Campestre"
            zip_code = "37128"
            city = "León"
        content = base.find(class_="main-content")

        try:
            phone = re.findall(r"[(\d)]{5}.[\d]{3}-[\d]{4}", str(content))[0]
        except:
            phone = "<MISSING>"

        if "temporarily closed" in str(content).lower():
            hours_of_operation = "Temporarily Closed"
        else:
            ps = content.find_all("p")
            hours_of_operation = "<MISSING>"
            for p in ps:
                if "pm" in str(p).lower():
                    hours_of_operation = (
                        " ".join(list(p.stripped_strings))
                        .replace("Store Hours:", "")
                        .replace("Store Hours", "")
                        .replace("-Takeout & Delivery only-", "")
                        .replace("- Takeout & Delivery only- ", "")
                        .replace("-Pickup & Delivery only-", "")
                        .replace("STORE HOURS", "")
                        .replace("Temporary Hours:", "")
                        .strip()
                    )
                    break
            if "pm" not in str(p).lower():
                if "0pm" in content.span.text:
                    hours_of_operation = (
                        " ".join(list(content.span.stripped_strings))
                        .replace("Store Hours:", "")
                        .replace("Store Hours", "")
                        .replace("-Takeout & Delivery only-", "")
                        .replace("- Takeout & Delivery only- ", "")
                        .replace("-Pickup & Delivery only-", "")
                        .replace("STORE HOURS", "")
                        .replace("Temporary Hours:", "")
                        .strip()
                    )

        if "STORE INFO" in hours_of_operation:
            hours_of_operation = hours_of_operation.split("  ")[-1].strip()

        hours_of_operation = (
            hours_of_operation.split("Limited")[0].replace("﻿﻿ ", "").strip()
        )
        if hours_of_operation.find(f"{phone}") != -1:
            hours_of_operation = hours_of_operation.split(f"{phone}")[1].strip()

        row = SgRecord(
            locator_domain=locator_domain,
            page_url=link,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=zip_code,
            country_code=country_code,
            store_number=SgRecord.MISSING,
            phone=phone,
            location_type=SgRecord.MISSING,
            latitude=lat,
            longitude=longit,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)
