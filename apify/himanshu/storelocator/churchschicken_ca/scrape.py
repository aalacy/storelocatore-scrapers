import json
import httpx
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import International_Parser, parse_address


def fetch_data(sgw: SgWriter):
    with SgRequests() as http:
        locator_domain = "https://churchschicken.ca/"
        api_urls = [
            "https://alberta.churchstexaschicken.com/Location",
            "https://ontario.churchstexaschicken.com/Location",
        ]
        for api_url in api_urls:

            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
            }
            r = http.get(url=api_url, headers=headers)
            assert isinstance(r, httpx.Response)
            assert 200 == r.status_code
            tree = html.fromstring(r.text)
            div = tree.xpath('//div[@id="M_2"]')
            for d in div:

                slug = "".join(d.xpath('.//p[@class="h4"]/a/@href'))
                page_url = f"{api_url.split('/Location')[0].strip()}{slug}"
                location_name = (
                    "".join(d.xpath('.//p[@class="h4"]/a/text()'))
                    .replace("\n", "")
                    .strip()
                )
                ad = (
                    "".join(d.xpath('.//p[@class="h4"]/following-sibling::p[1]/text()'))
                    .replace("\n", "")
                    .strip()
                )

                a = parse_address(International_Parser(), ad)
                street_address = (
                    f"{a.street_address_1} {a.street_address_2}".replace(
                        "None", ""
                    ).strip()
                    or "<MISSING>"
                )
                state = a.state or "<MISSING>"
                if state == "<MISSING>" and page_url.find("ontario") != -1:
                    state = "ON"
                postal = a.postcode or "<MISSING>"
                country_code = "CA"
                city = a.city or "<MISSING>"
                phone = (
                    "".join(
                        d.xpath(
                            './/span[contains(text(), "Mobile Number:")]/following-sibling::text()'
                        )
                    )
                    .replace("\n", "")
                    .strip()
                    or "<MISSING>"
                )
                hours_of_operation = (
                    " ".join(
                        d.xpath(
                            './/span[contains(text(), "Opening Daily:")]/following-sibling::text()'
                        )
                    )
                    .replace("\n", "")
                    .strip()
                    or "<MISSING>"
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
                    store_number=SgRecord.MISSING,
                    phone=phone,
                    location_type=SgRecord.MISSING,
                    latitude=SgRecord.MISSING,
                    longitude=SgRecord.MISSING,
                    hours_of_operation=hours_of_operation,
                    raw_address=ad,
                )

                sgw.write_row(row)

    locator_domain = "https://www.churchschicken.ca/"
    api_url = "https://www.churchschicken.ca/british-columbia/locations/"
    with SgRequests() as http:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
        }
        r = http.get(url=api_url, headers=headers)
        assert isinstance(r, httpx.Response)
        assert 200 == r.status_code
        tree = html.fromstring(r.text)
        js_block = (
            "".join(tree.xpath('//script[contains(text(), "var map2")]/text()'))
            .split('"places":')[1]
            .split(',"map_tabs"')[0]
            .strip()
        )
        js = json.loads(js_block)
        for j in js:
            info = j.get("content")
            b = html.fromstring(info)
            a = j.get("location")
            location_name = j.get("title") or "<MISSING>"
            page_url = a.get("redirect_custom_link")
            info_lst = b.xpath("//text()")
            info_lst = list(filter(None, [c.strip() for c in info_lst]))
            street_address = "".join(info_lst[0]).strip()
            if (
                street_address.find("Centre") != -1
                or street_address.find("NOW OPEN") != -1
            ):
                street_address = "".join(info_lst[1]).strip()
            state = a.get("state")
            postal = a.get("postal_code")
            country_code = a.get("country")
            city = a.get("city")
            store_number = j.get("id") or "<MISSING>"
            latitude = a.get("lat")
            longitude = a.get("lng")
            r = http.get(url=page_url, headers=headers)
            assert isinstance(r, httpx.Response)
            assert 200 == r.status_code
            tree = html.fromstring(r.text)

            phone = (
                "".join(
                    tree.xpath(
                        '//div[./i[contains(@class, "fa-phone")]]/following-sibling::p//text()'
                    )
                )
                or "<MISSING>"
            )
            hours_of_operation = (
                " ".join(
                    tree.xpath(
                        '//div[./i[contains(@class, "fa-clock")]]/following-sibling::p//text()'
                    )
                )
                .replace("\n", "")
                .strip()
            )
            hours_of_operation = (
                " ".join(hours_of_operation.split())
                .replace("Drive thru 24 hours", "")
                .replace("24 hour drive thru", "")
                .replace("No drive thru / pick up window", "")
                .replace("24 hour pick up window", "")
                or "<MISSING>"
            )
            if hours_of_operation.find("Pick up") != -1:
                hours_of_operation = hours_of_operation.split("Pick up")[0].strip()
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
            )

            sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))) as writer:
        fetch_data(writer)
