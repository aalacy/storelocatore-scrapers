from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0",
    }

    r = session.post(
        "https://geodis.com/geodis_custom_ajax_get_all_locations", headers=headers
    )
    js = r.json()
    for j in js:
        node_id = j.get("node_id")
        latitude = j.get("coordinates")[0]
        longitude = j.get("coordinates")[1]

        session = SgRequests()
        data = {"node_id": f"{node_id}"}
        r = session.post(
            "https://geodis.com/geodis_custom_ajax_get_agency_popup",
            headers=headers,
            data=data,
        )
        tree = html.fromstring(r.text)
        page_url = "https://geodis.com/locations"
        street_address = (
            " ".join(tree.xpath('//span[@class="address-line1"]/text()'))
            .replace("\n", "")
            .strip()
            or "<MISSING>"
        )
        city = (
            " ".join(tree.xpath('//span[@class="locality"]/text()'))
            .replace("\n", "")
            .strip()
            or "<MISSING>"
        )
        if city.find("Cedex") != -1:
            city = city.split("Cedex")[0].strip()
        if city.find("cedex") != -1:
            city = city.split("cedex")[0].strip()
        state = (
            " ".join(tree.xpath('//span[@class="administrative-area"]/text()'))
            .replace("\n", "")
            .strip()
            or "<MISSING>"
        )

        postal = (
            " ".join(tree.xpath('//span[@class="postal-code"]/text()'))
            .replace("\n", "")
            .strip()
            or "<MISSING>"
        )
        if postal.find("Buenos Aires") != -1:
            postal = "<MISSING>"
        if postal.find("Co. Dublin") != -1:
            postal = postal.replace("Co. Dublin", "").strip()
        postal = (
            postal.replace("French Guiana", "")
            .replace("DOM TOM", "")
            .replace("Metro Manila", "")
            .replace("Taipei City", "")
            .replace("Songkhla", "")
            .replace("Chon Buri", "")
            .replace("Bangkok", "")
            .replace("NY-", "")
            .strip()
        )
        if postal.find("Santiago") != -1:
            postal = "<MISSING>"

        location_name = (
            " ".join(tree.xpath('//div[@class="title-agency-view"]/a/text()'))
            .replace("\n", "")
            .strip()
            or "<MISSING>"
        )

        country_code = (
            " ".join(tree.xpath('//span[@class="country"]/text()'))
            .replace("\n", "")
            .strip()
            or "<MISSING>"
        )
        if postal.find(" ") != -1 and country_code == "United States":
            po = postal
            state = po.split()[0].strip()
            postal = po.split()[1].strip()
        if postal.find("Province") != -1 and country_code == "China":
            po = postal
            state = " ".join(po.split()[:-1])
            postal = po.split()[-1].strip()
        store_number = node_id
        hours_of_operation = (
            " ".join(tree.xpath('//div[1][@class="group-clock-view"]/div/text()'))
            .replace("\n", "")
            .strip()
            or "<MISSING>"
        )
        if (
            hours_of_operation.count("24/7") == 7
            or hours_of_operation.count("24/7") > 7
        ):
            hours_of_operation = "24/7"
        phone = "".join(tree.xpath('//a[contains(@href, "tel")]/text()')) or "<MISSING>"
        if phone.find("|") != -1:
            phone = phone.split("|")[0].strip()
        if phone.find("(Wittelsheim)") != -1:
            phone = phone.split("(Wittelsheim)")[1].strip()
        if phone == "0" or phone == "2":
            phone = "<MISSING>"

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
    locator_domain = "https://geodis.com/"
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)
