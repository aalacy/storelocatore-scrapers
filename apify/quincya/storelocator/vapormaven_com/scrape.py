from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests


def fetch_data(sgw: SgWriter):

    base_link = "https://www.google.com/maps/d/u/0/embed?mid=1nHEcQRe7S-wHl-S4f4ZGK5bA3RRp7BQu&ll=35.362378823551076%2C-94.74845825&z=6"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()

    stores_req = session.get(base_link, headers=headers)
    raw_info = stores_req.text.replace('\\"', '"').strip()
    street_addresses = raw_info.split('["1 Address",["')
    cities = raw_info.split('["City",["')
    states = raw_info.split('["State",["')
    zipcodes = raw_info.split('["Zip",["')
    phone_list = raw_info.split('["Phone",["')

    for index in range(1, len(cities)):
        page_url = "https://vapormaven.com/location/"
        locator_domain = "https://vapormaven.com/"

        street_address = "".join(street_addresses[index].split('"')[0]).strip()
        city = "".join(cities[index].split('"')[0]).strip().replace("\\u0027", "'")
        location_name = city
        state = "".join(states[index].split('"')[0]).strip()
        zip = "".join(zipcodes[index].split('"')[0]).strip()

        country_code = "US"
        store_number = "<MISSING>"

        phone = "".join(phone_list[index].split('"')[0]).strip()
        location_type = "<MISSING>"
        hours_of_operation = "<MISSING>"
        latlng = "".join(
            cities[index - 1].rsplit("[[[", 1)[1].strip().split("]")[0]
        ).strip()
        latitude = latlng.split(",")[0].strip()
        longitude = latlng.split(",")[1].strip()

        sgw.write_row(
            SgRecord(
                locator_domain=locator_domain,
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zip,
                country_code=country_code,
                store_number=store_number,
                phone=phone,
                location_type=location_type,
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=hours_of_operation,
            )
        )


with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))) as writer:
    fetch_data(writer)
