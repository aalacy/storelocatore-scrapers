import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.helpinghandshomecare.co.uk/"
    api_url = "https://www.helpinghandshomecare.co.uk/wp-admin/admin-ajax.php?action=store_search&lat=51.173516&lng=-0.172109&max_results=100000&radius=750000"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    js = r.json()
    for j in js:

        page_url = "".join(j.get("permalink"))
        location_name = (
            "".join(j.get("store"))
            .replace("&amp;", "&")
            .replace("&#8217;", "’")
            .strip()
            or "<MISSING>"
        )
        street_address = f"{j.get('address')}".replace(",", "").strip() or "<MISSING>"
        state = f"{j.get('state')}".replace(",", "").strip() or "<MISSING>"
        postal = j.get("zip") or "<MISSING>"
        country_code = "UK"
        city = f"{j.get('city')}".replace(",", "").strip() or "<MISSING>"
        if city == "<MISSING>":
            city = page_url.split("/")[-2].replace("-", " ").capitalize().strip()
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
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)

        js_block = (
            "".join(tree.xpath('//script[contains(text(), "latitude")]/text()'))
            or "<MISSING>"
        )
        if js_block != "<MISSING>":
            j = json.loads(js_block)
            street_address = j.get("address").get("streetAddress")
            postal = j.get("address").get("postalCode") or "<MISSING>"
        if street_address.find("Contact us") != -1:
            street_address = "<MISSING>"
        street_address = street_address.replace(",", "") or "<MISSING>"
        if street_address == "Unit 2":
            street_address = (
                "".join(tree.xpath('//p[@class="branch-address-text"]/text()[1]'))
                .replace(",", "")
                .replace("\n", "")
                .strip()
            )
        if street_address == "Unit 8":
            street_address = (
                "".join(tree.xpath('//p[@class="branch-address-text"]/text()[1]'))
                .replace(",", "")
                .replace("\n", "")
                .strip()
            )
        postal = postal.replace(",", "").strip()
        if postal == "Hammersmith":
            postal = "<MISSING>"
        if street_address.find("Frome") != -1:
            street_address = street_address.split("Frome")[0].strip()
        if street_address.find("Monmouth") != -1:
            postal = " ".join(street_address.split()[-2:])
            street_address = street_address.split("Monmouth")[0].strip()
        par_loc = j.get("parent_branch")
        if par_loc:
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
            store_number=SgRecord.MISSING,
            phone=phone,
            location_type=SgRecord.MISSING,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))) as writer:
        fetch_data(writer)
