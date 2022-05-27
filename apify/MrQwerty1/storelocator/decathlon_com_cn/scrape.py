from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def fetch_data(sgw: SgWriter):
    params = [
        [
            "https://api.woosmap.cn/stores/search/?key=woos-bd4119f8-8bf7-3891-96d8-ae6a4df2cf0b&lat=36.647458&lng=101.729955&max_distance=2000000&stores_by_page=300&page=",
            "decathlon.com.cn",
            "CN",
        ],
        [
            "https://api.woosmap.com/stores/nearby?key=woos-5dbb4402-9d17-366b-af49-614910204d64&lat=40.416706&lng=-3.7035825&max_distance=2000000&stores_by_page=300&page=",
            "decathlon.es",
            "ES",
        ],
        [
            "https://api.woosmap.com/stores/nearby?key=woos-77d134ba-bbcc-308d-959e-9a8ce014dfec&lat=50.52645&lng=9.696555&max_distance=2000000&stores_by_page=300&page=",
            "decathlon.de",
            "DE",
        ],
        [
            "https://api.woosmap.com/stores/nearby?key=woos-c7283e70-7b4b-3c7d-bbfe-e65958b8769b&lat=48.856697&lng=2.3514616&max_distance=1500000&stores_by_page=300&page=",
            "decathlon.fr",
            "FR",
        ],
        [
            "https://api.woosmap.com/stores/search?key=woos-8833f380-7dec-353e-bef7-6b064a097516&lat=59.32512&lng=18.071093&max_distance=2000000&stores_by_page=300&page=",
            "decathlon.se",
            "SE",
        ],
        [
            "https://api.woosmap.com/stores/nearby?key=woos-02fa0b82-a54d-3cc3-bdfa-3ce69249f220&lat=39.920788&lng=32.85405&max_distance=1500000&stores_by_page=300&page=",
            "decathlon.com.tr",
            "TR",
        ],
        [
            "https://api.woosmap.com/stores/nearby?key=woos-1a635f2d-aee1-3a1d-a21e-a8fe3ae1da21&lat=52.2356&lng=21.01037&max_distance=1500000&stores_by_page=300&page=",
            "decathlon.pl",
            "PL",
        ],
        [
            "https://api.woosmap.com/stores/nearby?key=woos-8e13088e-16a2-322a-9440-1681be0d34ef&lat=50.087467&lng=14.421253&max_distance=1500000&stores_by_page=300&page=",
            "decathlon.cz",
            "CZ",
        ],
        [
            "https://api.woosmap.com/stores/nearby?key=woos-9f8c8ff6-ebbf-34aa-ae1c-437fde9f85e7&lat=50.846558&lng=4.351697&max_distance=1500000&stores_by_page=300&page=",
            "decathlon.be",
            "BE",
        ],
        [
            "https://api.woosmap.com/stores/nearby?key=woos-a11e8e0e-80e2-35e1-8316-ca1d015a4ed0&lat=46.76938&lng=23.589954&max_distance=1500000&stores_by_page=300&page=",
            "decathlon.ro",
            "RO",
        ],
        [
            "https://api.woosmap.com/stores/search?key=woos-1cbecb65-1565-309b-829b-673fb4e70b03&lat=46.04998&lng=14.50686&max_distance=1500000&stores_by_page=300&query=type:%22PHYSICAL_STORE%22&page=",
            "decathlon.si",
            "SI",
        ],
        [
            "https://api.woosmap.com/stores/search?key=woos-2dc9f151-9bc1-3e29-b440-91fa944449ef&lat=45.8150108&lng=15.9819189&max_distance=1500000&stores_by_page=300&query=type:%22PHYSICAL_STORE%22&page=",
            "decathlon.hr",
            "HR",
        ],
        [
            "https://api.woosmap.com/stores/search?key=woos-e244e48a-8ad6-3e09-8287-3f73daaafeb7&lat=48.717228&lng=21.249678&max_distance=1500000&stores_by_page=300&&query=type:%22PHYSICAL_STORE%22&page=",
            "decathlon.sk",
            "SK",
        ],
        [
            "https://api.woosmap.com/stores/search?key=woos-f1363832-508b-3056-820f-e8a3e3783782&lat=42.697865&lng=23.322178&max_distance=1500000&stores_by_page=300&query=type:%22PHYSICAL_STORE%22&page=",
            "decathlon.bg",
            "BG",
        ],
        [
            "https://api.woosmap.com/stores/search/?key=woos-25d7be73-ee80-3e98-915d-a5349756f5d2&lat=41.893322&lng=12.482932&max_distance=2000000&stores_by_page=300&page=",
            "decathlon.it",
            "IT",
        ],
        [
            "https://api.woosmap.com/stores/search/?key=woos-3019bc60-8e57-3c2a-8e6f-1893e1e44466&lat=52.37276&lng=4.8936043&max_distance=2000000&stores_by_page=300&page=",
            "decathlon.nl",
            "NL",
        ],
        [
            "https://api.woosmap.com/stores/search/?key=woos-7b40f2ea-b0a6-3a3b-9315-53ca807b601c&lat=47.050545&lng=8.305469&stores_by_page=300&page=",
            "decathlon.ch",
            "CH",
        ],
        [
            "https://api.woosmap.com/stores/search/?key=woos-c224dd3f-84cf-336c-a5f8-ef7272389ae3&lat=38.707752&lng=-9.136592&stores_by_page=300&page=",
            "decathlon.pt",
            "PT",
        ],
        [
            "https://api.woosmap.com/stores/search/?key=woos-f4e1c407-8623-32f6-aaf9-c586e8ef2337&lat=47.497993&lng=19.04036&stores_by_page=300&page=",
            "decathlon.hu",
            "HU",
        ],
    ]

    for param in params:
        api = param.pop(0)
        locator_domain = param.pop(0)
        country_code = param.pop(0)

        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:95.0) Gecko/20100101 Firefox/95.0",
            "Accept": "*/*",
            "Referer": f"https://www.{locator_domain}/",
            "Origin": f"https://www.{locator_domain}",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "cross-site",
            "Connection": "keep-alive",
        }
        for i in range(1, 100):
            r = session.get(api + str(i), headers=headers)
            js = r.json()["features"]

            for j in js:
                p = j.get("properties") or {}
                g = j.get("geometry") or {}
                a = p.get("address") or {}

                store_number = p.get("store_id")
                location_name = p.get("name")
                try:
                    phone = p["contact"]["phone"]
                except:
                    phone = SgRecord.MISSING

                page_url = f"https://www.{locator_domain}/store-view/-{store_number}"
                lines = a.get("lines") or []
                street_address = " ".join(lines)
                city = a.get("city")
                postal = a.get("zipcode")
                longitude, latitude = g.get("coordinates") or [
                    SgRecord.MISSING,
                    SgRecord.MISSING,
                ]

                _tmp = []
                days = [
                    "Monday",
                    "Tuesday",
                    "Wednesday",
                    "Thursday",
                    "Friday",
                    "Saturday",
                    "Sunday",
                ]
                try:
                    hours = p["opening_hours"]["usual"]
                except KeyError:
                    hours = dict()

                for k, v in hours.items():
                    index = int(k) - 1
                    day = days[index]
                    if not v:
                        continue
                    try:
                        start = v[0]["start"]
                        end = v[0]["end"]
                    except:
                        continue
                    _tmp.append(f"{day}: {start}-{end}")

                hours_of_operation = ";".join(_tmp)

                row = SgRecord(
                    page_url=page_url,
                    location_name=location_name,
                    street_address=street_address,
                    city=city,
                    zip_postal=postal,
                    country_code=country_code,
                    phone=phone,
                    store_number=store_number,
                    latitude=latitude,
                    longitude=longitude,
                    locator_domain=locator_domain,
                    hours_of_operation=hours_of_operation,
                )

                sgw.write_row(row)

            if len(js) < 300:
                break


if __name__ == "__main__":
    session = SgRequests()

    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        fetch_data(writer)
