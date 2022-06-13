import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.atriaseniorliving.com/"
    api_url = "https://www.atriaseniorliving.com/retirement-communities/search-state/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//ul[@id="subpages"]/li/a')
    for d in div:
        state_url = "".join(d.xpath(".//@href"))
        r = session.get(state_url, headers=headers)
        tree = html.fromstring(r.text)
        js_block = (
            "".join(tree.xpath('//script[contains(text(), "CommunityList")]/text()'))
            .split("CommunityList = ")[1]
            .split(";")[0]
            .strip()
        )
        js = json.loads(js_block)
        for j in js["communities"]:

            page_url = j.get("url")
            location_name = j.get("name")
            street_address = f"{j.get('address_1')} {j.get('address_2') or ''}".strip()
            state = j.get("state")
            postal = j.get("zip_code")
            country_code = "US"
            city = j.get("city")
            store_number = j.get("community_number")
            latitude = j.get("latitude")
            longitude = j.get("longitude")
            phone = j.get("phone")

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
                hours_of_operation=SgRecord.MISSING,
                raw_address=f"{street_address} {city}, {state} {postal}",
            )

            sgw.write_row(row)

    api_url = "https://www.atriaretirement.ca/page-sitemap.xml"
    session = SgRequests(verify_ssl=False)
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.content)
    div = tree.xpath('//url/loc[contains(text(), "retirement-communities")]')
    for d in div:
        page_url = "".join(d.xpath(".//text()"))
        if page_url.count("/") != 5:
            continue
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)

        location_name = (
            "".join(tree.xpath('//h1[@itemprop="name"]/text()')) or "<MISSING>"
        )
        street_address = (
            "".join(tree.xpath('//span[@itemprop="streetAddress"]/text()'))
            or "<MISSING>"
        )
        state = (
            "".join(tree.xpath('//span[@itemprop="addressRegion"]/text()'))
            or "<MISSING>"
        )
        postal = (
            "".join(tree.xpath('//span[@itemprop="postalCode"]/text()')) or "<MISSING>"
        )
        country_code = "CA"
        city = (
            "".join(tree.xpath('//span[@itemprop="addressLocality"]/text()'))
            or "<MISSING>"
        )
        store_number = "".join(
            tree.xpath('//meta[@itemprop="community-number"]/@content')
        )
        latitude = (
            "".join(tree.xpath('//script[contains(text(), "LatLng(")]/text()'))
            .split("LatLng(")[1]
            .split(",")[0]
            .strip()
        )
        longitude = (
            "".join(tree.xpath('//script[contains(text(), "LatLng(")]/text()'))
            .split("LatLng(")[1]
            .split(",")[1]
            .split(")")[0]
            .strip()
        )
        phone = (
            "".join(tree.xpath('//span[@itemprop="telephone"]//text()')) or "<MISSING>"
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
            location_type=SgRecord.MISSING,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=SgRecord.MISSING,
            raw_address=f"{street_address} {city}, {state} {postal}",
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))) as writer:
        fetch_data(writer)
