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
        day = h.get("dayOfWeek")
        opens = h.get("opens")
        closes = h.get("closes")
        line = f"{day} {opens} - {closes}"
        tmp.append(line)
    hours_of_operation = "; ".join(tmp) or "<MISSING>"
    return hours_of_operation


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.burgerking.com.tr/"
    api_url = "https://www.burgerking.com.tr/restoranlar-subeler"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//a[@class="counter"]')
    for d in div:
        s_p = "".join(d.xpath(".//@href"))
        session = SgRequests()
        r = session.get(s_p, headers=headers)
        tree = html.fromstring(r.text)

        div_1 = tree.xpath("//h1/following-sibling::ul[1]/li/a")
        for d_1 in div_1:
            s_p_1 = "".join(d_1.xpath(".//@href"))

            session = SgRequests()
            r = session.get(s_p_1, headers=headers)
            tree = html.fromstring(r.text)

            div_2 = tree.xpath("//h3/a")
            for d_2 in div_2:

                page_url = "".join(d_2.xpath(".//@href"))

                session = SgRequests()
                r = session.get(page_url, headers=headers)
                tree = html.fromstring(r.text)
                jsblock = "".join(
                    tree.xpath('//script[contains(text(), "latitude")]/text()')
                )
                js = json.loads(jsblock)

                location_name = js.get("name") or "<MISSING>"
                location_type = js.get("@type") or "<MISSING>"
                a = js.get("address")
                street_address = a.get("streetAddress") or "<MISSING>"

                state = a.get("addressRegion") or "<MISSING>"
                postal = a.get("postalCode") or "<MISSING>"
                country_code = a.get("addressCountry") or "<MISSING>"
                city = a.get("addressLocality") or "<MISSING>"
                latitude = js.get("geo").get("latitude") or "<MISSING>"
                longitude = js.get("geo").get("longitude") or "<MISSING>"
                phone = js.get("telephone") or "<MISSING>"
                hours = js.get("openingHoursSpecification")
                hours_of_operation = get_hours(hours)

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
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))) as writer:
        fetch_data(writer)
