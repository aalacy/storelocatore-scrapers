import httpx
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import International_Parser, parse_address


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.jysk.me/"
    api_url = "https://www.jysk.me/me/prodavnice/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    with SgRequests() as http:
        r = http.get(url=api_url, headers=headers)
        assert isinstance(r, httpx.Response)
        assert 200 == r.status_code
        tree = html.fromstring(r.text)
        div = tree.xpath('//div[contains(@class, "col-sm-6 col-xs-12 prod")]')
        for d in div:

            page_url = "https://www.jysk.me/me/prodavnice/"
            location_name = "".join(d.xpath(".//h4/text()")).replace("\n", "").strip()
            info = d.xpath("./div[2]/text()")
            info = list(filter(None, [a.strip() for a in info]))
            tmp_address = []
            for i in info:
                if "+" in i:
                    break
                tmp_address.append(i)

            ad = " ".join(tmp_address)
            a = parse_address(International_Parser(), ad)
            street_address = f"{a.street_address_1} {a.street_address_2}".replace(
                "None", ""
            ).strip()
            state = a.state or "<MISSING>"
            postal = a.postcode or "<MISSING>"
            country_code = "ME"
            city = a.city or "<MISSING>"
            map_link = "".join(d.xpath(".//iframe/@src"))
            try:
                latitude = map_link.split("!3d")[1].strip().split("!")[0].strip()
                longitude = map_link.split("!2d")[1].strip().split("!")[0].strip()
            except:
                latitude = map_link.split("q=")[1].split(",")[0].strip()
                longitude = map_link.split("q=")[1].split(",")[1].split("&")[0].strip()
            info_1 = d.xpath("./div[2]/text()")
            info_1 = list(filter(None, [a.strip() for a in info_1]))
            tmp_phone = []
            for b in info_1:
                if "+" in b:
                    tmp_phone.append(b)
                    break

            phone = "".join(tmp_phone)

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
                hours_of_operation=SgRecord.MISSING,
                raw_address=ad,
            )

            sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.RAW_ADDRESS}))
    ) as writer:
        fetch_data(writer)
