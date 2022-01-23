from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://carpartswarehouse.net"
    api_url = "https://carpartswarehouse.net/wp-admin/admin-ajax.php?action=store_search&lat=41.081445&lng=-81.519005&max_results=25&search_radius=50&autoload=1"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    js = r.json()
    for j in js:

        location_name = j.get("store")
        street_address = f"{j.get('address')} {j.get('address2')}".strip()
        state = j.get("state")
        postal = j.get("zip")
        country_code = j.get("country")
        city = j.get("city")
        latitude = j.get("lat")
        store_number = "".join(j.get("email")).split("store")[1].split("@")[0].strip()
        longitude = j.get("lng")
        phone = j.get("phone")
        hours = j.get("hours") or "<MISSING>"
        hours_of_operation = "<MISSING>"
        if hours != "<MISSING>":
            h = html.fromstring(hours)
            hours_of_operation = (
                " ".join(h.xpath("//*//text()")).replace("\n", "").strip()
            )

        api_url = "https://carpartswarehouse.net/locations/"
        session = SgRequests()
        r = session.get(api_url, headers=headers)
        tree = html.fromstring(r.text)
        div = tree.xpath('//a[contains(@href, "mailto")]')
        for d in div:
            em = "".join(d.xpath(".//text()")).split("store")[1].split("@")[0].strip()
            if store_number == em:
                page_url = "".join(d.xpath(".//preceding::h3[1]/a/@href"))

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
