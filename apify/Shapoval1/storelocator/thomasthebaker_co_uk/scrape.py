from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import International_Parser, parse_address


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.thomasthebaker.co.uk/"
    api_url = "https://www.thomasthebaker.co.uk/include/stores_xml.php?lat=54.180212&lng=-1.202271&radius=10000&limit=0"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.content)
    div = tree.xpath("//store/store")
    for d in div:

        page_url = "https://www.thomasthebaker.co.uk/store-locator.html"
        location_name = "".join(d.xpath(".//@name"))
        ad = "".join(d.xpath(".//@address"))
        a = parse_address(International_Parser(), ad)
        street_address = f"{a.street_address_1} {a.street_address_2}".replace(
            "None", ""
        ).strip()
        state = a.state or "<MISSING>"
        city = a.city or "<MISSING>"
        postal = " ".join(ad.split()[-2:])
        country_code = "UK"
        latitude = "".join(d.xpath(".//@lat"))
        longitude = "".join(d.xpath(".//@lng"))
        phone = "".join(d.xpath(".//@telephone"))
        hours_of_operation = "<MISSING>"
        hours = (
            "".join(d.xpath(".//@opening_times"))
            .replace("NULL", "")
            .replace('"1"', '"Monday"')
            .replace('"2"', '"Tuesday"')
            .replace('"3"', '"Wednesday"')
            .replace('"4"', '"Thursday"')
            .replace('"5"', '"Friday"')
            .replace('"6"', '"Saturday"')
            .replace('"7"', '"Sunday"')
            or "<MISSING>"
        )
        days = [
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
            "Sunday",
        ]
        tmp = []
        if hours != "<MISSING>":
            h = eval(hours)
            for i in days:
                day = i
                try:
                    opens = h.get(f"{i}")[0].get("open")
                    closes = h.get(f"{i}")[0].get("close")
                except TypeError:
                    continue
                line = f"{day} {opens} - {closes}"
                tmp.append(line)
            hours_of_operation = "; ".join(tmp)

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
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.RAW_ADDRESS}))
    ) as writer:
        fetch_data(writer)
