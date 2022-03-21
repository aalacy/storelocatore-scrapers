import time
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://carilionclinic.org"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "Origin": "https://www.carilionclinic.org",
        "Connection": "keep-alive",
        "Referer": "https://www.carilionclinic.org/locations?q=Hospitals",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
    }

    json_data = {
        "query": "*",
        "rows": "2000",
        "fields": [
            "*_type",
            "*_title",
            "*_body_summary",
            "*_en_url",
            "*_field_given_name",
            "*_field_surname",
            "*_field_affiliations",
            "*_en_provider_photo_uri",
            "*_field_primaryphone_location",
            "*_field_primaryphone",
            "*_field_acceptsnewclients",
            "*_field_acceptschildren",
            "*_field_specialties",
            "*_field_services",
            "*_address_line1",
            "*_locality",
            "*_administrative_area",
            "*_postal_code",
            "*_en_location_hero_image_uri",
            "*_field_service_areas",
            "*_field_medical_categories",
            "*_field_specialty_conditions",
            "*_en_url",
            "*_field_owned",
            "*_latlon",
        ],
        "sort": {
            "ss_title": "ASC",
        },
        "queryfields": [
            "searchfields",
            "ts_title",
        ],
        "type": "edismax",
        "filterquery": {
            "index_id": {
                "query": "ss_type:location",
            },
        },
        "geofilt": {},
        "bq": {},
    }

    r = session.post(
        "https://www.carilionclinic.org/solr/select",
        headers=headers,
        json=json_data,
    )
    js = r.json()["results"]

    for j in js:
        slug = j.get("tm_X3b_en_url")[0]
        page_url = f"{locator_domain}{slug}"
        location_name = "".join(j.get("ts_title"))
        if location_name.find("-") != -1:
            location_name = location_name.split("-")[0].strip()
        location_type = j.get("ss_type")
        street_address = j.get("ts_address_line1")
        state = j.get("ss_administrative_area")
        postal = j.get("ss_postal_code")
        country_code = "USA"
        city = j.get("ss_locality")
        ll = j.get("ss_latlon") or "<MISSING>"
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        if ll != "<MISSING>":
            latitude = str(ll).split(",")[0]
            longitude = str(ll).split(",")[1]
        phone = j.get("ss_field_primaryphone")
        r = session.get(page_url, headers=headers)
        time.sleep(3)
        tree = html.fromstring(r.text)
        hours_of_operation = (
            " ".join(tree.xpath('//meta[@name="description"]/@content')) or "<MISSING>"
        )
        if hours_of_operation.find("open") != -1:
            hours_of_operation = " ".join(hours_of_operation.split("open")[1:]).strip()
        if hours_of_operation == "|":
            hours_of_operation = "<MISSING>"
        if (
            hours_of_operation.find("|") != -1
            and hours_of_operation.find("AM") != -1
            and hours_of_operation.find("PM") != -1
        ):
            hours_of_operation = hours_of_operation.split("|")[0].strip()
        if hours_of_operation.find("Inpatient Visiting Hours:") != -1:
            hours_of_operation = (
                hours_of_operation.split("Inpatient Visiting Hours:")[1]
                .split("|")[0]
                .strip()
            )
        if hours_of_operation.find("|") != -1:
            hours_of_operation = "<MISSING>"

        row = SgRecord(
            locator_domain=locator_domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code=country_code,
            store_number=SgRecord.MISSING,
            phone=phone,
            location_type=location_type,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))) as writer:
        fetch_data(writer)
