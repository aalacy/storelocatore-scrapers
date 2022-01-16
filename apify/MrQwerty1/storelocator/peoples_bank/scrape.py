from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def write(params: dict, sgw: SgWriter):
    row = SgRecord(
        page_url=page_url,
        location_name=params["location_name"],
        street_address=params["street_address"],
        city=params["city"],
        state=params["state"],
        zip_postal=params["zip_postal"],
        country_code="US",
        phone=params["phone"],
        latitude=params["latitude"],
        longitude=params["longitude"],
        locator_domain=locator_domain,
        hours_of_operation=params["hours_of_operation"],
    )

    sgw.write_row(row)


def fetch_data(sgw: SgWriter):
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    divs = tree.xpath("//ul[@class='accordion']/li[not(contains(@id, 'atm'))]")

    for d in divs:
        lines = d.xpath(".//text()")
        lines = list(filter(None, [l.replace("\xa0", "").strip() for l in lines]))
        check = lines.pop(0)
        is2 = False
        if "2" in check:
            is2 = True

        hoos = []
        coords = []
        cnt = 1
        tables = d.xpath(".//table")
        for table in tables:
            _tmp = []
            tr = table.xpath("./tbody/tr")
            for t in tr:
                day = "".join(t.xpath("./th/text()")).strip()
                inter = "".join(t.xpath("./td[1]/text()")).strip()
                if "lunch" in day.lower():
                    continue
                _tmp.append(f"{day}: {inter}")
            hoos.append(";".join(_tmp))

            text = "".join(d.xpath(f".//a[not(contains(@href, '#'))][{cnt}]/@href"))
            if "/@" in text:
                latitude = text.split("/@")[1].split(",")[0]
                longitude = text.split("/@")[1].split(",")[1]
            else:
                latitude, longitude = SgRecord.MISSING, SgRecord.MISSING
            coords.append((latitude, longitude))
            cnt += 1

        for j in range(2):
            location_name, phone = SgRecord.MISSING, SgRecord.MISSING
            street_address, city = SgRecord.MISSING, SgRecord.MISSING
            state, postal = SgRecord.MISSING, SgRecord.MISSING

            for i in range(len(lines)):
                t = lines[i]
                if i == 0:
                    location_name = lines[i]
                    continue
                if t == "PHONE":
                    phone = lines[i + 1]
                    continue
                if t == "ADDRESS":
                    street_address = lines[i + 1]
                    csz = lines[i + 2]
                    city = csz.split(", ")[0]
                    sz = csz.split(", ")[-1]
                    state, postal = sz.split()
                    continue
                if i < len(lines) - 1:
                    t1 = lines[i + 1]
                    if "(" in t1 and t1[-1] == ")" and t1[0] != "(":
                        lines = lines[i + 1 :]
                        break
            params = {
                "location_name": location_name,
                "street_address": street_address,
                "city": city,
                "state": state,
                "zip_postal": postal,
                "phone": phone,
            }
            lat, lng = coords[j]
            params["latitude"] = lat
            params["longitude"] = lng
            params["hours_of_operation"] = hoos[j]
            write(params, sgw)
            if not is2:
                break


if __name__ == "__main__":
    locator_domain = "https://www.peoples.bank/"
    page_url = "https://www.peoples.bank/locations"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PhoneNumberId)) as writer:
        fetch_data(writer)
