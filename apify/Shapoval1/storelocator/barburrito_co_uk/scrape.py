import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgpostal import International_Parser, parse_address


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.barburrito.co.uk"
    api_url = "https://www.barburrito.co.uk/restaurants"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    jsblock = (
        "".join(tree.xpath('//script[contains(text(), "var mmm_maps = ")]/text()'))
        .split("var mmm_maps = ")[1]
        .split(";")[0]
        .strip()
    )
    js = json.loads(jsblock)
    for j in js:
        locations = j.get("markers")
        for l in locations:
            store_number = l.get("id")
            latitude = l.get("lat")
            longitude = l.get("lng")

            session = SgRequests()
            headers = {
                "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0",
                "Accept": "*/*",
                "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
                "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                "Origin": "https://www.barburrito.co.uk",
                "Alt-Used": "www.barburrito.co.uk",
                "Connection": "keep-alive",
                "Referer": "https://www.barburrito.co.uk/restaurants",
                "Sec-Fetch-Dest": "empty",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Site": "same-origin",
                "TE": "trailers",
            }

            data = {"action": "mmm_async_content_marker", "id": f"{store_number}"}

            r = session.post(
                "https://www.barburrito.co.uk/wp-admin/admin-ajax.php",
                headers=headers,
                data=data,
            )
            tree = html.fromstring(r.text)
            page_url = "https://www.barburrito.co.uk/restaurants"
            location_name = "".join(tree.xpath("//h2/text()")).replace("'", "’")
            ad = "".join(tree.xpath('//li[@class="adresse"]/strong/text()'))
            a = parse_address(International_Parser(), ad)
            street_address = f"{a.street_address_1} {a.street_address_2}".replace(
                "None", ""
            ).strip()
            state = a.state or "<MISSING>"
            postal = a.postcode or "<MISSING>"
            country_code = "UK"
            city = a.city or "<MISSING>"
            phone = (
                "".join(tree.xpath('//a[contains(@href, "tel")]/text()')) or "<MISSING>"
            )

            session = SgRequests()
            r = session.get(page_url, headers=headers)
            tree = html.fromstring(r.text)
            slugloc = location_name
            if slugloc.find("MANCHESTER") != -1:
                slugloc = slugloc.split()[-1]
            if slugloc.find("GARDENS") != -1:
                slugloc = "MANCHESTER PICCADILLY"

            hours_of_operation = (
                " ".join(
                    tree.xpath(
                        f'//h3[./span[contains(text(), "{slugloc.upper()}")]]/following::span[./span[text()="HOURS"]][1]/following-sibling::span//text()'
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
                raw_address=ad,
            )

            sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)
