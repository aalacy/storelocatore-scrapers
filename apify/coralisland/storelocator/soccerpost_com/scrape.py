from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.soccerpost.com/"
    api_url = "https://www.soccerpost.com/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    jsblock = (
        "".join(tree.xpath('//script[contains(text(), "latitude")]/text()'))
        .split("SP.stores = ")[1]
        .split(";")[0]
        .replace("{", "{ ")
        .strip()
    )
    jsblock = (
        jsblock.replace("name", '"name"')
        .replace("address:", '"address":')
        .replace("address2", '"address2"')
        .replace("city", '"city"')
        .replace("state", '"state"')
        .replace("zip", '"zip"')
        .replace("phone", '"phone"')
        .replace("url", '"url"')
        .replace("latitude", '"latitude"')
        .replace("longitude", '"longitude"')
        .replace("email", '"email"')
        .replace("home", '"home"')
        .replace("true", "True")
        .replace("prefix", '"prefix"')
        .replace("false", "False")
    )
    js = eval(jsblock)

    for j in js:
        page_url = j.get("url") or "https://www.soccerpost.com/"
        location_name = j.get("name") or "<MISSING>"
        street_address = f"{j.get('address')} {j.get('address2') or ''}".strip()
        if street_address.find("Severna Park Market") != -1:
            street_address = street_address.split("Severna Park Market")[0].strip()
        if street_address.find("Franklin Crossing Shopping Center") != -1:
            street_address = street_address.split("Franklin Crossing Shopping Center")[
                0
            ].strip()
        street_address = street_address.replace(
            "Greenbriar Shopping Center", ""
        ).strip()
        if street_address == "NEW location opening soon!":
            continue
        state = j.get("state") or "<MISSING>"
        postal = j.get("zip") or "<MISSING>"
        country_code = "US"
        city = j.get("city") or "<MISSING>"
        latitude = j.get("latitude") or "<MISSING>"
        longitude = j.get("longitude") or "<MISSING>"
        phone = j.get("phone") or "<MISSING>"

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
            hours_of_operation=SgRecord.MISSING,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)
