import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID


def remove_comma(text):
    text = text.strip()
    if text.endswith(","):
        return text[:-1]
    return text


def fetch_data(sgw: SgWriter):
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    divs = tree.xpath(
        "//div[@class='row sqs-row' and count(./div[@class='col sqs-col-6 span-6'])=2]"
    )

    for d in divs:
        location_name = "".join(d.xpath(".//h3[1]//text()"))
        js = d.xpath(".//div[@data-block-json]/@data-block-json")[0]
        try:
            j = json.loads(js)["location"]
            latitude = j.get("markerLat")
            longitude = j.get("markerLng")
        except:
            if "thumbnailUrl" in js:
                latitude, longitude = js.split("center=")[-1].split("&")[0].split(",")
            else:
                latitude, longitude = SgRecord.MISSING, SgRecord.MISSING

        location_type = SgRecord.MISSING
        if "coming soon" in location_name.lower():
            location_type = "Coming Soon"
        street_address = remove_comma(
            "".join(d.xpath(".//h3[1]/following-sibling::p[1]/text()"))
        )
        line = "".join(d.xpath(".//h3[1]/following-sibling::p[2]/text()"))
        postal = line.split()[-1]
        state = line.split()[-2]
        city = remove_comma(line.replace(postal, "").replace(state, "").strip())
        try:
            phone = (
                d.xpath(".//a[contains(@href, 'tel:')]/text()")[0]
                .replace("\xa0", " ")
                .strip()
            )
        except IndexError:
            phone = SgRecord.MISSING

        hours_of_operation = " ".join(
            ";".join(
                d.xpath(
                    ".//strong[contains(text(), 'Hours')]/following-sibling::text()"
                )
            ).split()
        )

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code="US",
            location_type=location_type,
            phone=phone,
            latitude=latitude,
            longitude=longitude,
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.playtri.com/"
    page_url = "https://www.playtri.com/locations"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0"
    }
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.LOCATION_NAME}))
    ) as writer:
        fetch_data(writer)
