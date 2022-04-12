import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgpostal import parse_address, International_Parser


def get_street(line):
    adr = parse_address(International_Parser(), line)
    adr1 = adr.street_address_1 or ""
    adr2 = adr.street_address_2 or ""
    street = f"{adr1} {adr2}".strip()

    return street


def get_hours(page_url):
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)

    hours = ";".join(
        tree.xpath(
            "//ul[@class='hours__list' and .//p[contains(text(),'Dinner') or contains(text(), 'DINNER')]]//li[contains(@class, 'hours')]/text()"
        )
    ).strip()
    lunch = (
        ";".join(
            tree.xpath(
                "//p[contains(text(),'Lunch')]/following-sibling::ul[1]/li/text()"
            )
        ).strip()
        or ""
    )

    if lunch:
        out = f"{hours};Lunch: {lunch}"
    else:
        out = hours

    return out


def fetch_data(sgw: SgWriter):
    api = "https://fogodechao.com/locations/"
    r = session.get(api, headers=headers)
    tree = html.fromstring(r.text)
    text = "".join(tree.xpath("//script[contains(text(), 'locationsData =')]/text()"))
    text = text.split("locationsData =")[1].strip()[:-1]
    js = json.loads(text)

    for store_number, j in js.items():
        location_name = j.get("title") or ""
        if "COMING" in location_name or "OPENS" in location_name:
            continue

        street_address = j.get("address1") or ""
        st = j.get("city_state") or ""
        city, state = st.split(", ")[:2]
        postal = str(j.get("address2")).split()[-1].replace(".", "")
        country_code = j.get("region") or ""
        country_code = country_code.replace("-Canada", "").strip()
        if country_code != "US":
            street_address = get_street(street_address)
        slug = j.get("url")
        page_url = f"https://fogodechao.com{slug}"
        phone = j.get("phone")
        latitude = j.get("lat")
        longitude = j.get("lng")
        hours_of_operation = get_hours(page_url)

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code=country_code,
            latitude=latitude,
            longitude=longitude,
            phone=phone,
            store_number=store_number,
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://fogodechao.com/"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:97.0) Gecko/20100101 Firefox/97.0",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
