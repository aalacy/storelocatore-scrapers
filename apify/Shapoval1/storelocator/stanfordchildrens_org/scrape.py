import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.stanfordchildrens.org/"
    api_url = "https://www.stanfordchildrens.org/en/locations-directions"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = (
        "".join(tree.xpath('//script[contains(text(), "var  json =")]/text()'))
        .split("var  json =")[1]
        .split("}]}};")[0]
        + "}]}}"
    )
    js = json.loads(div)
    for j in js["response"]["docs"]:

        slug = j.get("id")
        page_url = f"https://www.stanfordchildrens.org/en/location/{slug}"
        location_name = j.get("name") or "<MISSING>"
        location_type = j.get("loctype") or "<MISSING>"
        street_address = (
            f"{j.get('address-a')} {j.get('address-b') or ''}".replace("None", "")
            .replace("Neuromuscular Disorders Family Clinic", "")
            .replace("(Stanford Barn)", "")
            .replace("El Camino Hospital Sobrato Pavilion", "")
            .replace("El Camino Hospital - Sobrato Pavilion", "")
            .strip()
        )
        state = j.get("state") or "<MISSING>"
        postal = j.get("zip") or "<MISSING>"
        country_code = "US"
        city = j.get("city") or "<MISSING>"
        latitude = j.get("lat") or "<MISSING>"
        longitude = j.get("long") or "<MISSING>"
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)
        info = tree.xpath("//h4/following-sibling::p[1]/text()")
        info = list(filter(None, [a.strip() for a in info]))
        phone = "<MISSING>"
        if info:
            for i in info:
                if "Phone" in i:
                    phone = str(i).replace("Phone:", "").strip()
        hours_of_operation = (
            " ".join(
                tree.xpath(
                    '//div[./h2[text()="Office Hours"]]/following-sibling::div[1]//text()'
                )
            )
            .replace("\n", "")
            .strip()
        )
        hours_of_operation = " ".join(hours_of_operation.split()) or "<MISSING>"
        if hours_of_operation.find("Holidays by appointment") != -1:
            hours_of_operation = hours_of_operation.split("Holidays by appointment")[
                1
            ].strip()
        if hours_of_operation.find("* *") != -1:
            hours_of_operation = hours_of_operation.split("* *")[0].strip()
        if hours_of_operation.find("Neonatal") != -1:
            hours_of_operation = "<MISSING>"
        if hours_of_operation.find("Learn about") != -1:
            hours_of_operation = hours_of_operation.split("Learn about")[0].strip()
        if hours_of_operation.find("After Hours") != -1:
            hours_of_operation = hours_of_operation.split("After Hours")[0].strip()
        if hours_of_operation.find("After hours") != -1:
            hours_of_operation = hours_of_operation.split("After hours")[0].strip()

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
