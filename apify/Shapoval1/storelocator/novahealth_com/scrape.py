from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.novahealth.com/"
    api_url = "https://www.novahealth.com/wp-admin/admin-ajax.php?action=store_search&lat=44.05207&lng=-123.08675&max_results=10&search_radius=10&autoload=1"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    js = r.json()
    for j in js:

        page_url = j.get("url") or "https://www.novahealth.com/locations/"
        location_name = (
            "".join(j.get("store"))
            .replace("&#8211;", "–")
            .replace("&#038;", "&")
            .strip()
        )
        if location_name.find("–") != -1:
            location_name = location_name.split("–")[0].strip()
        if location_name.find("—") != -1:
            location_name = location_name.split("—")[0].strip()
        street_address = (
            f"{j.get('address')} {j.get('address2')}".strip() or "<MISSING>"
        )
        state = j.get("state") or "<MISSING>"
        postal = j.get("zip") or "<MISSING>"
        country_code = "US"
        city = j.get("city") or "<MISSING>"
        store_number = j.get("id") or "<MISSING>"
        latitude = j.get("lat") or "<MISSING>"
        longitude = j.get("lng") or "<MISSING>"
        phone = j.get("phone") or "<MISSING>"
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)
        hours_of_operation = (
            " ".join(
                tree.xpath(
                    '//div[./div/h4/i[@class="far fa-clock"]]/following-sibling::div[1]//ul/li//text()'
                )
            )
            .replace("\n", "")
            .strip()
            or "<MISSING>"
        )
        hours_of_operation = " ".join(hours_of_operation.split()) or "<MISSING>"
        if hours_of_operation == "<MISSING>":
            hours_of_operation = (
                "".join(
                    tree.xpath(
                        '//h2[contains(text(), "Hours")]/following-sibling::ul/li[1]/text()'
                    )
                )
                .replace("\n", "")
                .strip()
                or "<MISSING>"
            )
        if phone == "<MISSING>" and page_url != "https://www.novahealth.com/locations/":
            phone = (
                "".join(
                    tree.xpath(
                        "//i[@class='fas fa-phone-square teal']/following-sibling::a[1]/text()"
                    )
                )
                or "<MISSING>"
            )
        if phone == "<MISSING>" and page_url != "https://www.novahealth.com/locations/":
            phone = (
                "".join(tree.xpath('//p[contains(text(), "Urgent Care:")]/a/text()'))
                or "<MISSING>"
            )
        if (
            hours_of_operation.find("Urgent Care:") != -1
            and hours_of_operation.find("Primary Care:") != -1
        ):
            hours_of_operation = (
                hours_of_operation.split("Urgent Care:")[1]
                .split("Primary Care:")[0]
                .strip()
            )
        if (
            hours_of_operation.find("Urgent Care:") != -1
            and hours_of_operation.find("Musculoskeletal :") != -1
        ):
            hours_of_operation = (
                hours_of_operation.split("Urgent Care:")[1]
                .split("Musculoskeletal :")[0]
                .strip()
            )
        hours_of_operation = (
            hours_of_operation.replace("Urgent Care:", "")
            .replace("Primary Care:", "")
            .replace("Physical & Hand Therapy:", "")
            .replace("Testing Facility", "")
            .strip()
        )
        if hours_of_operation.find("Nova Health") != -1:
            hours_of_operation = hours_of_operation.split("Nova Health")[0].strip()
        if (
            page_url == "https://www.novahealth.com/locations/nova-health-mcminnville/"
            and street_address == "4001 Tieton Drive"
        ):
            continue

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
            raw_address=f"{street_address} {city}, {state} {postal}",
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STORE_NUMBER}))
    ) as writer:
        fetch_data(writer)
