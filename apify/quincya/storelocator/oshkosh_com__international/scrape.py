import re
import os

from bs4 import BeautifulSoup

from sglogging import SgLogSetup

from sgpostal.sgpostal import parse_address_intl

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests

logger = SgLogSetup().get_logger("oshkosh.com")


def fetch_data(sgw: SgWriter):

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"

    headers = {"User-Agent": user_agent}

    session = SgRequests()

    proxy_password = os.environ["PROXY_PASSWORD"]
    proxy_url = "http://auto:{}@proxy.apify.com:8000/".format(proxy_password)
    proxies = {"http": proxy_url, "https": proxy_url}
    session.proxies = proxies

    base_link = "https://www.oshkosh.com/on/demandware.store/Sites-Carters-Site/default/Stores-International"
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    locator_domain = "https://www.oshkosh.com"

    countries = base.find(id="country").find_all("option")[1:]
    num = 1
    for i in countries:
        country_code = i["value"]
        final_link = (
            locator_domain
            + "/on/demandware.store/Sites-Carters-Site/default/Stores-InternationalStores?countryCd="
            + country_code
            + "&id=oshkosh"
        )

        if num % 15 == 0:
            session = SgRequests()
            session.proxies = proxies
        num = num + 1

        logger.info(final_link)
        final_req = session.get(final_link, headers=headers)
        base = BeautifulSoup(final_req.text, "lxml")

        items = base.find_all(class_="storeTile")
        if len(items) == 0:
            if "No store found" in base.text:
                continue
            else:
                raise
        for item in items:
            raw_data = list(item.stripped_strings)
            location_name = raw_data[0].strip()
            if raw_data[-1][-1:].isdigit():
                raw_address = " ".join(raw_data[1:-1])
                city_line = raw_data[-2]
            else:
                raw_address = " ".join(raw_data[1:])
                city_line = raw_data[-1]
            addr = parse_address_intl(raw_address.replace("PQ H7N 0A8", "QC H7N 0A8"))
            try:
                street_address = addr.street_address_1 + " " + addr.street_address_2
            except:
                street_address = addr.street_address_1
            city = addr.city
            state = addr.state
            zip_code = addr.postcode
            location_type = ""
            phone = item.find_all("p")[-1].text.strip()
            try:
                if not phone[1].isdigit():
                    phone = ""
            except:
                phone = ""
            try:
                zip_code = zip_code.replace(phone, "").split("250-3")[0].strip()
            except:
                pass
            try:
                street_address = street_address.replace(phone, "").strip()
            except:
                pass

            if not street_address:
                try:
                    street_address = raw_data[1].strip()
                except:
                    street_address = ""

            try:
                if street_address in phone:
                    street_address = raw_data[1].strip()
            except:
                pass

            if street_address.replace(" ", "").isdigit():
                street_address = raw_data[1].strip()

            try:
                if phone in street_address:
                    street_address.replace(phone, "").strip()
            except:
                pass

            try:
                if phone in state:
                    state.replace(phone, "").strip()
            except:
                pass

            try:
                state = state.replace("Qc Qc", "QC")
            except:
                pass

            if location_name == "@":
                location_name = ""

            if len(street_address) < 10:
                try:
                    street_address = raw_data[1].strip()
                except:
                    pass

            if city == "St.":
                if "ST. MICHAEL" in raw_address:
                    city = "ST. MICHAEL".title()

            if not city and country_code == "ES":
                if raw_address.split()[-1].isupper():
                    city = raw_address.split()[-1]
                    if raw_address.split()[-2].isupper():
                        city = raw_address.split()[-2] + " " + city

                    try:
                        if city.lower() in street_address[-20:].lower():
                            city = street_address.lower()[
                                street_address.lower().rfind(city.lower()) :
                            ].title()
                    except:
                        pass
                if "Dubai" in street_address:
                    city = "Dubai"
                    street_address = street_address[
                        : street_address.rfind("Dubai")
                    ].strip()

            try:
                if len(state) < 4:
                    state = state.upper()
                if len(state) == 1:
                    state = ""
                if state == "Melbourne":
                    city = "Melbourne"
                    state = "VIC"
            except:
                pass

            if not state and country_code == "AU":
                try:
                    state = re.findall(r"[A-Z]{2,3}", city_line)[0]
                except:
                    pass
                street_address = street_address.replace("Nt 800", "")

            try:
                if len(city) == 1:
                    city = ""
            except:
                pass

            if not city:
                if "Dubai" in street_address:
                    city = "Dubai"
                    street_address = street_address.replace("Point. Dubai", "Point")
                if "Moscow" in street_address:
                    city = "Moscow"
                    street_address = street_address.replace("Moscow 21", "21")
                if "Istanbul Istanbul" in street_address:
                    city = "Istanbul"
                    street_address = street_address.split("/")[0].strip()

            if street_address == city:
                street_address = ""

            if len(street_address.split()) == 1 and not city:
                if street_address == raw_address:
                    street_address = ""
                    if state:
                        if raw_address != state:
                            city = raw_address
                    else:
                        city = raw_address

            store_number = ""
            latitude = ""
            longitude = ""
            hours_of_operation = ""

            sgw.write_row(
                SgRecord(
                    locator_domain=locator_domain,
                    page_url="https://www.oshkosh.com/on/demandware.store/Sites-Carters-Site/default/Stores-International",
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


with SgWriter(
    SgRecordDeduper(
        SgRecordID({SgRecord.Headers.LOCATION_NAME, SgRecord.Headers.STREET_ADDRESS})
    )
) as writer:
    fetch_data(writer)
