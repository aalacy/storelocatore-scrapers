from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.dominos.lu/"
    api_url = "https://www.dominos.lu/fr/dynamicstoresearchapi/getlimitedstores/10/2000"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    js = r.json()["Data"]
    for j in js:

        location_name = j.get("Name") or "<MISSING>"
        a = j.get("Address")
        street_address = a.get("StreetName") or "<MISSING>"
        ad = a.get("FullAddress")
        state = a.get("State") or "<MISSING>"
        postal = a.get("PostalCode") or "<MISSING>"
        country_code = "LU"
        city = a.get("Suburb") or "<MISSING>"
        latitude = j.get("GeoCoordinates").get("Latitude") or "<MISSING>"
        longitude = j.get("GeoCoordinates").get("Longitude") or "<MISSING>"
        phone = j.get("PhoneNo") or "<MISSING>"
        store_number = j.get("StoreNo")
        page_url = f"https://www.dominos.lu/fr/magasin/{str(state).lower()}-{str(location_name).replace(' ','').lower()}-{store_number}"
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)
        hours_of_operation = (
            " ".join(
                tree.xpath(
                    '//div[@class="store-trading-hours"]/following-sibling::span/span[@class="visually-hidden"]//text()'
                )
            )
            .replace("\n", "")
            .strip()
        )
        hours_of_operation = " ".join(hours_of_operation.split()) or "<MISSING>"

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
            location_type=SgRecord.MISSING,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
            raw_address=ad,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))) as writer:
        fetch_data(writer)
