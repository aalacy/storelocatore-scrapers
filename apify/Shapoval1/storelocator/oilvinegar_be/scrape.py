from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.oilvinegar.be/"
    api_url = "https://www.oilvinegar.be/rest/V1/storelocator/search/?searchCriteria%5Bfilter_groups%5D%5B0%5D%5Bfilters%5D%5B0%5D%5Bfield%5D=country_id&searchCriteria%5Bfilter_groups%5D%5B0%5D%5Bfilters%5D%5B0%5D%5Bvalue%5D=BE&searchCriteria%5Bfilter_groups%5D%5B0%5D%5Bfilters%5D%5B0%5D%5Bcondition_type%5D=eq&_=1652342523071"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    js = r.json()["items"]
    for j in js:

        slug = j.get("website")
        page_url = f"https://www.oilvinegar.be/{slug}"
        location_name = j.get("name") or "<MISSING>"
        street_address = j.get("street") or "<MISSING>"
        state = j.get("region") or "<MISSING>"
        postal = j.get("postal_code") or "<MISSING>"
        country_code = "BE"
        city = j.get("city") or "<MISSING>"
        latitude = j.get("lat") or "<MISSING>"
        longitude = j.get("lng") or "<MISSING>"
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)
        phone_lst = tree.xpath('//a[contains(@href, "tel")]/text()')
        phone_lst = list(filter(None, [a.strip() for a in phone_lst]))
        phone = "".join(phone_lst[0]).strip()
        hours_of_operation = (
            " ".join(
                tree.xpath(
                    '//tr[.//span[text()="Openingstijden"]]/following-sibling::tr//td//text()'
                )
            )
            .replace("\n", "")
            .strip()
            or "<MISSING>"
        )
        if hours_of_operation == "<MISSING>":
            hours_of_operation = (
                " ".join(
                    tree.xpath(
                        '//h4[text()="Openingstijden"]/following-sibling::div[1]//text() | //h4[text()="Heures d’ouverture"]/following-sibling::div[1]//text()'
                    )
                )
                .replace("\n", "")
                .strip()
            )
        hours_of_operation = (
            " ".join(hours_of_operation.split())
            .replace("Ouvertures exceptionnelles", "")
            .strip()
        )
        if hours_of_operation.find("Extra") != -1:
            hours_of_operation = hours_of_operation.split("Extra")[0].strip()
        if hours_of_operation.find("Eerste zondag") != -1:
            hours_of_operation = hours_of_operation.split("Eerste zondag")[0].strip()
        if hours_of_operation.find("Aangepaste") != -1:
            hours_of_operation = hours_of_operation.split("Aangepaste")[0].strip()
        if hours_of_operation.find("Sluiting over") != -1:
            hours_of_operation = hours_of_operation.split("Sluiting over")[0].strip()

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
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))) as writer:
        fetch_data(writer)
