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
        locator_domain = "https://www.sunlife.com.ph/en/"
        api_url = "https://www.sunlife.com.ph/en/about-us/where-to-find-us/"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
        }
        r = http.get(url=api_url, headers=headers)
        assert isinstance(r, httpx.Response)
        assert 200 == r.status_code
        tree = html.fromstring(r.text)
        div = tree.xpath("//label/b | //label/strong")
        for d in div:

            location_name = "".join(d.xpath(".//text()"))
            info = d.xpath(".//following-sibling::text()")
            info = list(filter(None, [a.strip() for a in info]))
            tmp = []
            for i in info:
                tmp.append(i)
                if ":" in i or "Tel" in i:
                    break
            ad = " ".join(tmp).replace("\n", "").strip()
            if ad.find("Trunkline:") != -1:
                ad = ad.split("Trunkline:")[0].strip()
            if ad.find("Tel") != -1:
                ad = ad.split("Tel")[0].strip()
            if ad.find("Operating") != -1:
                ad = ad.split("Operating")[0].strip()
            page_url = "https://www.sunlife.com.ph/en/about-us/where-to-find-us/"
            a = parse_address(International_Parser(), ad)
            street_address = f"{a.street_address_1} {a.street_address_2}".replace(
                "None", ""
            ).strip()
            state = a.state or "<MISSING>"
            postal = a.postcode or "<MISSING>"
            country_code = "PH"
            city = a.city or "<MISSING>"
            tmp_1 = []
            for l in info[:5]:
                if "Trunkline" in l or "Telephone" in l or "Tel" in l:
                    tmp_1.append(l)
                    break

            phone = (
                "".join(tmp_1)
                .replace("\n", "")
                .replace("Trunkline:", "")
                .replace("Tel No.", "")
                .replace("Telephone No.", "")
                .replace("Telefax No.", "")
                .replace("Tel no.", "")
                .replace("Telephone Nos.", "")
                .strip()
            )
            if phone.find("loc") != -1:
                phone = phone.split("loc")[0].strip()
            if phone.find(";") != -1:
                phone = phone.split(";")[0].strip()
            if phone.find(",") != -1:
                phone = phone.split(",")[0].strip()
            if phone.find("to") != -1:
                phone = phone.split("to")[0].strip()
            phone = phone or "<MISSING>"
            tmp_2 = []
            for k in info[:6]:
                if "Operating" in k:
                    tmp_2.append(k)
                    break
            hours_of_operation = (
                " ".join(tmp_2).replace("Operating hours:", "").strip() or "<MISSING>"
            )

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
                latitude=SgRecord.MISSING,
                longitude=SgRecord.MISSING,
                hours_of_operation=hours_of_operation,
                raw_address=ad,
            )

            sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(
            SgRecordID({SgRecord.Headers.RAW_ADDRESS, SgRecord.Headers.LOCATION_NAME})
        )
    ) as writer:
        fetch_data(writer)
