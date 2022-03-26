import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import International_Parser, parse_address


def fetch_data(sgw: SgWriter):

    locator_domain = "https://tacobell.co.nz/"
    api_url = "https://tacobell.co.nz/en/store-locator.html"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = (
        "".join(tree.xpath('//script[contains(text(), "pageData")]/text()'))
        .split("pageData=")[1]
        .split("window.isGeneratedStatically")[0]
        .strip()
    )
    div = "".join(div[:-1])
    js = json.loads(div)

    for j in js["chainStores"]["msg"]:

        b = j.get("address")
        location_name = j.get("title").get("en_US")
        ad = b.get("formatted")
        a = parse_address(International_Parser(), ad)
        street_address = (
            f"{a.street_address_1} {a.street_address_2}".replace("None", "").strip()
            or "<MISSING>"
        )
        state = a.state or "<MISSING>"
        postal = a.postcode or "<MISSING>"
        country_code = "NZ"
        city = b.get("city") or "<MISSING>"
        latitude = b.get("latLng").get("lat") or "<MISSING>"
        longitude = b.get("latLng").get("lng") or "<MISSING>"
        phone = j.get("contact").get("phone") or "<MISSING>"
        hours = j.get("openingHours")[0].get("en")
        days = [
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
            "Sunday",
        ]
        hours_of_operation = "<MISSING>"
        tmp = []
        if hours:
            for d in range(len(days)):
                day = days[d]
                times = hours[d][0]
                line = f"{day} {times}"
                tmp.append(line)
            hours_of_operation = "; ".join(tmp)
        slug = str(location_name).replace(" ", "_")
        page_url = f"https://tacobell.co.nz/en/store-locator/{slug}.html"

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
            raw_address=ad,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))) as writer:
        fetch_data(writer)
