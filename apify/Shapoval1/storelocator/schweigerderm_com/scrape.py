import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.schweigerderm.com"
    api_url = "https://www.schweigerderm.com/locations/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//a[@class="loc-link"]')
    for d in div:

        page_url = "".join(d.xpath(".//@href"))

        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)

        id_key = (
            "".join(tree.xpath('//script[contains(text(), "var et_post_id=")]/text()'))
            .split("var et_post_id=")[1]
            .split(";")[0]
            .replace("'", "")
            .strip()
        )

        r = session.get(
            f"https://knowledgetags.yextpages.net/embed?key=LshOHdaZaCFDUjs4KsmkvqHaDYrNMnI-a56D78q6U2rvn5uE051HZyS2URSiQw5x&account_id=6629542544138241976&location_id={id_key}",
            headers=headers,
        )
        js_block = r.text.split("Yext._embed(")[1]
        js_block = "".join(js_block[:-1])
        js = json.loads(js_block)
        b = js.get("entities")
        for j in b:
            k = j.get("attributes")
            location_name = k.get("name") or "<MISSING>"
            types = k.get("schemaTypes")
            tmp = []
            for t in types:
                line = f"{t}"
                tmp.append(line)
            location_type = ", ".join(tmp) or "<MISSING>"
            street_address = (
                f"{k.get('address1')} {k.get('address2')}".replace("None", "")
                .replace("Hackensack Medical Plaza", "")
                .replace("Holy Redeemer Medical Office Building", "")
                .strip()
                or "<MISSING>"
            )
            state = k.get("state") or "<MISSING>"
            postal = k.get("zip") or "<MISSING>"
            country_code = "US"
            city = k.get("city") or "<MISSING>"
            latitude = k.get("yextDisplayLat") or "<MISSING>"
            longitude = k.get("yextDisplayLng") or "<MISSING>"
            phone = k.get("phone") or "<MISSING>"
            hours = k.get("hours")
            hrs = []
            for h in hours:
                line = f"{h}"
                hrs.append(line)
            hours_of_operation = "; ".join(hrs) or "<MISSING>"

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
                raw_address=f"{street_address} {city}, {state} {postal}",
            )

            sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))) as writer:
        fetch_data(writer)
