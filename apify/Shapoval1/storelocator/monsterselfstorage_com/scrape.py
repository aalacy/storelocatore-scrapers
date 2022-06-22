from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://monsterselfstorage.com/"
    session = SgRequests()
    r = session.get(
        "https://pizza-clients.storage.googleapis.com/production/11ee2cd0-8512-11ec-a9e6-570eaf456782/states-and-cities.json?ignoreCache=1"
    )
    div = str(r.text).split('"locationIds":["')
    tmp = []
    for d in div[1:]:
        tmp.append(d.split('"')[0])
    api_url = "https://www.monsterselfstorage.com/_nuxt/35baf56.js"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    for t in tmp:

        block = r.text.split(f"{t}")[1]
        slug = str(block).split('url_slug:"')[1].split('"')[0].strip()
        page_url = f"https://www.monsterselfstorage.com/locations/{slug}"
        location_name = (
            "Monster Self Storage - "
            + str(block).split(',name:"')[1].split('"')[0].strip()
        )
        street_address = str(block).split('street_1:"')[1].split('"')[0].strip()
        state = str(block).split('state_province:"')[1].split('"')[0].strip()
        postal = str(block).split('postal:"')[1].split('"')[0].strip()
        country_code = "US"
        city = str(block).split('city:"')[1].split('"')[0].strip()
        latitude = str(block).split('lat:"')[1].split('"')[0].strip()
        longitude = str(block).split('lon:"')[1].split('"')[0].strip()
        phone = (
            str(block).split(',phone_number:"')[1].split('"')[0].strip() or "<MISSING>"
        )
        hours = (
            str(block)
            .split("hours:[")[1]
            .split("address")[0]
            .split('type:"office"')[1]
            .strip()
        )
        if hours.find("gate") != -1:
            hours = hours.split("gate")[0].strip()
        hoo = hours.split("id_json_formatted_text")[1:]
        lmp = []
        for h in hoo:
            times = str(h).split('"')[1]
            lmp.append(times)

        hours_of_operation = "; ".join(lmp).replace("; ;", "; ").strip()
        if hours_of_operation.startswith(";"):
            hours_of_operation = "".join(hours_of_operation[1:]).strip()
        if hours_of_operation.endswith(";"):
            hours_of_operation = "".join(hours_of_operation[:-1]).strip()

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
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))) as writer:
        fetch_data(writer)
