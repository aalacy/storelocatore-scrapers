from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def get_hours(hours) -> str:
    tmp = []
    for h in hours:
        day = h.get("dayNumber")
        day = (
            str(day)
            .replace("1", "Monday")
            .replace("2", "Tuesday")
            .replace("3", "Wednesday")
            .replace("4", "Thursday")
            .replace("5", "Friday")
            .replace("6", "Saturday")
            .replace("7", "Sunday")
        )
        opens = h.get("slots")[0].get("openTime")
        closes = h.get("slots")[0].get("closeTime")
        line = f"{day} {opens} - {closes}"
        tmp.append(line)
    hours_of_operation = ";".join(tmp) or "<MISSING>"
    return hours_of_operation


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.montblanc.com/"
    for i in range(1, 4):
        api_url = f"https://www.montblanc.com/api/richemont1/wcs/resources/store/montblanc_GB/storelocator/boutiques/?pageSize=1000&pageNumber={i}"
        session = SgRequests()

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0",
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
            "X-IBM-Client-Id": "b8d40347-fa4e-457c-831a-31b159bf081a",
            "X-Requested-With": "XMLHttpRequest",
            "Connection": "keep-alive",
            "Referer": "https://www.montblanc.com/en-gb/store-locator",
            "Cache-Control": "max-age=0",
            "TE": "Trailers",
        }
        r = session.get(api_url, headers=headers)
        js = r.json()
        for j in js["data"]:
            ids = j.get("identifier")
            a = j.get("address")
            page_url = f"https://www.montblanc.com/en-gb/store-locator#store/{ids}"

            location_name = j.get("storeName") or "<MISSING>"
            if location_name.find("?") != -1:
                location_name = "<MISSING>"
            if location_name.find("& https://") != -1:
                location_name = location_name.split("& https://")[0].strip()
            if location_name.find("https://protect-eu.mimecast.com/s/nKZVC") != -1:
                location_name = "<MISSING>"
            try:
                location_type = (
                    j.get("attributes")[0].get("values")[0].get("value") or "<MISSING>"
                )
            except:
                location_type = "<MISSING>"
            try:
                phone = a.get("phone1") or "<MISSING>"
            except:
                phone = "<MISSING>"
            if not phone:
                phone = "<MISSING>"

            if phone == "0" or phone == "-0":
                phone = "<MISSING>"
            if phone.find("|") != -1:
                phone = phone.replace("|", "").strip()
            if phone.find('"') != -1:
                phone = phone.replace('"', "").strip()
            try:
                street_address = a.get("line1") or "<MISSING>"
            except:
                street_address = "<MISSING>"
            if not street_address:
                street_address = "<MISSING>"
            if street_address.find("?") != -1:
                street_address = "<MISSING>"

            if street_address == "0":
                street_address = "<MISSING>"
            try:
                state = a.get("state") or "<MISSING>"
            except:
                state = "<MISSING>"
            if state == "0":
                state = "<MISSING>"
            try:
                postal = a.get("postCode") or "<MISSING>"
            except:
                postal = "<MISSING>"
            if not postal:
                postal = "<MISSING>"
            if postal == "0":
                postal = "<MISSING>"
            if (
                postal.find("QLD") != -1
                or postal.find("VIC") != -1
                or postal.find("WA") != -1
            ):
                ad = postal
                state = ad.split()[0].strip()
                postal = ad.split()[1].strip()
            if postal.find("SA") != -1 or postal.find("NSW") != -1:
                ad = postal
                state = ad.split()[0].strip()
                postal = ad.split()[1].strip()
            if (
                postal.find("3 Rue du Châtelet") != -1
                or postal.find("22-24 Rue G. Clémenceau") != -1
                or postal.find("14 Place du Cygne") != -1
                or postal.find("C.C. Carrefour") != -1
                or postal.find("Cité Europe - Boulevard du Kent") != -1
                or postal.find("5 Rue des Domeliers") != -1
            ):
                postal = "<MISSING>"
            if postal.find("54292 Trier") != -1 or postal.find("50737 Köln") != -1:
                postal = postal.split()[0].strip()
            postal = postal.replace("*", "").replace("%", "").strip()
            try:
                country_code = a.get("countryCode")
            except:
                country_code = "<MISSING>"
            try:
                city = a.get("city") or "<MISSING>"
            except:
                city = "<MISSING>"
            if city.find("?") != -1:
                city = "<MISSING>"
            city = city.replace("Rio De Janeiro", "Rio de Janeiro")

            if street_address.find("Rio Grande do Norte") != -1:
                state = "Rio Grande do Norte"
                street_address = street_address.split(f"{state}")[0].strip()

            if street_address.find("Jordan") != -1:
                street_address = street_address.split("Jordan")[0].strip()
            if street_address.find("TORINO") != -1:
                street_address = street_address.replace("TORINO", "").strip()

            if street_address.find(f"{postal}") != -1 and postal != "<MISSING>":
                street_address = street_address.replace(f"{postal}", "").strip()
            if street_address.find(f"{city}") != -1 and city != "<MISSING>":
                street_address = street_address.replace(f"{city}", "").strip()

            latitude = j.get("spatialData").get("latitude") or "<MISSING>"
            longitude = j.get("spatialData").get("longitude") or "<MISSING>"
            hours = j.get("openingTimes")
            hours_of_operation = "<MISSING>"
            if hours:
                hours_of_operation = get_hours(hours)

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
                location_type=location_type,
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=hours_of_operation,
            )

            sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))) as writer:
        fetch_data(writer)
