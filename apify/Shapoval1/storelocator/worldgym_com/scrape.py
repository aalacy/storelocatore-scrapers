import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.worldgym.com"
    api_url = "https://www.worldgym.com/findagym?search=ca"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    jsblock = (
        "".join(
            tree.xpath('//script[contains(text(), "var franhiseeLocations")]/text()')
        )
        .split("var franhiseeLocations = ")[1]
        .split(";")[0]
        .strip()
    )
    js = json.loads(jsblock)

    for j in js:

        page_url = j.get("MicroSiteUrl") or "<MISSING>"
        location_name = j.get("LocationName") or "<MISSING>"
        location_type = "GYM"
        street_address = f"{j.get('Line1')} {j.get('Line2')}".strip() or "<MISSING>"
        state = j.get("State") or "<MISSING>"
        postal = j.get("Postal") or "<MISSING>"
        country_code = j.get("Country")

        city = j.get("City") or "<MISSING>"
        store_number = (
            "".join(j.get("LocationNumber")).replace("WGY", "").strip() or "<MISSING>"
        )
        latitude = j.get("Latitude") or "<MISSING>"
        longitude = j.get("Longitude") or "<MISSING>"
        phone = j.get("PhoneWithOutCountryCode") or "<MISSING>"

        session = SgRequests()
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)

        hours_of_operation = (
            " ".join(
                tree.xpath(
                    '//div[contains(@class, "tab-pane gymhourstab")]//h5//text()'
                )
            )
            .replace("\n", "")
            .strip()
            or "<MISSING>"
        )
        if hours_of_operation == "<MISSING>":
            hours_of_operation = (
                " ".join(
                    tree.xpath(
                        '//div[./div/h2[text()="HEURES"]]/following-sibling::div[1]//text()'
                    )
                )
                .replace("\n", "")
                .strip()
                or "<MISSING>"
            )
        hours_of_operation = (
            hours_of_operation.replace("LUNDI", "MONDAY")
            .replace("MARDI", "TUESDAY")
            .replace("MERCREDI", "WEDNESDAY")
            .replace("JEUDI", "THURSDAY")
            .replace("VENDREDI", "FRIDAY")
            .replace("SAMDI", "SATURDAY ")
            .replace("DIMANCHE", "SUNDAY")
            .replace("SAMEDI", "SATURDAY")
            .replace("À", "TO")
        )
        if hours_of_operation.find("Taille") != -1:
            hours_of_operation = (
                hours_of_operation.split("Taille")[0].strip() or "<MISSING>"
            )
        hours_of_operation = hours_of_operation or "<MISSING>"

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
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.LATITUDE}))) as writer:
        fetch_data(writer)
