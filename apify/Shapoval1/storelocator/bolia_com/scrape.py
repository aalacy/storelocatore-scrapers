import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.bolia.com"
    api_urls = [
        "https://www.bolia.com/api/location/stores?language=en-gb&v=2021.3975.1115.1-43",
        "https://www.bolia.com/api/location/partnerstores?language=en-gb&v=2021.3975.1115.1-43",
    ]
    for api_url in api_urls:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
        }
        r = session.get(api_url, headers=headers)
        js = r.json()["model"]
        for j in js:
            slug = j.get("url") or "<MISSING>"
            page_url = "https://www.bolia.com/en-gb/this-is-us/stores/our-dealers/bolia-bergen-vaskerelven/"
            location_name = j.get("htmlTitle")
            location_type = j.get("type")
            if location_type == "Store":
                page_url = f"{locator_domain}{slug}"
            street_address = (
                str(j.get("street")).replace("\n", " ").strip() or "<MISSING>"
            )
            postal = j.get("zipCode") or "<MISSING>"
            country_code = j.get("countryCode") or "<MISSING>"
            if country_code == "xx":
                continue
            city = j.get("city") or "<MISSING>"
            latitude = j.get("latitude") or "<MISSING>"
            longitude = j.get("longitude") or "<MISSING>"
            phone = "<MISSING>"
            hours_of_operation = "<MISSING>"
            if location_type == "Store":
                r = session.get(page_url, headers=headers)
                tree = html.fromstring(r.text)

                js_block = "".join(
                    tree.xpath('//script[@type="application/ld+json"]/text()')
                )
                js = json.loads(js_block)
                phone = js.get("telephone") or "<MISSING>"
                hours = "".join(tree.xpath("//*[@opening-hours]/@opening-hours"))
                js_hours = json.loads(hours)
                tmp = []
                for h in js_hours[:7]:
                    day = h.get("formattedDay")
                    start = (
                        str(h.get("startTime"))
                        .split("T")[1]
                        .replace("+00:00", "")
                        .strip()
                    )
                    end = (
                        str(h.get("endTime"))
                        .split("T")[1]
                        .replace("+00:00", "")
                        .strip()
                    )
                    line = f"{day} {start} - {end}"
                    tmp.append(line)
                hours_of_operation = "; ".join(tmp) or "<MISSING>"
                cms = "".join(tree.xpath('//h1[contains(text(), "Opening")]/text()'))
                if cms:
                    hours_of_operation = "Coming Soon"

            row = SgRecord(
                locator_domain=locator_domain,
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=SgRecord.MISSING,
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
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {SgRecord.Headers.STREET_ADDRESS, SgRecord.Headers.LOCATION_NAME}
            )
        )
    ) as writer:
        fetch_data(writer)
