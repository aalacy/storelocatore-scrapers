import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.go-sport.com/"
    api_url = "https://www.go-sport.com/stores#/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    js_block = "".join(tree.xpath('//script[@id="bt-resource-global"]/text()'))
    js = json.loads(js_block)
    for j in js["countriesList"]:

        country_code = j.get("countryCode")
        r = session.get(
            f"https://www.go-sport.com/on/demandware.store/Sites-GoSport_FR-Site/default/StoreLocator-GetPlacesByLatLng?lat=48.861717&lng=2.3375435&unit=km&radius=50000&countryCode={country_code}"
        )
        js = r.json()
        for j in js:

            location_name = j.get("storeName") or "<MISSING>"
            location_type = j.get("type") or "<MISSING>"
            street_address = (
                f"{j.get('address1')} {j.get('address2')}".replace("None", "").strip()
                or "<MISSING>"
            )
            state = j.get("stateCode") or "<MISSING>"
            postal = j.get("postalCode") or "<MISSING>"
            if postal == "/" or postal == "-":
                postal = "<MISSING>"
            city = j.get("city") or "<MISSING>"
            store_number = j.get("id") or "<MISSING>"
            page_url = f"https://www.go-sport.com/stores#/stores/{store_number}"
            latitude = j.get("lat") or "<MISSING>"
            longitude = j.get("lng") or "<MISSING>"
            phone = j.get("phone") or "<MISSING>"
            hours_of_operation = "<MISSING>"
            hours = j.get("storeHours")
            days = [
                "Lundi",
                "Mardi",
                "Mercredi",
                "Jeudi",
                "Vendredi",
                "Samedi",
                "Dimanche",
            ]
            tmp = []
            if hours:
                for d in days:
                    day = d
                    try:
                        opens = hours.get(f"{d}")[0].get("start")
                        closes = hours.get(f"{d}")[0].get("end")
                    except:
                        opens, closes = "Closed", "Closed"
                    line = f"{day} {opens} - {closes}"
                    tmp.append(line)
                hours_of_operation = "; ".join(tmp)

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
                location_type=location_type,
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
