import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID


def fetch_data(sgw: SgWriter):
    data = {"address": "2000"}
    r = session.post(page_url, headers=headers, data=data)
    tree = html.fromstring(r.text)
    divs = tree.xpath("//div[@class='module-locations-results__item']")

    coords = dict()
    text = "".join(tree.xpath("//script[contains(text(), 'locations:')]/text()"))
    text = text.split("locations:")[1].split("}],")[0] + "}]"
    js = json.loads(text)

    for j in js:
        _id = j.get("id")
        link = j.get("link")
        lat = j.get("lat")
        lng = j.get("lng")
        coords[link] = (lat, lng, _id)

    for d in divs:
        location_name = "".join(d.xpath(".//h2/text()")).strip()
        raw_address = "".join(
            d.xpath(
                ".//div[./h5[contains(text(), 'Adres')]]/following-sibling::div[1]//text()"
            )
        ).strip()
        street_address, postal, city = raw_address.split(", ")
        country_code = "NL"
        phone = "".join(
            d.xpath(
                ".//div[./h5[contains(text(), 'Telefoon')]]/following-sibling::div[1]//text()"
            )
        ).strip()
        if "bereikbaar" in phone:
            phone = SgRecord.MISSING
        if "of" in phone:
            phone = phone.split("of")[0].strip()
        key = "".join(d.xpath(".//a[contains(text(), 'Plan')]/@href"))
        latitude, longitude, store_number = coords.get(key) or (
            SgRecord.MISSING,
            SgRecord.MISSING,
            SgRecord.MISSING,
        )

        _tmp = []
        hours = d.xpath(
            ".//div[./h5[contains(text(), 'Openingstijden')]]/following-sibling::div[1]/div"
        )
        for h in hours:
            day = "".join(h.xpath("./div[1]//text()")).strip()
            inter = "".join(h.xpath("./div[2]//text()")).strip()
            if not inter:
                continue
            if "(" in inter:
                inter = inter.split("(")[0]

            inter = (
                inter.replace("tijdens Lockdown", "")
                .replace("voor PostNL handelingen", "")
                .strip()
            )
            _tmp.append(f"{day}: {inter}")

        hours_of_operation = ";".join(_tmp)

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            zip_postal=postal,
            country_code=country_code,
            latitude=latitude,
            longitude=longitude,
            phone=phone,
            store_number=store_number,
            hours_of_operation=hours_of_operation,
            raw_address=raw_address,
            locator_domain=locator_domain,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.cigo.nl/"
    page_url = "https://www.cigo.nl/winkels/"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:99.0) Gecko/20100101 Firefox/99.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "ru,en-US;q=0.7,en;q=0.3",
        "Origin": "https://www.cigo.nl",
        "Connection": "keep-alive",
        "Referer": "https://www.cigo.nl/winkels/",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-User": "?1",
    }
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.RAW_ADDRESS}))
    ) as writer:
        fetch_data(writer)
