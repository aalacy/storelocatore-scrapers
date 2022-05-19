from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def get_hours(hours) -> str:
    tmp = []
    for h in hours:
        try:
            day = " ".join(h.get("dayOfWeek"))
        except:
            day = h.get("dayOfWeek")
        time = f"{h.get('opens')} - {h.get('closes')}"
        line = f"{day} {time}"
        tmp.append(line)
    hours_of_operation = "; ".join(tmp) or "<MISSING>"
    return hours_of_operation


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.columbia.com/"
    api_url = "https://stores.columbia.com/"
    session = SgRequests(verify_ssl=False)

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    jsblock = "".join(
        tree.xpath(
            '//div[@class="hosted-domain-location-index"]/preceding::script[@type="application/ld+json"][1]/text()'
        )
    ).strip()

    js = eval(jsblock)

    for j in js:
        a = j.get("address")
        page_url = "".join(j.get("url")).replace("\\", "").strip()
        location_name = "".join(j.get("name"))
        if location_name.find("Permanently Closed") != -1:
            continue
        street_address = a.get("streetAddress")
        state = a.get("addressRegion")
        postal = "".join(a.get("postalCode"))
        country_code = "CA"
        if postal.isdigit():
            country_code = "US"
        city = a.get("addressLocality")
        store_number = "<MISSING>"
        if location_name.find("#") != -1:
            store_number = location_name.split("#")[1].strip()
        if store_number.find(" ") != -1:
            store_number = store_number.split(" ")[0].strip()
        if store_number == "<MISSING>":
            store_number = location_name.split("Store")[1].split()[0].strip()
        phone = j.get("telephone")
        session = SgRequests(verify_ssl=False)
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)

        jsbl = (
            "".join(tree.xpath('//head//script[@type="application/ld+json"]/text()'))
            .replace("true", "True")
            .strip()
        )
        info = eval(jsbl)

        latitude = info.get("geo").get("latitude")
        longitude = info.get("geo").get("longitude")
        hours = info.get("openingHoursSpecification") or "<MISSING>"
        hours_of_operation = "<MISSING>"
        if hours != "<MISSING>":
            hours_of_operation = get_hours(hours)
        if location_name.find("Temporarily Closed") != -1:
            hours_of_operation = "Temporarily Closed"
        if hours_of_operation.find("; None ") != -1:
            hours_of_operation = hours_of_operation.split("; None ")[0].strip()
        cms = "".join(tree.xpath('//h2[contains(text(), "OPENING SOON")]/text()'))
        if cms:
            hours_of_operation = "Coming Soon"
        if hours_of_operation == "None 00:00 - 00:00":
            hours_of_operation = "Closed"
        location_type = "Brand Stores"
        if location_name.find("Employee Store") != -1:
            location_type = "Invite Only s"
        if location_name.find("Factory Store") != -1:
            location_type = "Factory Outlets"

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
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)
