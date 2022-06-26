import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.mattressland.com"
    api_url = "https://www.mattressland.com/contacts"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    jsblock = "".join(tree.xpath('//script[@data-from="cms-api"]/text()'))
    js = json.loads(jsblock)

    for j in js["@graph"]:
        a = j.get("address")
        location_type = j.get("@type")
        if location_type != "Store":
            continue
        street_address = str(a.get("streetAddress"))
        state = a.get("addressRegion")
        postal = a.get("postalCode")
        country_code = a.get("addressCountry")
        city = a.get("addressLocality")
        text = "".join(j.get("hasMap"))
        try:
            if text.find("ll=") != -1:
                latitude = text.split("ll=")[1].split(",")[0]
                longitude = text.split("ll=")[1].split(",")[1].split("&")[0]
            else:
                latitude = text.split("@")[1].split(",")[0]
                longitude = text.split("@")[1].split(",")[1]
        except IndexError:
            latitude, longitude = "<MISSING>", "<MISSING>"
        slug_lat = "".join(latitude[:6])

        phone = j.get("telephone")
        hours_of_operation = " ".join(j.get("openingHours"))
        session = SgRequests()
        r = session.get("https://www.mattressland.com/contacts", headers=headers)
        tree = html.fromstring(r.text)
        page_url = "".join(
            tree.xpath(
                f'//*[contains(@data-href, "{slug_lat}")]/following::*[text()="Contact this location"][1]/@data-href'
            )
        )
        location_name = "".join(
            tree.xpath(
                f'//*[contains(@data-href, "{slug_lat}")]/preceding::h3[1]/text()'
            )
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
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)
