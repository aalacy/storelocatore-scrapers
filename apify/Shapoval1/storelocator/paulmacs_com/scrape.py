from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://paulmacs.com/"
    api_url = "https://store.petvalu.ca/modules/multilocation/?near_location=K6V%203G9&threshold=4000&geocoder_components=country:CA&distance_unit=km&limit=20000&services__in=&language_code=en-us&published=1&within_business=true"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    js = r.json()["objects"]
    for j in js:

        page_url = j.get("location_url") or "https://store.petvalu.ca/"
        location_name = j.get("location_name") or "<MISSING>"
        street_address = j.get("street") or "<MISSING>"
        state = j.get("state") or "<MISSING>"
        postal = j.get("postal_code") or "<MISSING>"
        country_code = "CA"
        city = j.get("city") or "<MISSING>"
        store_number = j.get("partner_location_sub_id") or "<MISSING>"
        latitude = j.get("lat") or "<MISSING>"
        longitude = j.get("lon") or "<MISSING>"
        phone = j.get("phonemap").get("phone") or "<MISSING>"
        try:
            r = session.get(page_url, headers=headers)
            tree = html.fromstring(r.text)
            hours_of_operation = (
                " ".join(tree.xpath('//div[@class="hours-box"]/div//text()'))
                .replace("\n", "")
                .strip()
            )
            hours_of_operation = " ".join(hours_of_operation.split()) or "<MISSING>"
            raw_address = j.get("formatted_address")
        except:
            hours_of_operation = "<MISSING>"
            raw_address = f"{street_address} {city}, {state} {postal}".replace(
                "<MISSING>", ""
            ).strip()

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
            raw_address=raw_address,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(
            SgRecordID({SgRecord.Headers.STORE_NUMBER, SgRecord.Headers.PAGE_URL})
        )
    ) as writer:
        fetch_data(writer)
