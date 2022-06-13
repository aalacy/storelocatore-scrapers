from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://keyes.com/"
    api_url = "https://offices.keyes.com/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)

    js_block = (
        "".join(tree.xpath('//script[contains(text(), "defaultListData ")]/text()'))
        .split("$config.defaultListData = '")[1]
        .split("';")[0]
        .replace("\\", "")
    )
    js_block = js_block.replace(
        '"hours_sets:primary":"', '"hours_sets:primary":\''
    ).replace('","more_info_button"', '\',"more_info_button"')

    js = eval(js_block)
    for j in js:

        page_url = j.get("url")
        if page_url == "https://offices.keyes.com/fl/miami/keyes-offices-v001.html":
            continue
        location_name = j.get("location_name")
        location_type = "Keyes Office"
        street_address = f"{j.get('address_1')} {j.get('address_2') or ''}".replace(
            ", Seabranch Square Plaza", ""
        ).strip()
        phone = j.get("local_phone")
        state = j.get("region")
        postal = j.get("post_code")
        country_code = j.get("country")
        city = j.get("city")
        store_number = j.get("fid")
        latitude = j.get("lat")
        longitude = j.get("lng")
        hours = j.get("hours_sets:primary")
        hours_of_operation = "<MISSING>"
        hour = eval(hours).get("days")
        days = [
            "Sunday",
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
        ]
        tmp = []
        if hour:
            for d in days:
                day = d
                opens = hour.get(f"{d}")
                closes = hour.get(f"{d}")
                if type(opens) == list:
                    opens = hour.get(f"{d}")[0].get("open")
                    closes = hour.get(f"{d}")[0].get("close")
                line = f"{day} {opens} - {closes}"
                tmp.append(line)
            hours_of_operation = (
                "; ".join(tmp).replace("closed - closed", "closed").strip()
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
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))) as writer:
        fetch_data(writer)
