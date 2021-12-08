import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def get_hours(hours) -> str:
    tmp = []
    for h in hours:
        day = str(h.get("dayOfWeek"))
        if day.find("/") != -1:
            day = day.split("/")[-1].strip()
        opens = h.get("opens")
        closes = h.get("closes")
        line = f"{day} {opens} - {closes}"
        if opens == closes:
            line = f"{day} Closed"
        tmp.append(line)
    hours_of_operation = "; ".join(tmp) or "<MISSING>"
    return hours_of_operation


def fetch_data(sgw: SgWriter):

    locator_domain = "https://ashleyfurniture.com/"
    api_url = "https://stores.ashleyfurniture.com/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[@class="allstore-CTA"]/a')
    for d in div:
        slug = "".join(d.xpath(".//@href"))
        location_type = slug.replace("/", "").capitalize().strip()
        s_page_url = f"https://stores.ashleyfurniture.com{slug}"
        r = session.get(s_page_url, headers=headers)
        tree = html.fromstring(r.text)
        div = tree.xpath('//div[@class="state-col"]/a')
        for d in div:
            slug = "".join(d.xpath(".//@href"))
            state_url = f"https://stores.ashleyfurniture.com{slug}"
            r = session.get(state_url, headers=headers)
            tree = html.fromstring(r.text)
            div = tree.xpath('//div[@class="storeName"]/a')
            for d in div:
                slug = "".join(d.xpath(".//@href"))
                page_url = f"https://stores.ashleyfurniture.com{slug}"
                session = SgRequests()
                r = session.get(page_url, headers=headers)
                tree = html.fromstring(r.text)
                div = "".join(
                    tree.xpath('//script[contains(text(), "telephone")]/text()')
                )
                j = json.loads(div)
                a = j.get("address")
                street_address = (
                    str(a.get("streetAddress"))
                    .replace("&#39;", "`")
                    .replace("&#194;", "Â")
                    .replace("&#233;", "é")
                    .strip()
                    or "<MISSING>"
                )
                city = a.get("addressLocality") or "<MISSING>"
                state = a.get("addressRegion") or "<MISSING>"
                postal = a.get("postalCode") or "<MISSING>"
                country_code = a.get("addressCountry") or "<MISSING>"
                location_name = j.get("name") or "<MISSING>"
                phone = j.get("telephone") or "<MISSING>"
                hours = j.get("openingHoursSpecification") or "<MISSING>"
                hours_of_operation = "<MISSING>"
                if hours != "<MISSING>":
                    hours_of_operation = get_hours(hours)
                if hours_of_operation.count("Closed") == 7:
                    hours_of_operation = "Closed"
                latitude = j.get("geo").get("latitude") or "<MISSING>"
                longitude = j.get("geo").get("longitude") or "<MISSING>"

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
                )

                sgw.write_row(row)

    api_url = "https://stores.ashleyfurniture.com/sitemap.xml"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.content)
    div = tree.xpath(
        '//url/loc[not(contains(text(), "https://stores.ashleyfurniture.com/store/us/"))]'
    )
    for d in div:

        page_url = "".join(d.xpath(".//text()"))
        if page_url.count("/") != 8:
            continue

        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)
        div = "".join(tree.xpath('//script[contains(text(), "telephone")]/text()'))
        j = json.loads(div)
        a = j.get("address")
        street_address = (
            str(a.get("streetAddress"))
            .replace("&#39;", "`")
            .replace("&#194;", "Â")
            .replace("&#233;", "é")
            .strip()
            or "<MISSING>"
        )
        city = a.get("addressLocality") or "<MISSING>"
        state = a.get("addressRegion") or "<MISSING>"
        postal = a.get("postalCode") or "<MISSING>"
        country_code = a.get("addressCountry") or "<MISSING>"
        location_name = j.get("name") or "<MISSING>"
        phone = j.get("telephone") or "<MISSING>"
        hours = j.get("openingHoursSpecification") or "<MISSING>"
        hours_of_operation = "<MISSING>"
        if hours != "<MISSING>":
            hours_of_operation = get_hours(hours)
        if hours_of_operation.count("Closed") == 7:
            hours_of_operation = "Closed"
        latitude = j.get("geo").get("latitude") or "<MISSING>"
        longitude = j.get("geo").get("longitude") or "<MISSING>"

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
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(
            SgRecordID({SgRecord.Headers.PAGE_URL, SgRecord.Headers.LOCATION_TYPE})
        )
    ) as writer:
        fetch_data(writer)
