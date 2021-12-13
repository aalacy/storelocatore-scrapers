import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import International_Parser, parse_address


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.jamaicablue.co.uk/"
    api_url = "https://www.jamaicablue.co.uk/find-a-cafe/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[@class="blk-Store-Grid-Item-Content"]')
    for d in div:

        page_url = "".join(d.xpath("./a[1]/@href"))
        location_name = "".join(d.xpath(".//h3/text()"))
        ad = (
            " ".join(d.xpath("./p[1]/text()"))
            .replace("\n", "")
            .replace("\r", "")
            .strip()
        )
        a = parse_address(International_Parser(), ad)
        street_address = f"{a.street_address_1} {a.street_address_2}".replace(
            "None", ""
        ).strip()
        state = a.state or "<MISSING>"
        postal = a.postcode or "<MISSING>"
        country_code = "UK"
        city = a.city or "<MISSING>"
        if "Rushden" in city:
            city = "Rushden"
        phone = (
            " ".join(d.xpath("./p[2]/text()"))
            .replace("\n", "")
            .replace("\r", "")
            .replace("T:", "")
            .strip()
            or "<MISSING>"
        )
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)

        text = "".join(tree.xpath('//a[contains(@href, "maps")]/@href'))
        try:
            if text.find("ll=") != -1:
                latitude = text.split("ll=")[1].split(",")[0]
                longitude = text.split("ll=")[1].split(",")[1].split("&")[0]
            else:
                latitude = text.split("@")[1].split(",")[0]
                longitude = text.split("@")[1].split(",")[1]
        except IndexError:
            latitude, longitude = "<MISSING>", "<MISSING>"
        hours_of_operation = (
            " ".join(
                tree.xpath(
                    '//div[@class="opening-times-item opening-times-text"]/p/text()'
                )
            )
            .replace("\n", "")
            .replace("\r", "")
            .replace("Made to order ends 4pm", "")
            .strip()
            or "<MISSING>"
        )
        js = "".join(tree.xpath('//script[@class="rank-math-schema"]/text()'))
        if js and postal == "<MISSING>":
            j = json.loads(js)
            for a in j["@graph"]:
                aa = a.get("address")
                if not aa:
                    continue
                postal = aa.get("postalCode")
        if js and phone == "<MISSING>":
            j = json.loads(js)
            for a in j["@graph"]:
                try:
                    phone = a.get("contactPoint")[0].get("telephone")
                except:
                    continue

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
            raw_address=ad,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))) as writer:
        fetch_data(writer)
