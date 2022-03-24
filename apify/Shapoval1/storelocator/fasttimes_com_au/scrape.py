import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://fasttimes.com.au/"
    api_url = "https://fasttimes.com.au/stores"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = (
        "".join(
            tree.xpath(
                '//script[contains(text(), "Aheadworks_StoreLocator/js/view/location-list")]/text()'
            )
        )
        .split('"locationItems":')[1]
        .split("\n")[0]
        .strip()
    )
    div = " ".join(div.split())
    div = "".join(div[:-1])
    js = json.loads(div)
    for j in js:

        page_url = "".join(j.get("more_details_url"))
        if page_url.find("https") == -1:
            page_url = f"https://fasttimes.com.au/{page_url}"
        location_name = j.get("title")
        street_address = j.get("street")
        state = j.get("region")
        postal = j.get("zip")
        country_code = j.get("country_id")
        city = j.get("city")
        store_number = j.get("location_id")
        latitude = j.get("latitude")
        longitude = j.get("longitude")
        phone = j.get("phone")
        days = [
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
            "Sunday",
        ]
        try:
            h = eval(j.get("hoursofoperation"))

            tmp = []
            for d in days:
                day = d
                opens = h.get(f"{d}")[0]
                closes = h.get(f"{d}")[1]
                line = f"{day} {opens} - {closes}"
                tmp.append(line)
            hours_of_operation = "; ".join(tmp)
        except:
            hours_of_operation = "<MISSING>"
        if hours_of_operation == "<MISSING>":
            r = session.get(page_url, headers=headers)
            tree = html.fromstring(r.text)

            hours_of_operation = (
                " ".join(
                    tree.xpath(
                        '//p[./strong[text()="Opening Hours:"]]/following-sibling::p[1]//text()'
                    )
                )
                .replace("\n", "")
                .strip()
            )
            hours_of_operation = " ".join(hours_of_operation.split())

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
            raw_address=f"{street_address} {city}, {state} {postal}",
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)
