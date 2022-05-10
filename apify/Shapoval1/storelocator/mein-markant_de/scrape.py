import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.mein-markant.de"
    api_url = "https://www.mein-markant.de/mein-markt/unsere-maerkte/"
    session = SgRequests(verify_ssl=False)
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    js_block = (
        "".join(tree.xpath('//script[contains(text(), "oMaerkte")]/text()'))
        .split("var oMaerkte = ")[1]
        .split("}];")[0]
        + "}]"
    )
    js = json.loads(js_block)
    for j in js:

        info_ph = j.get("city")
        p = html.fromstring(info_ph)
        page_url = "https://www.mein-markant.de/mein-markt/unsere-maerkte/"
        location_name = j.get("name") or "<MISSING>"
        location_type = "<MISSING>"
        if j.get("is_nah_frisch_markt") == "1":
            location_type = "Nah&Frisch"
        if j.get("is_nah_frisch_markt") == "0":
            location_type = "Markant"
        street_address = j.get("street") or "<MISSING>"
        postal = j.get("zip") or "<MISSING>"
        country_code = "DE"
        city = j.get("cityRaw") or "<MISSING>"
        store_number = j.get("uid") or "<MISSING>"
        latitude = j.get("lat") or "<MISSING>"
        longitude = j.get("lon") or "<MISSING>"
        phone = "".join(p.xpath('//a[contains(@href, "tel")]/text()'))
        hours_of_operation = "<MISSING>"
        hours = j.get("openings")
        if hours:
            h = html.fromstring(hours)
            hours_of_operation = (
                " ".join(h.xpath("//*//text()")).replace("\n", "").strip()
            )
            hours_of_operation = " ".join(hours_of_operation.split()) or "<MISSING>"

        row = SgRecord(
            locator_domain=locator_domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=SgRecord.MISSING,
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
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STORE_NUMBER}))
    ) as writer:
        fetch_data(writer)
