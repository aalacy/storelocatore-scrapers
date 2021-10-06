from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.murraysupply.com/"
    api_url = "https://www.murraysupply.com/api/v1/dealers?latitude=34.03054&longitude=-118.38458&radius=10000&pageSize=100&startPage=1&"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    js = r.json()["dealers"]
    for j in js:
        slug = j.get("id")
        page_url = f"https://www.murraysupply.com/Locations/Branch-Locations/Dealer?dealerId={slug}"
        location_name = "".join(j.get("name"))
        location_type = "Branch"
        street_address = f"{j.get('address1')} {j.get('address2')}".strip()
        state = j.get("state")
        postal = j.get("postalCode")
        country_code = "US"
        city = j.get("city")
        latitude = j.get("latitude")
        longitude = j.get("longitude")
        phone = j.get("phone")
        store_number = "<MISSING>"
        if location_name.find("#") != -1:
            store_number = location_name.split("#")[1].strip()
        hours_of_operation = j.get("properties").get("hours")
        a = html.fromstring(hours_of_operation)
        hours_of_operation = (
            " ".join(a.xpath("//*//text()")).replace("Via Palace Avenue", "").strip()
        )
        if hours_of_operation.find("Holiday") != -1:
            hours_of_operation = hours_of_operation.split("Holiday")[0].strip()
        if hours_of_operation.find("Showroom open by appointment") != -1:
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
            store_number=store_number,
            phone=phone,
            location_type=location_type,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.LOCATION_NAME}))
    ) as writer:
        fetch_data(writer)
