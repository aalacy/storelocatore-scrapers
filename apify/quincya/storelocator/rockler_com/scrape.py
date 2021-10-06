import json

from bs4 import BeautifulSoup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests


def fetch_data(sgw: SgWriter):

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    base_link = "https://storemapper-herokuapp-com.global.ssl.fastly.net/api/users/10216/stores.js?callback=SMcallback2"

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    js = base.text.split('ores":')[1].split("})")[0]
    stores = json.loads(js)

    found = []
    locator_domain = "rockler.com"

    for store in stores:
        link = store["url"].lower()
        if "missouri-store" in link:
            link = "https://www.rockler.com/retail/stores/mo/st-louis-missouri-hardware-store"
        if link in found:
            continue
        found.append(link)

        if "rockler.com/retail/stores/" in link and "retail-partner" not in link:
            location_name = store["name"]
            raw_address = (
                store["address"]
                .replace("Street Olathe", "Street, Olathe")
                .replace("200C Round", "200C, Round")
                .split(",")
            )
            street_address = raw_address[0]
            city = raw_address[1].strip()
            state = raw_address[2].strip().split()[0]
            try:
                zip_code = raw_address[-1].strip().split()[1]
            except:
                zip_code = raw_address[-1].strip()
            if "Frisco" in state:
                street_address = street_address + " " + city
                city = "Frisco"
                state = "TX"

            phone = store["phone"]
            country_code = "US"
            store_number = store["id"]
            latitude = store["latitude"]
            longitude = store["longitude"]
            location_type = "<MISSING>"

            try:
                req = session.get(link, headers=headers)
                base = BeautifulSoup(req.text, "lxml")

                if not phone:
                    phone = list(base.find(class_="col-m-6").stripped_strings)[4]
                try:
                    hours_of_operation = " ".join(
                        list(
                            base.find(class_="col-m-6")
                            .find_all(class_="sect")[-1]
                            .stripped_strings
                        )
                    )
                except:
                    try:
                        hours_of_operation = " ".join(
                            list(
                                base.find(class_="row sect")
                                .find_all(class_="sect")[-1]
                                .stripped_strings
                            )
                        )
                    except:
                        hours_of_operation = " ".join(
                            list(
                                base.find_all(class_="row sect")[1]
                                .find_all(class_="sect")[-1]
                                .stripped_strings
                            )
                        )
            except:
                hours_of_operation = "<MISSING>"
                if "Opening in Early" in base.text:
                    continue
                if req.status_code == 404:
                    link = "https://www.rockler.com/retail/stores/"
            hours_of_operation = (
                hours_of_operation.replace("Store Hours", "")
                .split("Holiday")[0]
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


with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
    fetch_data(writer)
