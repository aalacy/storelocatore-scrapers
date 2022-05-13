from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from concurrent import futures


def get_urls():
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:85.0) Gecko/20100101 Firefox/85.0",
    }
    r = session.get("https://stanfordhealthcare.org/en.sitemap.xml", headers=headers)
    tree = html.fromstring(r.content)
    return tree.xpath("//url/loc[contains(text(), 'medical-clinics')]/text()")


def get_data(url, sgw: SgWriter):
    locator_domain = "https://stanfordhealthcare.org/"
    page_url = url
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:85.0) Gecko/20100101 Firefox/85.0",
    }
    try:
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)
    except:
        return
    street_address = "".join(tree.xpath('//meta[@name="sp_address_line1"]/@content'))
    if not street_address:
        return
    location_name = (
        "".join(tree.xpath('//meta[@name="sp_displayName"]/@content'))
        .replace("- OB/GYN", "")
        .replace("Stanford Express Care Clinic -", "Stanford Express Care Clinic")
        .strip()
    )
    if location_name.find(" in ") != -1:
        location_name = location_name.split(" in ")[0].strip()
    if location_name.find(" at ") != -1:
        location_name = location_name.split(" at ")[0].strip()
    if location_name.find(f"{street_address}") != -1:
        location_name = location_name.split("-")[0].strip()
    if location_name.find("–") != -1:
        location_name = location_name.split("–")[0].strip()
    if (
        location_name.find(f"{street_address.split()[0]}") != -1
        and street_address.find("-") != -1
    ):
        street_address = street_address.split("-")[0].strip()
    if location_name.find("Clinic -") != -1 or location_name.find("Center -") != -1:
        location_name = location_name.split("-")[0].strip()

    city = "".join(tree.xpath('//meta[@name="sp_city"]/@content'))
    if location_name.find(f"{city}") != -1:
        location_name = location_name.replace(f"{city}", "").strip()
    state = "".join(tree.xpath('//meta[@name="sp_state"]/@content'))
    postal = "".join(tree.xpath('//meta[@name="sp_zip"]/@content'))
    country_code = "US"
    phone = "".join(tree.xpath('//meta[@name="sp_phone"]/@content'))
    latitude = "".join(tree.xpath('//meta[@name="sp_latitude"]/@content'))
    longitude = "".join(tree.xpath('//meta[@name="sp_longitude"]/@content'))
    location_type = "<MISSING>"
    specialty_care = "".join(
        tree.xpath('//meta[@name="sp_specialty_care_clinic"]/@content')
    )
    primary_care_clinic = "".join(
        tree.xpath('//meta[@name="sp_primary_care_clinic"]/@content')
    )
    other_service = "".join(tree.xpath('//meta[@name="sp_other_service"]/@content'))
    if specialty_care == "true":
        location_type = "Specialty Care"
    if primary_care_clinic == "true":
        location_type = "Primary Care"
    if other_service == "true":
        location_type = "Other Services"

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
        hours_of_operation=SgRecord.MISSING,
    )

    sgw.write_row(row)


def fetch_data(sgw: SgWriter):
    urls = get_urls()
    with futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {executor.submit(get_data, url, sgw): url for url in urls}
        for future in futures.as_completed(future_to_url):
            future.result()


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))) as writer:
        fetch_data(writer)
