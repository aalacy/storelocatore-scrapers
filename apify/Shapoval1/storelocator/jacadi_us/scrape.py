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
        days = h.get("dayOfWeek")
        opens = h.get("opens")
        closes = h.get("closes")
        line = f"{days} {opens} - {closes}".replace("None", "Closed")
        tmp.append(line)
    hours_of_operation = "; ".join(tmp) or "<MISSING>"
    return hours_of_operation


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.jacadi.us"
    api_url = "https://www.jacadi.us/store-finder"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath("//h3/following-sibling::ul/li/a")
    for d in div:
        slug = "".join(d.xpath(".//@href"))
        spage_url = f"https://www.jacadi.us{slug}"
        session = SgRequests()
        r = session.get(spage_url, headers=headers)
        tree = html.fromstring(r.text)
        div = tree.xpath('//a[contains(text(), "Store details")]')
        for d in div:
            sslug = "".join(d.xpath(".//@href"))
            page_url = f"https://www.jacadi.us{sslug}"

            session = SgRequests()
            r = session.get(page_url, headers=headers)
            tree = html.fromstring(r.text)
            jsblock = "".join(tree.xpath('//script[contains(text(), "geo")]/text()'))

            js = json.loads(jsblock)
            a = js.get("address")
            location_name = js.get("name")
            location_type = js.get("@type")
            street_address = a.get("streetAddress")
            state = "<MISSING>"

            postal = a.get("postalCode")
            if postal == "0" or postal == "-":
                postal = "<MISSING>"
            country_code = a.get("addressCountry")
            city = "".join(a.get("addressLocality"))
            if city.find(",") != -1:
                state = city.split(",")[1].strip()
                city = city.split(",")[0].strip()
            if country_code == "CA" and city.find(" ") != -1:
                state = city.split()[1].strip()
                city = city.split()[0].strip()
            store_number = page_url.split("/")[-1].strip()
            latitude = js.get("geo").get("latitude")
            longitude = js.get("geo").get("longitude")
            phone = js.get("telephone") or "<MISSING>"
            if phone == "0":
                phone = "<MISSING>"
            hours = js.get("openingHoursSpecification") or "<MISSING>"
            hours_of_operation = "<MISSING>"
            if hours != "<MISSING>":
                hours_of_operation = get_hours(hours)
            if latitude == "0" or latitude == "0.0":
                latitude, longitude = "<MISSING>", "<MISSING>"
            if state == "-":
                state = "<MISSING>"
            if postal == "0":
                postal = "<MISSING>"
            if postal[0] == postal[1] == postal[2] == "0":
                postal = "<MISSING>"
            if phone[0] == phone[1] == phone[2] == "0":
                phone = "<MISSING>"

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
            SgRecordID({SgRecord.Headers.STREET_ADDRESS, SgRecord.Headers.STORE_NUMBER})
        )
    ) as writer:
        fetch_data(writer)
