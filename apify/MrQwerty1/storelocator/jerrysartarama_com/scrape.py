import json

from lxml import html

from sgrequests import SgRequests

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


def get_hours(page_url):
    session = SgRequests()
    r = session.get(page_url)
    tree = html.fromstring(r.text)
    hours = tree.xpath(
        "//h3[contains(text(), 'Hours')]/following-sibling::p[1]//text()"
    )
    if not hours:
        hours = tree.xpath(
            "//div[@class='small-24 medium-8 contact-info large-9 columns text-center ']/div[@class='adr']/following-sibling::p//text()"
        )
    hours = list(filter(None, [h.strip() for h in hours]))
    hoo = ";".join(hours).replace(":;", ":") or "<MISSING>"
    if hoo.startswith("Yes"):
        hoo = ";".join(hoo.split(";")[1:])

    text = "".join(tree.xpath("//p/a[contains(@href, 'map')]/@href"))

    try:
        if text.find("ll=") != -1:
            latitude = text.split("ll=")[1].split(",")[0]
            longitude = text.split("ll=")[1].split(",")[1].split("&")[0]
        elif text.find("@") != -1:
            latitude = text.split("@")[1].split(",")[0]
            longitude = text.split("@")[1].split(",")[1]
        else:
            latitude = text.split("dir/")[1].split(",")[0]
            longitude = text.split("dir/")[1].split(",")[1].split("/")[0]
    except IndexError:
        latitude, longitude = "<MISSING>", "<MISSING>"

    try:
        hoo = tree.xpath("//b[contains(text(), 'OPENING SOON')]//text()")[0]
    except:
        pass

    return latitude, longitude, hoo, r.url


def fetch_data(sgw: SgWriter):
    locator_domain = "https://jerrysartarama.com/"
    api_url = "https://www.jerrysretailstores.com/locations/"

    session = SgRequests()
    r = session.get(api_url)
    tree = html.fromstring(r.text)
    text = "".join(tree.xpath("//script[contains(text(), '@vocab')]/text()"))
    js = json.loads(text)["@graph"]

    for j in js:
        a = j.get("address")
        street_address = a.get("streetAddress") or "<MISSING>"
        city = a.get("addressLocality") or "<MISSING>"
        state = a.get("addressRegion") or "<MISSING>"
        postal = a.get("postalCode") or "<MISSING>"
        country_code = "US"
        store_number = "<MISSING>"
        page_url = j.get("url").replace("/store-location", "")
        if page_url.find("greensboro") != -1:
            page_url = "https://www.jerryswholesalestores.com/greensboro-nc/"
        if "wholesale-club-of-jacksonville" in page_url:
            page_url = "https://www.jerryswholesalestores.com/jacksonville-fl/"
        location_name = j.get("name").replace("&#8217;", "'")
        location_type = "<MISSING>"
        phone = a.get("telephone") or "<MISSING>"
        latitude, longitude, hours_of_operation, page_url = get_hours(page_url)

        if "OPENING SOON" in hours_of_operation:
            continue

        sgw.write_row(
            SgRecord(
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
        )


with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
    fetch_data(writer)
