from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgselenium.sgselenium import SgChrome
import ssl

ssl._create_default_https_context = ssl._create_unverified_context


def get_states():
    with SgChrome() as fox:
        fox.get(
            "https://www.vodacom.cd/particulier/assisstance/nos-vodashops/nos-vodashops"
        )
        source = fox.page_source
    tree = html.fromstring(source)

    return tree.xpath("//markdown//a/@href")


def get_additional():
    data = dict()
    states = get_states()
    for state in states:
        with SgChrome() as fox:
            fox.get(f"{locator_domain}{state}")
            source = fox.page_source

        tree = html.fromstring(source)
        tables = tree.xpath("//markdown[@_ngcontent-c7]/table")
        for table in tables:
            key = "".join(table.xpath(".//th/text()")).strip()
            try:
                phone = table.xpath(
                    ".//td[contains(text(), 'phone')]/following-sibling::td/text()"
                )[0].strip()
            except:
                phone = SgRecord.MISSING

            _tmp = []
            hours = table.xpath(
                ".//tr[./td[contains(text(), 'Heures')]]/td[2]/text()|.//tr[./td[contains(text(), 'Heures')]]/following-sibling::tr/td[2]/text()"
            )
            for h in hours:
                if h[0].isdigit() or "phone" in h:
                    continue
                _tmp.append(h)
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
        location_name = j.get("nameStructure")
        street_address = j.get("address") or ""
        if "(" in street_address:
            street_address = street_address.split("(")[0].strip()
        city = j.get("city")
        state = j.get("region")
        location_type = j.get("shopType")
        latitude = j.get("lat")
        longitude = j.get("lon")
        try:
            phone = additional[location_name]["phone"]
        except:
            phone = SgRecord.MISSING
        try:
            hours_of_operation = additional[location_name]["hoo"]
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
