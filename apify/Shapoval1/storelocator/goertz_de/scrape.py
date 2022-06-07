from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.goertz.de/"
    api_url = "https://www.goertz.de/ajax/locationfinder/stores/?latitude=50.7780476&longitude=6.0887682&distance=800000"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0",
        "Accept": "*/*",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "Referer": "https://www.goertz.de/filialen/",
        "Content-Type": "application/json",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "Connection": "keep-alive",
    }

    r = session.get(api_url, headers=headers)
    js = r.json()["list"]
    for j in js:

        page_url = j.get("url") or "<MISSING>"
        location_name = j.get("storedesc") or "<MISSING>"
        location_type = j.get("type") or "<MISSING>"
        street_address = f"{j.get('street')} {j.get('streetno')}".replace(
            "None", ""
        ).strip()
        postal = j.get("zip") or "<MISSING>"
        country_code = j.get("country") or "<MISSING>"
        city = j.get("city") or "<MISSING>"
        store_number = j.get("id") or "<MISSING>"
        latitude = j.get("lat") or "<MISSING>"
        longitude = j.get("lng") or "<MISSING>"
        days = ["mo", "tu", "we", "th", "fr", "sa", "su"]
        tmp = []
        for d in days:
            day = str(d).capitalize()
            opens = j.get("openinghours").get(f"{d}").get("open")
            closes = j.get("openinghours").get(f"{d}").get("close")
            line = f"{day} {opens} - {closes}"
            tmp.append(line)
        hours_of_operation = "; ".join(tmp).replace("Su  -", "Su Closed").strip()
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)

        phone = (
            "".join(tree.xpath('//span[@itemprop="telephone"]//text()')) or "<MISSING>"
        )

        row = SgRecord(
            locator_domain=locator_domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=SgRecord.MISSING,
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
