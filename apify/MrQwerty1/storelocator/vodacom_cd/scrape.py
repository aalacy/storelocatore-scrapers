from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def get_states():
    urls = []
    r = session.get(
        "https://www.vodacom.cd/integration/cms/getpage/portal?url=/particulier/assisstance/nos-vodashops/nos-vodashops"
    )
    text = r.json()["response"]["page"]["summaryMarkdown"][1][0]["content"].split(
        "**]("
    )[1:]
    for t in text:
        url = t.split(")")[0]
        urls.append(url)

    return urls


def get_additional():
    data = dict()
    states = get_states()

    for state in states:
        r = session.get(
            f"https://www.vodacom.cd/integration/cms/getpage/portal?url=/{state}"
        )
        js = r.json()["response"]["page"]["summaryMarkdown"][1]
        for j in js:
            text = j.get("content") or ""
            if "|" not in text:
                continue
            line = text.split("|")
            line = list(
                filter(
                    None,
                    [
                        li.replace("<br/>", "")
                        .replace("---", "")
                        .replace("<hr/>", "")
                        .strip()
                        for li in line
                    ],
                )
            )
            key = line.pop(0).lower()

            _tmp = []
            cnt = 0
            phone = SgRecord.MISSING
            recording = False
            for li in line:
                if recording:
                    _tmp.append(li)
                li = li.lower()

                if "dimanche" in li:
                    recording = False

                if "téléphone" in li:
                    if cnt + 1 != len(line):
                        phone = line[cnt + 1]
                    else:
                        phone = li.split(":")[-1].strip()

                if "heures" in li:
                    recording = True
                cnt += 1

            if not phone[-1].isdigit():
                phone = SgRecord.MISSING

            hoo = ";".join(_tmp)

            data[key] = {"phone": phone, "hoo": hoo}

    return data


def fetch_data(sgw: SgWriter):
    api = "https://www.vodacom.cd/integration/drcportal/store_locator/portal"
    page_url = (
        "https://www.vodacom.cd/particulier/assisstance/nos-vodashops/find-vodashops"
    )
    data = '{\n  "method": "findNearestStore",\n  "longitude": 49.6074752,\n  "latitude": 34.5276416,\n  "source": "portal"\n}'
    r = session.post(api, data=data)
    js = r.json()["response"]["stores"]
    additional = get_additional()

    for j in js:
        location_name = j.get("nameStructure") or ""
        street_address = j.get("address") or ""
        if "(" in street_address:
            street_address = street_address.split("(")[0].strip()
        city = j.get("city")
        state = j.get("region")
        location_type = j.get("shopType")
        latitude = j.get("lat")
        longitude = j.get("lon")
        key = location_name.lower()
        try:
            phone = additional[key]["phone"]
        except:
            phone = SgRecord.MISSING
        try:
            hours_of_operation = additional[key]["hoo"]
        except:
            hours_of_operation = SgRecord.MISSING

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            country_code="CD",
            phone=phone,
            location_type=location_type,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
            locator_domain=locator_domain,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    locator_domain = "https://www.vodacom.cd/"
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.LOCATION_NAME}))
    ) as writer:
        fetch_data(writer)
