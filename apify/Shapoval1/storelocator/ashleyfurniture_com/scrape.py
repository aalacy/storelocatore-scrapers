import json
import time
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
    api_urls = [
        "https://stores.ashleyfurniture.com/store/",
        "https://stores.ashleyfurniture.com/outlet/",
    ]
    for api_url in api_urls:
        session = SgRequests()
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
        }
        r = session.get(api_url, headers=headers)
        tree = html.fromstring(r.text)
        div = tree.xpath('//div[@class="state-col"]/a')
        for d in div:
            slug = "".join(d.xpath(".//@href"))
            state_url = f"https://stores.ashleyfurniture.com{slug}"
            if api_url.find("outlet") != -1:
                slug = "".join(d.xpath(".//@href")).split("/")[-2].strip()
                state_url = f"https://stores.ashleyfurniture.com/outlet/{slug}/"
            r = session.get(state_url, headers=headers)
            tree = html.fromstring(r.text)
            div = tree.xpath('//div[@class="storeName"]')
            for d in div:
                slug = "".join(d.xpath(".//@href"))
                page_url = f"https://stores.ashleyfurniture.com{slug}"
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
                    .replace("&amp;", "&")
                    .strip()
                    or "<MISSING>"
                )
                if street_address == "<MISSING>":
                    continue
                city = a.get("addressLocality") or "<MISSING>"
                city = (
                    str(city)
                    .replace("&#241;", "ñ")
                    .replace("&#233;", "é")
                    .replace("&#193;", "Á")
                    .replace("&#243;", "ó")
                    .replace("&#225;", "á")
                    .replace("&#246;", "ö")
                    .replace("&#220;", "Ü")
                    .replace(",", "")
                    .strip()
                )
                state = a.get("addressRegion") or "<MISSING>"
                if state.isdigit():
                    state = "<MISSING>"
                postal = a.get("postalCode") or "<MISSING>"
                country_code = a.get("addressCountry") or "<MISSING>"
                location_name = j.get("name") or "<MISSING>"
                location_name = (
                    str(location_name)
                    .replace("&#241;", "ñ")
                    .replace("&#233;", "é")
                    .replace("&#193;", "Á")
                    .replace("&#243;", "ó")
                    .replace("&#225;", "á")
                    .replace("&#246;", "ö")
                    .replace("&#220;", "Ü")
                    .strip()
                )
                phone = j.get("telephone") or "<MISSING>"
                hours = j.get("openingHoursSpecification") or "<MISSING>"
                hours_of_operation = "<MISSING>"
                if hours != "<MISSING>":
                    hours_of_operation = get_hours(hours)
                if hours_of_operation.count("Closed") == 7:
                    hours_of_operation = "Closed"
                latitude = j.get("geo").get("latitude") or "<MISSING>"
                longitude = j.get("geo").get("longitude") or "<MISSING>"
                location_type = "<MISSING>"
                if api_url.find("/store/") != -1:
                    location_type = "store"
                if api_url.find("/outlet/") != -1:
                    location_type = "outlet"

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

    locator_domain = "https://ashleyfurniture.com/"

    api_url = "https://stores.ashleyfurniture.com/sitemap.xml"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    session = SgRequests()
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.content)
    div = tree.xpath("//url/loc")
    for d in div:

        page_url = "".join(d.xpath(".//text()"))
        if page_url.count("/") < 7:
            continue
        if page_url.find("/us/") != -1:
            continue
        r = session.get(page_url, headers=headers)
        try:
            tree = html.fromstring(r.text)
        except:
            try:
                time.sleep(5)
                tree = html.fromstring(r.text)
            except:
                continue
        div = "".join(tree.xpath('//script[contains(text(), "telephone")]/text()'))
        j = json.loads(div)
        a = j.get("address")
        street_address = (
            str(a.get("streetAddress"))
            .replace("&#39;", "`")
            .replace("&#194;", "Â")
            .replace("&#233;", "é")
            .replace("&amp;", "&")
            .strip()
            or "<MISSING>"
        )
        if street_address == "<MISSING>":
            continue
        city = a.get("addressLocality") or "<MISSING>"
        city = (
            str(city)
            .replace("&#241;", "ñ")
            .replace("&#233;", "é")
            .replace("&#193;", "Á")
            .replace("&#243;", "ó")
            .replace("&#225;", "á")
            .replace("&#246;", "ö")
            .replace("&#220;", "Ü")
            .replace(",", "")
            .strip()
        )
        state = a.get("addressRegion") or "<MISSING>"
        if state.isdigit():
            state = "<MISSING>"
        postal = a.get("postalCode") or "<MISSING>"
        country_code = a.get("addressCountry") or "<MISSING>"
        location_name = j.get("name") or "<MISSING>"
        location_name = (
            str(location_name)
            .replace("&#241;", "ñ")
            .replace("&#233;", "é")
            .replace("&#193;", "Á")
            .replace("&#243;", "ó")
            .replace("&#225;", "á")
            .replace("&#246;", "ö")
            .replace("&#220;", "Ü")
            .strip()
        )
        phone = j.get("telephone") or "<MISSING>"
        hours = j.get("openingHoursSpecification") or "<MISSING>"
        hours_of_operation = "<MISSING>"
        if hours != "<MISSING>":
            hours_of_operation = get_hours(hours)
        if hours_of_operation.count("Closed") == 7:
            hours_of_operation = "Closed"
        latitude = j.get("geo").get("latitude") or "<MISSING>"
        longitude = j.get("geo").get("longitude") or "<MISSING>"
        location_type = "store"

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


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(
            SgRecordID({SgRecord.Headers.PAGE_URL, SgRecord.Headers.LOCATION_TYPE})
        )
    ) as writer:
        fetch_data(writer)
