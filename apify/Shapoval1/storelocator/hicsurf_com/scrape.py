from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgpostal import International_Parser, parse_address


def fetch_data(sgw: SgWriter):

    locator_domain = "https://hicsurf.com"
    api_url = "https://hicsurf.com/stores/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[./h3[@class="widget-title"]]')
    for d in div:

        page_url = "https://hicsurf.com/stores/"
        location_name = "".join(d.xpath(".//h3/text()"))
        ad = " ".join(d.xpath("./div/p[1]//text()")).replace("\n", "").strip()
        ad = " ".join(ad.split())
        adr = ad.split("Phone:")[0].strip()
        a = parse_address(International_Parser(), adr)
        street_address = f"{a.street_address_1} {a.street_address_2}".replace(
            "None", ""
        ).strip()
        state = a.state or "<MISSING>"
        postal = a.postcode or "<MISSING>"
        country_code = "US"
        city = a.city or "<MISSING>"

        phone = (
            "".join(d.xpath('.//a[contains(@href, "tel")]//text()'))
            .replace("\n", "")
            .strip()
            or "<MISSING>"
        )
        if phone == "<MISSING>":
            phone = (
                "".join(d.xpath('.//span[@data-dtype="d3ph"]/text()')) or "<MISSING>"
            )
        slugPhone = phone.replace("(808)", "808").replace(" ", "-")
        hours_of_operation = (
            " ".join(
                d.xpath(
                    './/strong[contains(text(), "Hours:")]/following-sibling::text()'
                )
            )
            .replace("\n", "")
            .strip()
            or "<MISSING>"
        )
        if not hours_of_operation:
            hours_of_operation = (
                " ".join(d.xpath('.//span[contains(text(), "Monday")]/text()'))
                .replace("\n", "")
                .strip()
                or "<MISSING>"
            )

        session = SgRequests()
        r = session.get(
            "https://hicsurf.com/wp-admin/admin-ajax.php?action=store_search&lat=21.285002&lng=-157.835698&max_results=2500&search_radius=50000&autoload=1",
            headers=headers,
        )
        js = r.json()
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        for j in js:
            ph = "".join(j.get("phone")).replace("7100", "-7100")
            if slugPhone == ph:
                latitude = j.get("lat")
                longitude = j.get("lng")
                page_url = j.get("permalink")

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
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)
