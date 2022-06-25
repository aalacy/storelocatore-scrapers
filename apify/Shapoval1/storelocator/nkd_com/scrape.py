from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.nkd.com/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0",
    }
    json_data = {
        "query": "{\n                    storePickupLocations {\n                      items {\n                        \n            name\n            latitude\n            longitude\n            city\n            street\n            postCode\n            region\n            description\n            sourceCode\n            countryId\n            phone\n            fax\n            email\n            url\n        \n                      }\n                    }\n                  }",
    }

    r = session.post(
        "https://www.nkd.com/de_de/graphql", headers=headers, json=json_data
    )
    js = r.json()["data"]["storePickupLocations"]["items"]
    for j in js:

        slug = j.get("url")
        page_url = f"https://www.nkd.com/de_de/{slug}"
        location_name = j.get("name") or "<MISSING>"
        street_address = j.get("street") or "<MISSING>"
        state = j.get("region") or "<MISSING>"
        postal = j.get("postCode") or "<MISSING>"
        country_code = j.get("countryId")
        city = j.get("city") or "<MISSING>"
        store_number = j.get("sourceCode")
        latitude = j.get("latitude") or "<MISSING>"
        longitude = j.get("longitude") or "<MISSING>"
        phone = j.get("phone") or "<MISSING>"
        if phone == "-" or phone == "0":
            phone = "<MISSING>"
        hours = "".join(j.get("description")).replace("false", "False")
        js_hours = eval(hours)
        hours_of_operation = "<MISSING>"
        days = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
        tmp = []
        if js_hours:
            for d in days:
                day = str(d).capitalize()
                opens = js_hours.get(f"{d}_from")
                closes = js_hours.get(f"{d}_to")
                line = f"{day} {opens} - {closes}"
                tmp.append(line)
            hours_of_operation = "; ".join(tmp).replace("; Sun None - None", "").strip()

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
            location_type=SgRecord.MISSING,
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
