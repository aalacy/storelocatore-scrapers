from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://chuckanddons.com/"
    api_url = "https://stores.boldapps.net/front-end/get_surrounding_stores.php?shop=chuckanddonsdev.myshopify.com&latitude=37.568069&longitude=-97.2005806&max_distance=10000&limit=100&calc_distance=1"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    js = r.json()["stores"]
    for j in js:

        page_url = j.get("website") or "<MISSING>"
        location_name = j.get("name") or "<MISSING>"
        street_address = (
            f"{j.get('address')} {j.get('address2')}".strip() or "<MISSING>"
        )
        state = j.get("prov_state") or "<MISSING>"
        postal = j.get("postal_zip") or "<MISSING>"
        country_code = "US"
        city = j.get("city") or "<MISSING>"
        latitude = j.get("lat") or "<MISSING>"
        longitude = j.get("lng") or "<MISSING>"
        phone = j.get("phone") or "<MISSING>"
        hours_of_operation = (
            "".join(j.get("hours")).replace("\r\n", " ").strip() or "<MISSING>"
        )
        if hours_of_operation == "<MISSING>":
            r = session.get(page_url, headers=headers)
            tree = html.fromstring(r.text)
            hours_of_operation = (
                " ".join(tree.xpath('//div[@itemprop="openingHours"]/@content'))
                .replace("\n", "")
                .strip()
                or "<MISSING>"
            )

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
            location_type=SgRecord.MISSING,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
            raw_address=f"{street_address} {city}, {state} {postal}",
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))) as writer:
        fetch_data(writer)
