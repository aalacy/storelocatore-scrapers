import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.harryrosen.com"
    api_url = "https://www.harryrosen.com/en/stores"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    jsblock = "".join(tree.xpath('//script[contains(text(), "ctas")]/text()'))
    js = json.loads(jsblock)

    for j in js["props"]["pageProps"]["genericPageContent"]["items"][1]["tabs"]:
        a = j.get("content").get("items")
        for b in a:

            l = b.get("ctas")
            if l is None:
                continue
            try:
                slug = l[0].get("link")
            except IndexError:
                continue
            if str(slug).find("http") != -1:
                continue
            ad = b.get("body")

            m = html.fromstring(ad)
            ad = m.xpath("//*//text()")
            store_number = str(b).split("storeId={")[1].split("}")[0].strip()
            adr = "".join(ad[1]).replace("\n", "").strip() or "<MISSING>"
            page_url = f"{locator_domain}{slug}"
            location_name = b.get("headline")
            street_address = "".join(ad[0]).strip()

            if street_address.find("ADDRESS") != -1:
                street_address = "".join(ad[1]).strip()
                adr = "".join(ad[2]).replace("\n", "").strip()
            if street_address.find("100 King Street West Toronto") != -1:
                adr = " ".join(ad[0].split()[3:])
                street_address = " ".join(street_address.split()[:3])
            adr = adr.replace(",", "")

            state = adr.split()[-3]
            postal = " ".join(adr.split()[-2:])

            country_code = "CA"
            city = " ".join(adr.split()[:-3])
            phone = "".join(ad[2]).replace("\n", "").strip() or "<MISSING>"
            if phone == "<MISSING>":
                phone = "".join(ad[3]).replace("\n", "").strip() or "<MISSING>"
            if street_address.find("1455") != -1:
                phone = "".join(ad[4]).replace("\n", "").strip()
            phone = phone.replace("Tel:", "").strip()
            if phone.find("This") != -1:
                phone = phone.split("This")[0].strip()
            latitude, longitude = "<MISSING>", "<MISSING>"
            r = session.get("https://www.harryrosen.com/api/stores", headers=headers)
            js = r.json()
            days = ["MO", "TU", "WE", "TH", "FR", "SA", "SU"]
            tmp = []
            for j in js:
                ids = j.get("id")
                if ids == store_number:
                    latitude = j.get("latitude")
                    longitude = j.get("longitude")
                    for d in days:
                        day = d
                        opens = j.get("openingHours").get(f"{d}").get("start")
                        closes = j.get("openingHours").get(f"{d}").get("end")
                        line = f"{day} {opens} - {closes}"
                        tmp.append(line)

            hours_of_operation = (
                "; ".join(tmp).replace("CLOSED - CLOSED", "CLOSED").strip()
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
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))) as writer:
        fetch_data(writer)
