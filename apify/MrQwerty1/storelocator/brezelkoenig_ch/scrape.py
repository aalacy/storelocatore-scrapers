import datetime
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def fetch_data(sgw: SgWriter):
    api = "https://api.valora-stores.com/_index.php?apiv=2.0.9&c=21&a=data&ns=storefinder&l=de&key=avecHnbG6Tr"
    r = session.get(api, headers=headers)
    js = r.json()

    types = dict()
    for _id, v in js["props"]["formate"]["r"].items():
        _type = v[0]
        if "(" in _type:
            _type = _type.split("(")[0].strip()
        types[_id] = _type

    countries = dict()
    for _id, v in js["props"]["laender"]["r"].items():
        countries[_id] = v[1]

    hoos = dict()
    days = [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday",
    ]
    for _id, v in js["items"]["stores_open"]["r"].items():
        cnt = 0
        _tmp = []
        for d in v:
            a = ":".join(
                str(datetime.timedelta(seconds=int(d.get("a")))).split(":")[:-1]
            )
            z = ":".join(
                str(datetime.timedelta(seconds=int(d.get("z")))).split(":")[:-1]
            )
            day = days[cnt]
            if a == z:
                _tmp.append(f"{day}: Closed")
            else:
                _tmp.append(f"{day}: {a}-{z}".replace("1 day, ", "0"))
            cnt += 1
        hoo = ";".join(_tmp)
        hoos[_id] = hoo

    stores = js["items"]["stores"]["r"].items()
    for store_number, j in stores:
        location_name = j[0]
        country_code = countries.get(str(j[2]))
        adr1 = j[9]
        adr2 = j[10]
        street_address = f"{adr1} {adr2}".strip()
        city = j[12]
        postal = j[11]
        location_type = types.get(str(j[4]))
        latitude = j[5]
        longitude = j[6]
        hours_of_operation = hoos.get(store_number)

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            zip_postal=postal,
            country_code=country_code,
            latitude=latitude,
            longitude=longitude,
            location_type=location_type,
            store_number=store_number,
            hours_of_operation=hours_of_operation,
            locator_domain=locator_domain,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://brezelkoenig.ch/"
    page_url = "https://brezelkoenig.ch/de/standorte/"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:97.0) Gecko/20100101 Firefox/97.0",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        fetch_data(writer)
