from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import International_Parser, parse_address


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.honda.co.nz"
    api_url = "https://www.honda.co.nz/dealerlocations/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)

    div = r.text.split("var dealerLocations = ")[1].split(";")[0].strip()
    js = eval(div)
    for j in js.values():
        slug = j.get("url")
        page_url = f"https://www.honda.co.nz{slug}"
        latitude = j.get("lat")
        longitude = j.get("long")
        location_name = j.get("name")
        location_type = str(location_name).split()[1].strip()
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)
        ad = (
            "".join(
                tree.xpath('//h2[text()="Details"]/following-sibling::p[1]//text()')
            )
            .replace("\n", "")
            .replace("Physical Address", "")
            .strip()
        )
        ad = " ".join(ad.split())
        a = parse_address(International_Parser(), ad)
        street_address = f"{a.street_address_1} {a.street_address_2}".replace(
            "None", ""
        ).strip()
        state = a.state or "<MISSING>"
        postal = a.postcode or "<MISSING>"
        country_code = "NZ"
        city = a.city.replace("Wairau Valley", "").strip() or "<MISSING>"
        phone = (
            "".join(
                tree.xpath(
                    '//p[@class="address"]/following-sibling::a[contains(@href, "tel")][1]/span/text()'
                )
            )
            .replace("\n", "")
            .strip()
        )
        hours_of_operation = (
            " ".join(
                tree.xpath(
                    '//h2[text()="Opening hours"]/following-sibling::p[1]/span//text()'
                )
            )
            .replace("\n", "")
            .strip()
        )
        hours_of_operation = (
            " ".join(hours_of_operation.split()).replace("Only —", "").strip()
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
            store_number=SgRecord.MISSING,
            phone=phone,
            location_type=location_type,
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
