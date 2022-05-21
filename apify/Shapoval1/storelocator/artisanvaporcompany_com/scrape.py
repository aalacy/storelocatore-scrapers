from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.artisanvaporcompany.com/"
    api_url = "https://www.artisanvaporcompany.com/wp-admin/admin-ajax.php?action=store_search&lat=37.09024&lng=-95.71289&max_results=25&search_radius=50&autoload=1"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    js = r.json()
    for j in js:

        page_url = "https://www.artisanvaporcompany.com/store-locator/"
        location_name = "".join(j.get("store")).replace("&amp;", "&").strip()
        street_address = f"{j.get('address')} {j.get('address2')}".strip()
        state = j.get("state") or "<MISSING>"
        postal = "".join(j.get("zip")) or "<MISSING>"
        country_code = "US"
        city = j.get("city")
        if postal.find("IL") != -1:
            state = "IL"
            postal = postal.replace("IL", "").strip()
        if postal == state:
            postal = street_address.split(",")[-2].split()[-1].strip()
            state = street_address.split(",")[-2].split()[0].strip()
            street_address = street_address.split(f"{city}")[0].replace(",", "").strip()
        if street_address.find("Port Arthur") != -1:
            city = "Port Arthur"
            street_address = street_address.replace("Port Arthur", "").strip()
        store_number = j.get("id")
        latitude = j.get("lat") or "<MISSING>"
        longitude = j.get("lng") or "<MISSING>"
        phone = j.get("phone") or "<MISSING>"
        hours_of_operation = "<MISSING>"
        hours = j.get("hours") or "<MISSING>"
        if hours != "<MISSING>":
            a = html.fromstring(hours)
            hours_of_operation = (
                " ".join(a.xpath("//*//text()")).replace("\n", "").strip()
            )
            hours_of_operation = " ".join(hours_of_operation.split())
        desc = j.get("description") or "<MISSING>"
        per_cls = "<MISSING>"
        if desc != "<MISSING>":
            b = html.fromstring(desc)
            per_cls = "".join(
                b.xpath('//*[contains(text(), "Store closed permanently")]/text()')
            )
        if per_cls == "Store closed permanently.":
            continue

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
            raw_address=f"{street_address} {city}, {state} {postal}".replace(
                "<MISSING>", ""
            ).strip(),
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STORE_NUMBER}))
    ) as writer:
        fetch_data(writer)
