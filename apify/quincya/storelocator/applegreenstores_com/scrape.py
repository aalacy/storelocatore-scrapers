from bs4 import BeautifulSoup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests

from sgpostal.sgpostal import parse_address_intl


def remove_dups(raw_address):
    l = raw_address.split(", ")
    k = []
    for i in l:
        if raw_address.count(i.strip()) >= 1 and (i.strip() not in k):
            k.append(i.strip())
    return ", ".join(k)


def fetch_data(sgw: SgWriter):

    base_links = [
        "https://api.applegreenstores.com/v1/locations?geolat=52.7384&geolng=-4.4647335&limit=400&radius=600&country=GB",
        "https://api.applegreenstores.com/v1/locations?geolat=53.573399&geolng=-7.775527&limit=1200&radius=600",
        "https://www.applegreenstores.com/us/locations/",
    ]

    api_link = "https://api.applegreenstores.com/v1/locations/"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests(verify_ssl=False)

    locator_domain = "https://www.applegreenstores.com/"

    for base_link in base_links:
        if "/us/" not in base_link:
            link = "https://www.applegreenstores.com/locations/"
            stores = session.get(base_link, headers=headers).json()["items"]
            if "GB" in base_link:
                country_code = "GB"
            elif "geolat=53" in base_link:
                country_code = "Ireland"
            for i in stores:
                store_id = i["id"]
                if "applegreen" not in i["name"].lower() and i["competitor"]:
                    continue
                store = session.get(api_link + store_id, headers=headers).json()["item"]
                location_name = store["name"].replace(",", "")
                raw_address = store["address"].replace("\r\n", " ")
                if len(raw_address) < 6:
                    continue
                clean_add = remove_dups(raw_address)
                addr = parse_address_intl(clean_add)

                street_address = addr.street_address_1
                city = addr.city
                state = addr.state
                zip_code = addr.postcode
                country = addr.country

                if country:
                    country_code = country

                if zip_code:
                    zip_code = zip_code.replace("ANTRIM", "").strip()

                phone = store["phone"]
                store_number = store["id"]
                location_type = ""
                latitude = store["geolat"]
                longitude = store["geolng"]
                hours_of_operation = ""

                if country_code == "Ireland":
                    if state and len(state) == 3:
                        zip_code = state + " " + zip_code
                        state = ""
                    elif not state:
                        zc = " ".join(raw_address.split()[-2:])
                        if zc.isupper() or len(zc.replace(" ", "")) == 7:
                            zip_code = zc
                    try:
                        if state[-1:].isdigit():
                            state = ""
                    except:
                        pass

                    if not street_address:
                        street_address = raw_address
                    if len(street_address) < 5:
                        street_address = raw_address

                    if zip_code:
                        street_address = (
                            street_address.replace(zip_code, "")
                            .replace("  ", " ")
                            .strip()
                        )
                        if zip_code.split()[0] in street_address:
                            street_address = street_address.split(zip_code.split()[0])[
                                0
                            ].strip()
                        try:
                            if zip_code.split()[0] in city:
                                city = ""
                        except:
                            pass
                    else:
                        zip_code = ""

                    if not street_address:
                        street_address = raw_address.replace(zip_code, "").strip()

                    street_address = (
                        street_address.replace("H16", "")
                        .split(", Ballaghad")[0]
                        .strip()
                    )

                    try:
                        if "." in zip_code:
                            zip_code = ""
                    except:
                        pass

                    try:
                        if "Killarney" in street_address:
                            city = "Killarney"
                        city = city.replace("N71", "")
                    except:
                        pass

                    if "N71, N71" in raw_address:
                        street_address = raw_address
                    if "H16 FK15" in raw_address:
                        zip_code = "H16 FK15"
                        city = ""

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
                        raw_address=raw_address,
                    )
                )
        else:
            req = session.get(base_link, headers=headers)
            base = BeautifulSoup(req.text, "lxml")
            items = base.find_all(class_="ag-tile open-tile")

            for i in items:
                link = i.a["href"]
                req = session.get(link, headers=headers)
                base = BeautifulSoup(req.text, "lxml")

                rows = base.find_all("tr")[1:]

                for item in rows:
                    location_name = item.find_all("td")[1].text
                    raw_address = item.td.text.split(",")

                    street_address = (
                        raw_address[0]
                        .replace("   ", " ")
                        .replace("(", "")
                        .replace(")", "")
                    )
                    if len(raw_address) == 3:
                        city = raw_address[1].strip()
                        state = raw_address[2].strip()
                    elif len(raw_address) == 2:
                        state = raw_address[-1].split()[-1]
                        city = raw_address[-1].split(state)[0].strip()
                    elif len(raw_address) == 1:
                        street_address = ""
                        city = raw_address[0]
                        state = ""
                        if city[-2:].isupper():
                            state = city[-2:].strip()
                            city = city[:-2]
                    city = city.replace("   ", " ")

                    sgw.write_row(
                        SgRecord(
                            locator_domain=locator_domain,
                            page_url=link,
                            location_name=location_name,
                            street_address=street_address,
                            city=city,
                            state=state,
                            zip_postal="",
                            country_code="US",
                            store_number="",
                            phone="",
                            location_type="",
                            latitude="",
                            longitude="",
                            hours_of_operation="",
                            raw_address=item.td.text.strip(),
                        )
                    )


with SgWriter(
    SgRecordDeduper(
        SgRecordID(
            {
                SgRecord.Headers.LOCATION_NAME,
                SgRecord.Headers.STREET_ADDRESS,
                SgRecord.Headers.CITY,
                SgRecord.Headers.STATE,
            }
        )
    )
) as writer:
    fetch_data(writer)
