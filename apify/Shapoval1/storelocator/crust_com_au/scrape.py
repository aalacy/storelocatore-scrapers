from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.crust.com.au/"
    api_url = "https://www.crust.com.au/stores/stores_for_map_markers.json/?catering_active=undefined"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    js = r.json()
    for j in js:

        page_id = j.get("id")
        location_name = j.get("name") or "<MISSING>"
        street_address = j.get("address") or "<MISSING>"
        if str(street_address).find("(") != -1:
            street_address = str(street_address).split("(")[0].strip()
        state = j.get("state") or "<MISSING>"
        postal = j.get("postcode") or "<MISSING>"
        country_code = "AU"
        city = j.get("suburb") or "<MISSING>"
        ll = str(j.get("location"))
        latitude = ll.split(",")[0].strip()
        longitude = ll.split(",")[1].strip()
        r = session.get(
            f"https://www.crust.com.au/stores/{page_id}/store_online/?&context=locator"
        )
        tree = html.fromstring(r.text)
        slug = "".join(tree.xpath("//a[./h4]/@href"))
        page_url = f"https://www.crust.com.au{slug}"
        phone = "".join(tree.xpath('//a[contains(@href, "tel")]/text()')) or "<MISSING>"
        tmp = []
        tmp_1 = []
        tmp_2 = []
        tmp_3 = []
        tmp_4 = []
        tmp_5 = []
        tmp_6 = []

        day_1 = tree.xpath(
            '//h5[text()="Opening Hours"]/following-sibling::table//tr[./td][1]//text()'
        )
        day_1 = list(filter(None, [a.strip() for a in day_1]))
        for s in day_1:
            if "N/A" in s or "(Today)" in s:
                continue
            if "," in s:
                s = str(s).split(",")[0].strip()
            tmp.append(s)
        if len(tmp) == 3:
            tmp[1] = "".join(tmp[1]).split("-")[0] + "-" + "".join(tmp[2]).split("-")[1]
            del tmp[2]
        if len(tmp) == 4:
            tmp[1] = "".join(tmp[1]).split("-")[0] + "-" + "".join(tmp[3]).split("-")[1]
            del tmp[2]
            del tmp[2]

        day_2 = tree.xpath(
            '//h5[text()="Opening Hours"]/following-sibling::table//tr[./td][2]//text()'
        )
        day_2 = list(filter(None, [a.strip() for a in day_2]))
        for s in day_2:
            if "N/A" in s or "(Today)" in s:
                continue
            if "," in s:
                s = str(s).split(",")[0].strip()
            tmp_1.append(s)
        if len(tmp_1) == 3:
            tmp_1[1] = (
                "".join(tmp_1[1]).split("-")[0] + "-" + "".join(tmp_1[2]).split("-")[1]
            )
            del tmp_1[2]
        if len(tmp_1) == 4:
            tmp_1[1] = (
                "".join(tmp_1[1]).split("-")[0] + "-" + "".join(tmp_1[3]).split("-")[1]
            )
            del tmp_1[2]
            del tmp_1[2]

        day_3 = tree.xpath(
            '//h5[text()="Opening Hours"]/following-sibling::table//tr[./td][3]//text()'
        )
        day_3 = list(filter(None, [a.strip() for a in day_3]))
        for s in day_3:
            if "N/A" in s or "(Today)" in s:
                continue
            if "," in s:
                s = str(s).split(",")[0].strip()
            tmp_2.append(s)
        if len(tmp_2) == 3:
            tmp_2[1] = (
                "".join(tmp_2[1]).split("-")[0] + "-" + "".join(tmp_2[2]).split("-")[1]
            )
            del tmp_2[2]
        if len(tmp_2) == 4:
            tmp_2[1] = (
                "".join(tmp_2[1]).split("-")[0] + "-" + "".join(tmp_2[3]).split("-")[1]
            )
            del tmp_2[2]
            del tmp_2[2]

        day_4 = tree.xpath(
            '//h5[text()="Opening Hours"]/following-sibling::table//tr[./td][4]//text()'
        )
        day_4 = list(filter(None, [a.strip() for a in day_4]))
        for s in day_4:
            if "N/A" in s or "(Today)" in s:
                continue
            if "," in s:
                s = str(s).split(",")[0].strip()
            tmp_3.append(s)
        if len(tmp_3) == 3:
            tmp_3[1] = (
                "".join(tmp_3[1]).split("-")[0] + "-" + "".join(tmp_3[2]).split("-")[1]
            )
            del tmp_3[2]
        if len(tmp_3) == 4:
            tmp_3[1] = (
                "".join(tmp_3[1]).split("-")[0] + "-" + "".join(tmp_3[3]).split("-")[1]
            )
            del tmp_3[2]
            del tmp_3[2]

        day_5 = tree.xpath(
            '//h5[text()="Opening Hours"]/following-sibling::table//tr[./td][5]//text()'
        )
        day_5 = list(filter(None, [a.strip() for a in day_5]))
        for s in day_5:
            if "N/A" in s or "(Today)" in s:
                continue
            if "," in s:
                s = str(s).split(",")[0].strip()
            tmp_4.append(s)
        if len(tmp_4) == 3:
            tmp_4[1] = (
                "".join(tmp_4[1]).split("-")[0] + "-" + "".join(tmp_4[2]).split("-")[1]
            )
            del tmp_4[2]
        if len(tmp_4) == 4:
            tmp_4[1] = (
                "".join(tmp_4[1]).split("-")[0] + "-" + "".join(tmp_4[3]).split("-")[1]
            )
            del tmp_4[2]
            del tmp_4[2]

        day_6 = tree.xpath(
            '//h5[text()="Opening Hours"]/following-sibling::table//tr[./td][6]//text()'
        )
        day_6 = list(filter(None, [a.strip() for a in day_6]))
        for s in day_6:
            if "N/A" in s or "(Today)" in s:
                continue
            if "," in s:
                s = str(s).split(",")[0].strip()
            tmp_5.append(s)
        if len(tmp_5) == 3:
            tmp_5[1] = (
                "".join(tmp_5[1]).split("-")[0] + "-" + "".join(tmp_5[2]).split("-")[1]
            )
            del tmp_5[2]
        if len(tmp_5) == 4:
            tmp_5[1] = (
                "".join(tmp_5[1]).split("-")[0] + "-" + "".join(tmp_5[3]).split("-")[1]
            )
            del tmp_5[2]
            del tmp_5[2]

        day_7 = tree.xpath(
            '//h5[text()="Opening Hours"]/following-sibling::table//tr[./td][7]//text()'
        )
        day_7 = list(filter(None, [a.strip() for a in day_7]))
        for s in day_7:
            if "N/A" in s or "(Today)" in s:
                continue
            if "," in s:
                s = str(s).split(",")[0].strip()
            tmp_6.append(s)
        if len(tmp_6) == 3:
            tmp_6[1] = (
                "".join(tmp_6[1]).split("-")[0] + "-" + "".join(tmp_6[2]).split("-")[1]
            )
            del tmp_6[2]
        if len(tmp_6) == 4:
            tmp_6[1] = (
                "".join(tmp_6[1]).split("-")[0] + "-" + "".join(tmp_6[3]).split("-")[1]
            )
            del tmp_6[2]
            del tmp_6[2]

        hours_of_operation = (
            " ".join(tmp)
            + "; "
            + " ".join(tmp_1)
            + "; "
            + " ".join(tmp_2)
            + "; "
            + " ".join(tmp_3)
            + "; "
            + " ".join(tmp_4)
            + "; "
            + " ".join(tmp_5)
            + "; "
            + " ".join(tmp_6)
        )
        hours_of_operation = hours_of_operation.replace("Monday;", "").replace(
            "Wednesday;", ""
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
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))) as writer:
        fetch_data(writer)
