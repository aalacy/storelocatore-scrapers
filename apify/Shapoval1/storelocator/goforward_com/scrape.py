import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://goforward.com/"
    api_url = "https://goforward.com/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    jsblock1 = (
        "".join(tree.xpath('//script[contains(text(), "window.Clinics={")]/text()'))
        .split("window.Clinics=")[1]
        .strip()
    )
    js = json.loads(jsblock1)
    jsblock2 = (
        "".join(tree.xpath('//script[contains(text(), "window.Pages=")]/text()'))
        .split("window.Pages=")[1]
        .strip()
    )
    jsblock3 = (
        "".join(tree.xpath('//script[contains(text(), "window.Contentful=")]/text()'))
        .split("window.Contentful=")[1]
        .strip()
    )
    js1 = json.loads(jsblock2)
    for j in js["resources"]:
        a = j.get("clinic")
        if not a.get("address"):
            continue

        page_url = "<MISSING>"
        location_name = a.get("name")
        if location_name == "SB1":
            continue
        street_address = (
            ";".join(a.get("address").get("lines"))
            .replace("Westfield UTC,", "")
            .strip()
        )
        if street_address.find(";") != -1 and street_address.find("1435") == -1:
            street_address = street_address.split(";")[1].strip()
        street_address = street_address.replace(";", " ").strip()
        state = a.get("address").get("region")
        postal = a.get("address").get("post_code")
        country_code = a.get("address").get("country")
        city = a.get("address").get("locality")
        store_number = a.get("id")
        latitude = a.get("address").get("latitude") or "<MISSING>"
        longitude = a.get("address").get("longitude") or "<MISSING>"
        try:
            phone = a.get("phones")[0].get("number")
        except:
            phone = "<MISSING>"
        for k in js1.values():
            ids = k.get("id") or "<MISSING>"
            if ids == location_name:
                page_url = f"https://goforward.com{k.get('path')}"
                location_name = k.get("title")
        if page_url == "<MISSING>":
            continue
        if phone == "<MISSING>" and location_name == "Forward | Long Island":
            phone = "(833) 334-6393"
        hours_of_operation = "<MISSING>"

        s_js = json.loads(jsblock3)
        try:
            cms = s_js.get("TrialsHFFUnlockMyProgramVariant").get("components")
        except:
            cms = "<MISSING>"
        if cms != "<MISSING>":
            for c in cms:
                name = c.get("name")
                if name != "ForwardLocations":
                    continue
                cms = c.get("data").get("comingSoonLocations").get("locations")
                slug_cms = str(location_name).split("|")[1].strip()
                if slug_cms in cms:
                    hours_of_operation = "Coming Soon"

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
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)
