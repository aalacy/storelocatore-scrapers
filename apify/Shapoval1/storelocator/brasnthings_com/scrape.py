import httpx
import calendar
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import International_Parser, parse_address
from datetime import date, timedelta


def fetch_data(sgw: SgWriter):
    with SgRequests() as http:
        locator_domain = "https://www.brasnthings.com/"
        api_url = "https://www.brasnthings.com/stockists/ajax/stores?selected_groups%5B%5D=_1621812823_14994&_=1645391484396"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
        }
        r = http.get(url=api_url, headers=headers)
        assert isinstance(r, httpx.Response)
        assert 200 == r.status_code
        js = r.json()["groups_markers"][f'{api_url.split("=")[-2].split("&")[0]}']
        for j in js:

            location_name = j.get("name") or "<MISSING>"
            ad = j.get("address") or "<MISSING>"
            a = parse_address(International_Parser(), ad)
            street_address = f"{a.street_address_1} {a.street_address_2}".replace(
                "None", ""
            ).strip()
            state = j.get("region") or "<MISSING>"
            postal = j.get("postcode") or "<MISSING>"
            country_code = j.get("country") or "<MISSING>"
            if state == "CA":
                country_code = "US"
            city = j.get("city") or "<MISSING>"
            store_number = j.get("stockist_id") or "<MISSING>"
            page_url = (
                f"https://www.brasnthings.com/stores/store/index/id/{store_number}"
            )
            latitude = j.get("latitude") or "<MISSING>"
            longitude = j.get("longitude") or "<MISSING>"
            if latitude == longitude:
                latitude, longitude = "<MISSING>", "<MISSING>"
            phone = j.get("phone") or "<MISSING>"
            r = http.get(url=page_url, headers=headers)
            assert isinstance(r, httpx.Response)
            assert 200 == r.status_code
            tree = html.fromstring(r.text)
            curr_date = date.today()
            next_date = curr_date + timedelta(days=1)
            today = calendar.day_name[curr_date.weekday()]
            tomorrow = calendar.day_name[next_date.weekday()]
            hours_of_operation = (
                " ".join(tree.xpath('//div[@class="store-schedule"]/div//text()'))
                .replace("\n", "")
                .strip()
                or "<MISSING>"
            )
            hours_of_operation = (
                " ".join(hours_of_operation.split())
                .replace("Today", f"{today}")
                .strip()
            )
            if hours_of_operation.count(f"{today}") == 2:
                hours_of_operation = (
                    " ".join(tree.xpath('//div[@class="store-schedule"]/div//text()'))
                    .replace("\n", "")
                    .replace("Today", f"{tomorrow}")
                    .strip()
                )
            hours_of_operation = hours_of_operation.replace(
                "unknown - unknown", "<MISSING>"
            ).strip()
            if hours_of_operation.count("<MISSING>") == 7:
                hours_of_operation = "<MISSING>"
            if hours_of_operation.count("<MISSING>") > 2:
                hours_of_operation = "<MISSING>"

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
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STORE_NUMBER}))
    ) as writer:
        fetch_data(writer)
