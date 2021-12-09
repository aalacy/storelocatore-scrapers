from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def fetch_data(sgw: SgWriter):
    r = session.post("https://heronfoods.com/wp-admin/admin-ajax.php", data=data)

    for j in r.json().values():
        _tmp = []
        hours = j.get("op") or {}
        days = [
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
            "Sunday",
        ]
        for k, v in hours.items():
            index = int(k)
            if index % 2 == 0:
                day = days[int(index / 2)]
                start = v
                end = hours.get(str(index + 1))
                if not start:
                    continue
                _tmp.append(f"{day}: {start}-{end}")

        hours_of_operation = ";".join(_tmp)
        postal = j.get("zp") or j.get("rg")

        row = SgRecord(
            page_url=j.get("gu"),
            location_name=j.get("na"),
            street_address=j.get("st"),
            city=j.get("ct"),
            zip_postal=postal,
            country_code=j.get("co"),
            latitude=j.get("lat"),
            longitude=j.get("lng"),
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://heronfoods.com/"
    data = {
        "action": "get_stores",
        "lat": "51.5072178",
        "lng": "-0.1275862",
        "radius": "1000",
        "categories[0]": "",
        "name": "",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
