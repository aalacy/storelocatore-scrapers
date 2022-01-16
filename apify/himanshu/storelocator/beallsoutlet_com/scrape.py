import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://beallsoutlet.com/"
    api_url = "https://stores.beallsoutlet.com/?GA=HP_RibbonFindStore_Ribbon"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    jsblock1 = (
        "".join(tree.xpath('//script[contains(text(), "var map_list_data")]/text()'))
        .split("var map_list_data = ")[1]
        .split("//-->")[0]
        .strip()
    )
    js = json.loads(jsblock1)
    for j in js:
        state = j.get("region")
        url1 = j.get("url")
        session = SgRequests()
        r = session.get(url1, headers=headers)
        tree = html.fromstring(r.text)
        jsblock2 = (
            "".join(
                tree.xpath('//script[contains(text(), "var map_list_data")]/text()')
            )
            .split("var map_list_data = ")[1]
            .split("//-->")[0]
            .strip()
        )
        js = json.loads(jsblock2)
        for j in js:
            page_url = j.get("url")
            city = j.get("city")
            session = SgRequests()
            r = session.get(page_url, headers=headers)
            tree = html.fromstring(r.text)
            jsblock3 = (
                "".join(
                    tree.xpath('//script[contains(text(), "var map_list_data")]/text()')
                )
                .split("var map_list_data = ")[1]
                .split("//-->")[0]
                .strip()
            )
            js = json.loads(jsblock3)
            for j in js:

                location_name = j.get("location_name")
                street_address = f"{j.get('address_1')} {j.get('address_2')}".replace(
                    "The Crossings at Sahuarita", ""
                ).strip()
                postal = j.get("post_code")
                country_code = "US"
                store_number = j.get("fid")
                latitude = j.get("lat")
                longitude = j.get("lng")
                phone = j.get("local_phone")
                try:
                    hours = (
                        str(j.get("hours_sets:primary"))
                        .split('"days":')[1]
                        .split(',"children"')[0]
                        .strip()
                    )
                except:
                    hours = "<MISSING>"
                tmp = []
                if hours != "<MISSING>":
                    hJS = eval(hours)
                    days = [
                        "Sunday",
                        "Monday",
                        "Tuesday",
                        "Wednesday",
                        "Thursday",
                        "Friday",
                        "Saturday",
                    ]
                    for d in days:
                        day = d
                        opens = hJS.get(f"{d}")[0].get("open")
                        closes = hJS.get(f"{d}")[0].get("close")
                        line = f"{day} {opens} - {closes}"
                        tmp.append(line)
                cms = j.get("location_custom_message")
                hours_of_operation = "; ".join(tmp) or "<MISSING>"
                if cms == "Coming Soon":
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
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))) as writer:
        fetch_data(writer)
