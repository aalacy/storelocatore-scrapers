from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def get_hoo(page_url, ph=False):
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)

    _tmp = []
    hours = tree.xpath(
        "//div[div/h2/span[contains(text(), 'Openingsuren')]]/following-sibling::div//text()"
    )
    for h in hours:
        if not h.strip() or "WELKOM" in h or "open" in h:
            continue
        if "jouw" in h.lower():
            break
        _tmp.append(" ".join(h.split()))

    hoo = ";".join(_tmp)
    try:
        phone = tree.xpath(
            "//div[@class='elementor-widget-wrap']//a[contains(@href, 'tel:')]/text()"
        )[0].strip()
    except IndexError:
        phone = SgRecord.MISSING

    if ph:
        return hoo, phone
    else:
        return hoo


def fetch_data(sgw: SgWriter):
    api = "https://www.bikerepublic.be/module/storelocator/storefinder?ajax=1&all=1"
    r = session.get(api, headers=headers)
    tree = html.fromstring(r.content)
    divs = tree.xpath("//marker")

    for d in divs:
        location_name = "".join(d.xpath("./@name")).strip()
        line = "".join(d.xpath("./@address")).split("<br />")
        if len(line) == 3:
            line.pop()

        raw_address = ", ".join(line)
        street_address = line.pop(0)
        zc = line.pop()
        postal = zc.split()[0]
        city = zc.replace(postal, "").strip()
        country_code = "BE"
        store_number = "".join(d.xpath("./@id_store"))
        page_url = "".join(d.xpath("./@link"))
        phone = "".join(d.xpath("./@phone"))
        latitude = "".join(d.xpath("./@lat"))
        longitude = "".join(d.xpath("./@lng"))

        if phone:
            hours_of_operation = get_hoo(page_url)
        else:
            hours_of_operation, phone = get_hoo(page_url, ph=True)

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            zip_postal=postal,
            country_code=country_code,
            latitude=latitude,
            longitude=longitude,
            phone=phone,
            store_number=store_number,
            raw_address=raw_address,
            hours_of_operation=hours_of_operation,
            locator_domain=locator_domain,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.bikerepublic.be/"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:97.0) Gecko/20100101 Firefox/97.0",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
