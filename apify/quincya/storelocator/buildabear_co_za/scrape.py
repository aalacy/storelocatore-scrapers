import re

from bs4 import BeautifulSoup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgpostal.sgpostal import parse_address_intl

from sgrequests import SgRequests


def fetch_data(sgw: SgWriter):

    base_link = "https://www.buildabear.co.za/our-stores/"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    items = base.find(class_="col-inner text-center").find_all(class_="button alert")
    locator_domain = "https://www.buildabear.co.za"

    for item in items:
        link = locator_domain + item["href"]

        try:
            req = session.get(link, headers=headers)
            base = BeautifulSoup(req.text, "lxml")
        except:
            continue

        stores = base.find_all(class_="panel")
        for store in stores:
            location_name = store.h3.text
            raw_address = " ".join(list(store.p.stripped_strings)[:-2])
            addr = parse_address_intl(raw_address)
            street_address = addr.street_address_1.replace("  ", " ")
            if addr.street_address_2:
                street_address = (
                    addr.street_address_1 + " " + addr.street_address_2
                ).strip()
            city = addr.city
            state = addr.state
            zip_code = addr.postcode
            if len(street_address) < 60:
                if city:
                    street_address = (
                        raw_address[: raw_address.rfind(city)]
                        .replace(zip_code, "")
                        .strip()
                    )
                else:
                    street_address = raw_address
                    if zip_code:
                        street_address = street_address.replace(zip_code, "").strip()
                    else:
                        if street_address.split()[-1].isdigit():
                            zip_code = street_address.split()[-1]
                            street_address = street_address.replace(
                                zip_code, ""
                            ).strip()
            if not city:
                if "Waterfall City" in street_address:
                    city = "Waterfall City"
                    street_address = street_address[
                        street_address.find("Waterfall City") + len(city) :
                    ].strip()
            if street_address[-1:] == ",":
                street_address = street_address[:-1]

            if "Boksburg" in street_address:
                city = "Boksburg"

            country_code = "ZA"
            store_number = ""
            location_type = "<MISSING>"
            phone = list(store.p.stripped_strings)[-2]
            hours_of_operation = (
                " ".join(list(store.find(class_="row").stripped_strings))
                .split("Public")[0]
                .strip()
            )
            geo = (
                re.findall(r"-[0-9]{2}\.[0-9]+, [0-9]{2,3}\.[0-9]+", str(store))[0]
                .replace("[", "")
                .replace("]", "")
                .split(",")
            )
            latitude = geo[0].strip()
            longitude = geo[1].strip()

            final_link = locator_domain + req.url.path + "#" + store["id"]

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
                    raw_address=raw_address,
                )
            )


with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
    fetch_data(writer)
