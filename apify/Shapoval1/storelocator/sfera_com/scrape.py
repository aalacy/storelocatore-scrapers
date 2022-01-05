import httpx
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import International_Parser, parse_address


def fetch_data(sgw: SgWriter):
    with SgRequests() as http:
        locator_domain = "https://www.sfera.com/"
        api_url = "https://www.sfera.com/pl/stores"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
        }
        r = http.get(url=api_url, headers=headers)
        assert isinstance(r, httpx.Response)
        assert 200 == r.status_code
        tree = html.fromstring(r.text)
        div = "".join(
            tree.xpath(
                '//script[contains(text(), "location3 = new woosmap.map.LatLng(")]/text()'
            )
        ).split("location3 = new woosmap.map.LatLng(")[1:]
        for d in div:
            latitude = d.split(",")[0].strip()
            longitude = d.split(",")[1].split(")")[0].strip()

            location_name = d.split("title:")[1].split(",")[0].replace("'", "").strip()
            data = {
                "lat": f"{latitude}",
                "lng": f"{longitude}",
                "cont": "1",
                "entrada": "116",
                "busca": f"{location_name}",
            }
            api_url_1 = "https://www.sfera.com/one/mod/tiendas_ajax.php"

            r = http.post(url=api_url_1, headers=headers, data=data)
            assert isinstance(r, httpx.Response)
            assert 200 == r.status_code
            tree = html.fromstring(r.text)
            divs = tree.xpath('//div[contains(@id, "tiendas_obj")]')
            for li in divs:
                ad = (
                    "".join(li.xpath("./div[1]/following-sibling::text()[1]"))
                    .replace("\n", "")
                    .strip()
                )
                ad = " ".join(ad.split())
                page_url = f"https://www.sfera.com/pl/stores/?tiendas_buscar={location_name}&coord={latitude}@@{longitude}"

                a = parse_address(International_Parser(), ad)
                street_address = (
                    f"{a.street_address_1} {a.street_address_2}".replace(
                        "None", ""
                    ).strip()
                    or "<MISSING>"
                )
                if street_address == "<MISSING>" or street_address.isdigit():
                    street_address = ad
                state = a.state or "<MISSING>"
                postal = a.postcode or "<MISSING>"
                country_code = a.country or "<MISSING>"
                city = a.city or "<MISSING>"

                phone = (
                    "".join(li.xpath('.//span[@class="tientextos2"]/text()'))
                    .replace("\n", "")
                    .strip()
                    or "<MISSING>"
                )
                try:
                    latitude = "".join(li.xpath(".//@onclick")).split(",")[1].strip()
                    longitude = (
                        "".join(li.xpath(".//@onclick"))
                        .split(",")[2]
                        .split(")")[0]
                        .strip()
                    )
                except:
                    latitude, longitude = "<MISSING>", "<MISSING>"
                hours_of_operation = (
                    " ".join(
                        li.xpath(
                            './/span[@class="tientextos2"]/following-sibling::text()'
                        )
                    )
                    .replace("\n", "")
                    .strip()
                    or "<MISSING>"
                )
                hours_of_operation = " ".join(hours_of_operation.split())

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
