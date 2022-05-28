import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import International_Parser, parse_address


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.hondacarindia.com/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0",
        "Accept": "*/*",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "X-Requested-With": "XMLHttpRequest",
        "Origin": "https://www.hondacarindia.com",
        "Connection": "keep-alive",
        "Referer": "https://www.hondacarindia.com/car-dealers-showrooms",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "Cache-Control": "max-age=0",
        "TE": "trailers",
    }

    data = {
        "lngtitude": "0",
        "latitude": "0",
        "radius": "Select Radius",
        "outlettype": "Select Outlet Type",
    }

    r = session.post(
        "https://www.hondacarindia.com/finddealer/getresult", headers=headers, data=data
    )
    js = r.json()["mapData"]
    j = json.loads(js)
    for c in j:

        page_url = (
            c.get("dealerURL") or "https://www.hondacarindia.com/car-dealers-showrooms"
        )
        location_name = c.get("Name") or "<MISSING>"
        location_type = c.get("Outlettype") or "<MISSING>"
        ad = (
            "".join(c.get("Address"))
            .replace("\n", "")
            .replace("<br>", "")
            .replace("\r", "")
            .strip()
        )
        a = parse_address(International_Parser(), ad)
        street_address = (
            f"{a.street_address_1} {a.street_address_2}".replace("None", "").strip()
            or "<MISSING>"
        )
        if street_address == "<MISSING>" or street_address.isdigit():
            street_address = ad
        state = c.get("StateName") or "<MISSING>"
        postal = a.postcode or "<MISSING>"
        if postal.find("-") != -1:
            postal = postal.split("-")[1].strip()
        if postal.find(".") != -1:
            postal = postal.split(".")[1].strip()
        postal = postal or "<MISSING>"
        country_code = "India"
        city = c.get("CityName") or "<MISSING>"
        store_number = c.get("dealerCode") or "<MISSING>"
        latitude = c.get("latitude") or "<MISSING>"
        longitude = c.get("longitude") or "<MISSING>"
        phone = str(c.get("Telephone")) or "<MISSING>"
        if phone.find(",") != -1:
            phone = phone.split(",")[0].strip()
        hours_of_operation = "<MISSING>"
        if page_url != "https://www.hondacarindia.com/car-dealers-showrooms":
            session = SgRequests(verify_ssl=False)
            r = session.get(page_url, headers=headers)
            tree = html.fromstring(r.text)
            hours_of_operation = (
                " ".join(
                    tree.xpath(
                        '//div[@id="speakableBusinessHoursContent"]//ul/li/span/text()'
                    )
                )
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
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STORE_NUMBER}))
    ) as writer:
        fetch_data(writer)
