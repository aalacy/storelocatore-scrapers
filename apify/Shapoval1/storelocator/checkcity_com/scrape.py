import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.checkcity.com"
    api_url = "https://www.checkcity.com/locations"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//a[text()="Store Locations"]')
    for d in div:
        slug = "".join(d.xpath(".//@href"))
        spage_url = f"{locator_domain}{slug}"

        session = SgRequests()
        r = session.get(spage_url, headers=headers)
        tree = html.fromstring(r.text)

        block = tree.xpath("//p[./a]")
        for b in block:
            sslug = "".join(b.xpath(".//a/@href"))
            page_url = f"{locator_domain}{sslug}"

            session = SgRequests()
            r = session.get(page_url, headers=headers)
            tree = html.fromstring(r.text)

            location_name = (
                "".join(tree.xpath('//div[@class="check-city-state"]/div/text()'))
                .replace("|", "")
                .replace("\n", "")
                .strip()
            )
            street_address = "<MISSING>"
            phone = "<MISSING>"
            state = "<MISSING>"
            postal = "<MISSING>"
            country_code = "US"
            city = "<MISSING>"
            map_link = "".join(tree.xpath("//iframe/@src"))
            try:
                latitude = map_link.split("!3d")[1].strip().split("!")[0].strip()
                longitude = map_link.split("!2d")[1].strip().split("!")[0].strip()
            except:
                latitude, longitude = "<MISSING>", "<MISSING>"
            if latitude == "<MISSING>":
                latitude = map_link.split("@")[1].split(",")[0].strip()
                longitude = map_link.split("@")[1].split(",")[1].strip()
            hours_of_operation = "<MISSING>"
            api_url = "".join(tree.xpath('//script[contains(@src, "entity_id")]/@src'))
            r = session.get(api_url)
            try:
                block = r.text.split("Yext._embed(")[1]
            except:
                continue
            block = "".join(block[:-1]).strip()
            js = json.loads(block)
            for j in js["entities"]:
                a = j.get("attributes")
                city = a.get("address.city") or "<MISSING>"
                street_address = a.get("address1") or "<MISSING>"
                state = a.get("address.region") or "<MISSING>"
                postal = a.get("address.postalCode") or "<MISSING>"
                hours_of_operation = " ".join(a.get("hours")) or "<MISSING>"
                phone = a.get("mainPhone") or "<MISSING>"

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
                raw_address=f"{street_address} {city}, {state} {postal}",
            )

            sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))) as writer:
        fetch_data(writer)
