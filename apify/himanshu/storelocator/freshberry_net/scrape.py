import re

from sgpostal.sgpostal import parse_address_intl

from sgrequests import SgRequests

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

from bs4 import BeautifulSoup

session = SgRequests()


def fetch_data(sgw: SgWriter):

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    # it will used in store data
    locator_domain = "http://freshberry.net/"
    page_url = "<MISSING>"
    location_name = ""
    street_address = "<MISSING>"
    city = "<MISSING>"
    state = "<MISSING>"
    zipp = "<MISSING>"
    country_code = "US"
    store_number = "<MISSING>"
    phone = "<MISSING>"
    location_type = "<MISSING>"
    latitude = "<MISSING>"
    longitude = "<MISSING>"
    raw_address = ""
    hours_of_operation = "<MISSING>"

    r = session.get("http://freshberry.net/locations.html", headers=headers)
    soup = BeautifulSoup(r.text, "lxml")

    for store in soup.find("div", {"id": "interiormain"}).find_all("ul")[:-4]:
        for details in store.find_all("li"):
            list_store = list(details.stripped_strings)
            if len(list_store) == 4:
                location_name = list_store[0].strip()
                street_address = list_store[1].strip()
                city = list_store[2].split(",")[0].strip()
                state = list_store[2].split(",")[1].split()[0].strip()
                zipp = list_store[2].split(",")[1].split()[-1].strip()
                phone = list_store[-1].split()[-1].strip()
                hours_of_operation = "<MISSING>"

            elif len(list_store) == 7:
                if "Miami" == list_store[0]:
                    location_name = ",".join(list_store[:2]).strip()
                    street_address = list_store[2].strip()
                    city = list_store[3].split(",")[0].strip()
                    state = list_store[3].split(",")[-1].split()[0].strip()
                    zipp = list_store[3].split(",")[-1].split()[-1].strip()
                    phone = re.findall(
                        re.compile(r".?(\(?\d{3}\D{0,3}\d{3}\D{0,3}\d{4}).?"),
                        str(list_store[4]),
                    )[0]
                    hours_of_operation = list_store[-1].strip()

                else:
                    location_name = list_store[0].strip()
                    street_address = list_store[1].strip()
                    city = list_store[2].split(",")[0].strip()
                    state = list_store[2].split(",")[-1].split()[0].strip()
                    zipp = list_store[2].split(",")[-1].split()[-1].strip()
                    phone = re.findall(
                        re.compile(r".?(\(?\d{3}\D{0,3}\d{3}\D{0,3}\d{4}).?"),
                        str(list_store[3]),
                    )[0]
                    hours_of_operation = " ".join(list_store[-2:]).strip()

            elif len(list_store) == 8:
                if "Wilmington" == list_store[0]:
                    location_name = ",".join(list_store[:2]).strip()
                    street_address = list_store[2].strip()
                    city = list_store[3].split(",")[0].strip()
                    phone = re.findall(
                        re.compile(r".?(\(?\d{3}\D{0,3}\d{3}\D{0,3}\d{4}).?"),
                        str(list_store[4]),
                    )[0]
                    hours_of_operation = (
                        " ".join(list_store[6:]).strip().replace("&", "and")
                    )
                    if len(list_store[3].split(",")[-1].split()) > 2:
                        state = " ".join(
                            list_store[3].split(",")[-1].split()[:2]
                        ).strip()
                        zipp = list_store[3].split(",")[-1].split()[-1].strip()

                    else:
                        state = " ".join(list_store[3].split(",")[-1].split()).strip()
                        zipp = "<MISSING>"

                else:
                    location_name = list_store[0].strip()
                    street_address = list_store[1].strip()
                    city = list_store[2].split(",")[0].strip()
                    state = " ".join(list_store[2].split(",")[-1].split()[:-1]).strip()
                    zipp = list_store[2].split(",")[-1].split()[-1].strip()
                    phone = re.findall(
                        re.compile(r".?(\(?\d{3}\D{0,3}\d{3}\D{0,3}\d{4}).?"),
                        str(list_store[3]),
                    )[0]
                    hours_of_operation = " ".join(list_store[5:]).strip()

            else:
                location_name = ",".join(list_store[:2]).strip()
                street_address = list_store[2].strip()
                city = list_store[3].split(",")[0].strip()
                state = list_store[3].split(",")[-1].split()[0].strip()
                zipp = list_store[3].split(",")[-1].split()[-1].strip()
                phone = re.findall(
                    re.compile(r".?(\(?\d{3}\D{0,3}\d{3}\D{0,3}\d{4}).?"),
                    str(list_store[4]),
                )[0]
                hours_of_operation = " ".join(list_store[6:]).strip().replace("â", "")

            sgw.write_row(
                SgRecord(
                    locator_domain=locator_domain,
                    page_url=page_url,
                    location_name=location_name,
                    street_address=street_address,
                    city=city,
                    state=state,
                    zip_postal=zipp,
                    country_code=country_code,
                    store_number=store_number,
                    phone=phone,
                    location_type=location_type,
                    latitude=latitude,
                    longitude=longitude,
                    hours_of_operation=hours_of_operation,
                )
            )

    for store in soup.find("div", {"id": "interiormain"}).find_all("ul")[-4:]:
        if "COMING SOON" in str(store).upper():
            continue
        for details in store.find_all("li"):
            country_code = details.find_previous("a")["name"]
            list_store = list(details.stripped_strings)
            location_name = list_store[0]

            raw_address = " ".join(list(details.stripped_strings))
            addr = parse_address_intl(raw_address)
            street_address = addr.street_address_1.replace("Ksa", "").strip()
            city = addr.city
            state = addr.state
            zipp = addr.postcode
            hours_of_operation = ""
            phone = ""
            for i in list_store:
                if " # " in i:
                    phone = i.split("#")[1].strip()
                    if phone.split()[-1] in street_address:
                        street_address = street_address.split(phone.split()[-1])[
                            1
                        ].strip()
                    break
            if "Riyadh" in street_address or "Riyadh" in location_name:
                city = "Riyadh"
                street_address = street_address.replace(city, "").strip()
            if "Jeddah" in street_address:
                city = "Jeddah"
                street_address = street_address.replace(city, "").strip()
            if "Dammam" in street_address:
                city = "Dammam"
                street_address = street_address.replace(" Dammam", "")
            if "Jubail" in street_address:
                city = "Jubail"
            if "Locations" in street_address:
                street_address = ""
            if "#" in street_address:
                city = location_name
                street_address = list_store[1]
            if "locations" in location_name.lower():
                location_name = city

            if not city and len(location_name.split()) == 1:
                city = location_name
            if street_address == city:
                street_address = ""

            try:
                if zipp in phone:
                    zipp = ""
            except:
                pass

            city = city.replace("Ksa", "").strip()

            sgw.write_row(
                SgRecord(
                    locator_domain=locator_domain,
                    page_url=page_url,
                    location_name=location_name,
                    street_address=street_address,
                    city=city,
                    state=state,
                    zip_postal=zipp,
                    country_code=country_code,
                    store_number=store_number,
                    phone=phone,
                    location_type=location_type,
                    latitude=latitude,
                    longitude=longitude,
                    hours_of_operation=hours_of_operation,
                )
            )


with SgWriter(
    SgRecordDeduper(
        SgRecordID({SgRecord.Headers.STREET_ADDRESS, SgRecord.Headers.LOCATION_NAME})
    )
) as writer:
    fetch_data(writer)
