from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def get_coords(url):
    coords = dict()
    api = f"{url}wp-json/facetwp/v1/refresh"
    json_data = {
        "action": "facetwp_refresh",
        "data": {
            "facets": {
                "locations_map": [],
                "locations_auto": "",
                "location_dropdown": [],
                "location_type": [],
                "location_state": [],
            },
            "frozen_facets": {
                "locations_map": "hard",
            },
            "template": "locations",
            "soft_refresh": 0,
            "is_bfcache": 1,
            "first_load": 0,
            "paged": 1,
        },
    }
    r = session.post(api, json=json_data, headers=headers)
    js = r.json()["settings"]["map"]["locations"]
    for j in js:
        _id = j["post_id"]
        lat = j["position"]["lat"]
        lng = j["position"]["lng"]
        coords[_id] = (lat, lng)

    return coords


def fetch_data(sgw: SgWriter):
    apis = ["https://meekswest.com/", "https://meeksmidwest.com/"]
    for url in apis:
        page_url = f"{url}company/locations/"
        coords = get_coords(url)

        for store_number, ll in coords.items():
            data = {
                "action": "facetwp_map_marker_content",
                "facet_name": "locations_map",
                "post_id": store_number,
            }
            r = session.post(
                f"{url}wp-admin/admin-ajax.php", data=data, headers=headers
            )
            tree = html.fromstring(r.text)

            location_name = "".join(tree.xpath(".//h3//text()")).strip()
            line = tree.xpath(
                "//i[@class='fas fa-map-marker-alt']/following-sibling::text()"
            )
            line = list(filter(None, [l.strip() for l in line]))
            csz = line.pop()
            city = csz.split(",")[0].strip()
            csz = csz.split(",")[1].strip()
            state, postal = csz.split()
            street_address = ", ".join(line)

            phone = "".join(
                tree.xpath(
                    "//strong[contains(text(), 'Phone')]/following-sibling::text()[1]"
                )
            ).strip()
            latitude, longitude = ll
            hours = tree.xpath(
                "//strong[contains(text(), 'Hours')]/following-sibling::text()"
            )
            hours = list(filter(None, [h.strip() for h in hours]))
            hours_of_operation = ";".join(hours)
            if not phone and "NOTE" in hours_of_operation:
                hours_of_operation = SgRecord.MISSING
                phone = "(" + hours[1].split("(")[1]

            row = SgRecord(
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=postal,
                country_code="US",
                store_number=store_number,
                phone=phone,
                latitude=latitude,
                longitude=longitude,
                locator_domain=locator_domain,
                hours_of_operation=hours_of_operation,
            )

            sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://meeks.com/"

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:97.0) Gecko/20100101 Firefox/97.0",
        "Accept": "*/*",
        "Accept-Language": "ru,en-US;q=0.7,en;q=0.3",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "no-cors",
        "Sec-Fetch-Site": "same-origin",
        "TE": "trailers",
        "Pragma": "no-cache",
        "Cache-Control": "no-cache",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        fetch_data(writer)
