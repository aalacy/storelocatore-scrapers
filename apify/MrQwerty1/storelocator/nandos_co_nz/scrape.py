from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def get_phone(page_url):
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)

    return "".join(
        tree.xpath(
            "//div[./a[contains(@href, 'google.com')]]/following-sibling::div[1]/div[1]/p/text()"
        )
    ).strip()


def fetch_data(sgw: SgWriter):
    api = "https://api.nandos.co.nz/public/graphql"
    data = '{"query":"query getRestaurants {\\n  restaurants {\\n    id\\n    name\\n    longitude\\n    latitude\\n    phone\\n    status\\n    openNow\\n    orderingEnabled\\n    tableOrderingEnabled\\n    dineInGuestCheckoutEnabled\\n    address {\\n      address1\\n      address2\\n      country\\n      postcode\\n      state\\n      suburb\\n    }\\n    openingHours {\\n      day\\n      openingTime\\n      closingTime\\n    }\\n    catering\\n    facilities\\n    deliveryServices {\\n      deliveroo {\\n        live\\n        link\\n      }\\n      uberEats {\\n        live\\n        link\\n      }\\n      menulog {\\n        live\\n        link\\n      }\\n      doorDash {\\n        live\\n        link\\n      }\\n    }\\n    averageOrderTime\\n    thresholds {\\n      lowerThresholdAmount\\n      orderType\\n      time\\n    }\\n    utcOffset\\n  }\\n}\\n","variables":{}}'
    r = session.post(api, headers=headers, data=data)
    js = r.json()["data"]["restaurants"]

    for j in js:
        location_name = j.get("name") or ""
        latitude = j.get("latitude")
        longitude = j.get("longitude")
        store_number = j.get("id")
        a = j.get("address") or {}
        street_address = f'{a.get("address1")} {a.get("address2") or ""}'.replace(
            ",", ""
        ).strip()
        city = a.get("suburb")
        state = a.get("state") or ""
        postal = a.get("postcode")
        slug = location_name.replace(" ", "-").lower()
        page_url = f"https://www.nandos.co.nz/restaurants/{state.lower()}/{slug}"
        phone = j.get("phone") or get_phone(page_url)

        _tmp = []
        hours = j.get("openingHours") or []
        for h in hours:
            day = h.get("day") or ""
            if "Public" in day:
                continue
            start = h.get("openingTime")
            end = h.get("closingTime")
            _tmp.append(f"{day}: {start}-{end}")

        hours_of_operation = ";".join(_tmp)

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code="NZ",
            phone=phone,
            store_number=store_number,
            latitude=latitude,
            longitude=longitude,
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.nandos.co.nz"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:94.0) Gecko/20100101 Firefox/94.0",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "ru,en-US;q=0.7,en;q=0.3",
        "Referer": "https://www.nandos.co.nz/restaurants/search?lat=-37.7825893&lng=175.2527624",
        "Content-Type": "application/json; charset=UTF-8",
        "Origin": "https://www.nandos.co.nz",
        "Connection": "keep-alive",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-site",
        "TE": "trailers",
    }

    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.GeoSpatialId)) as writer:
        fetch_data(writer)
