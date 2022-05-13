from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://ao.dk/"
    api_url = "https://ao.dk/api/Center/HentKortCentre"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    js = r.json()
    for j in js:

        slug = j.get("Webalias")
        page_url = f"https://ao.dk/{slug}"
        if page_url == "https://ao.dk/None":
            page_url = str(page_url).replace("None", "").strip()
        location_name = j.get("Navn") or "<MISSING>"
        a = j.get("Adresse")
        street_address = a.get("VejHusnavn") or "<MISSING>"
        state = j.get("Region") or "<MISSING>"
        postal = a.get("Postnr") or "<MISSING>"
        country_code = "DK"
        city = a.get("By") or "<MISSING>"
        store_number = j.get("LagerNummer") or "<MISSING>"
        latitude = j.get("Laengdegrad") or "<MISSING>"
        longitude = j.get("Breddegrad") or "<MISSING>"
        phone = j.get("Telefonnummer") or "<MISSING>"
        try:
            r = session.get(page_url, headers=headers)
            tree = html.fromstring(r.text)
            hours = (
                "".join(tree.xpath("//opening-hours/@schedule"))
                .replace("null", "None")
                .replace("false", "False")
                .replace("true", "True")
            )
            h = eval(hours)
            tmp = []
            hours_of_operation = "<MISSING>"
            if h:
                for i in h:
                    day = i.get("ShortenedDayName")
                    opens = i.get("FormattedOpeningTime")
                    closes = i.get("FormattedClosingTime")
                    line = f"{day} {opens} - {closes}"
                    tmp.append(line)
                hours_of_operation = "; ".join(tmp)
        except:
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
