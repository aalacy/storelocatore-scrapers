from bs4 import BeautifulSoup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgzip.dynamic import DynamicZipSearch, SearchableCountries

from sgrequests import SgRequests


def fetch_data(sgw: SgWriter):

    session = SgRequests()

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers2 = {"User-Agent": user_agent}

    locator_domain = "https://www.flooranddecor.com/"
    base_link = "https://www.flooranddecor.com/on/demandware.store/Sites-floor-decor-Site/default/Stores-GetStores?ajax=true"

    headers = {
        "authority": "www.flooranddecor.com",
        "method": "POST",
        "path": "/on/demandware.store/Sites-floor-decor-Site/default/Stores-GetStores?ajax=true",
        "scheme": "https",
        "accept": "*/*",
        "content-length": "178",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "en-US,en;q=0.9",
        "content-type": "application/x-www-form-urlencoded",
        "cookie": "dwanonymous_ed51eafc6e98b4290396e36e1e738830=abwpfn5brvVtrV54T7w9XHmGC8; StoreID=194; insyncai_chat_uuid=3290474810421; _pxvid=9f70e23b-908a-11ec-9f40-456541416e58; mt.v=2.558468663.1645168563095; __cq_uuid=abnBzGUPK7EaZq9ahcu1AkOcSo; __cq_seg=0~0.00!1~0.00!2~0.00!3~0.00!4~0.00!5~0.00!6~0.00!7~0.00!8~0.00!9~0.00; _svsid=3216cb69dbc8e575374773ca905b1f08; RES_TRACKINGID=436172373091113; _ga=GA1.1.338163422.1645168700; flooranddecor.com=GA1.2.338163422.1645168700; mdLogger=false; kampyle_userid=6a6b-e6f6-4fd6-980d-617d-3a16-d716-0a48; dwac_bdy9IiaaiE8gaaaadbNEk9Ijqu=BdEPh1AYLmB8jMDyx4onzmXqTd0GqF2iUbQ%3D|dw-only|||USD|false|America%2FNew%5FYork|true; cqcid=abwpfn5brvVtrV54T7w9XHmGC8; cquid=||; sid=BdEPh1AYLmB8jMDyx4onzmXqTd0GqF2iUbQ; __cq_dnt=0; dw_dnt=0; dwsid=xgXXZUoP5uodl8Z09GisUqY-lT8cv5UoMK8XeWmKjf4FFtKAJAwivYpBJqdpl-gaj_q_dC1RIpdS5X8-xCme3g==; _pxhd=d4kPFSnzKOfj4r3evaz3IOlyfJ85/qh87zD3edltZIfjcggpPuTN90SpC0TAFjEzxgbKC4-ucJvm743WRTct7g==:YJEZ3BuLqKr-mHc7RA26rK2ZJ84CaAIUowYNMkCbQifOLu8z-YZDobbUtA2IbC1ipXDwZ0iwx2ivD-vNf0wu26QA16Wqkn36t3HnZXWtg8w=; pxcts=aefe8500-952b-11ec-a6f1-5642647a6462; __olapicU=1645677542585; flooranddecor.com_gid=GA1.2.2058428041.1645677543; kampyleUserSession=1645677543630; kampyleUserSessionsCount=11; BVBRANDID=81fdb9c2-2086-4fc9-93cf-8e06f54b96a4; BVBRANDSID=6f2aebd3-18e1-46b7-891e-3ed71226ea19; BE_CLA3=p_id%3DRJ28J424RN64RJJPNJ68P6J4RAAAAAAAAH%26bf%3Dda358ddb4c1835103e16e13f79cec8e7%26bn%3D2%26bv%3D3.43%26s_expire%3D1645763991345%26s_id%3DRJ28J424RN64RAL22RL8P6J4RAAAAAAAAH; _px2=eyJ1IjoiY2QzZjhmZjAtOTUyYi0xMWVjLTg2ZGYtZjk2NzNlNjdjYWQ0IiwidiI6IjlmNzBlMjNiLTkwOGEtMTFlYy05ZjQwLTQ1NjU0MTQxNmU1OCIsInQiOjE2NDU2Nzc4OTE3MTQsImgiOiJjY2ZlNWFiNTgxZTZiNzAwMzkwOTI3Y2M2NGM4MDUwZDU3NzkxNTM0YTQ4NjZmMGM5OWYzMWM3NjRhY2ZlODNhIn0=; kampyleSessionPageCounter=2; _ga_39EFENHN6Y=GS1.1.1645677543.2.1.1645677593.0; OptanonAlertBoxClosed=2022-02-24T04:40:03.485Z; OptanonConsent=isGpcEnabled=0&datestamp=Thu+Feb+24+2022+00%3A40%3A03+GMT-0400+(Atlantic+Standard+Time)&version=6.29.0&isIABGlobal=false&hosts=&consentId=8e4c49c1-1ba3-4794-a218-af06c3148646&interactionCount=2&landingPath=NotLandingPage&groups=C0001%3A1%2CC0002%3A0%2CC0003%3A0%2CC0004%3A0&AwaitingReconsent=false; utag_main=v_id:017f0bb224720093b8e0764bac0805068002406000bd0$_sn:2$_se:7$_ss:0$_st:1645679461162$ga_cid:338163422.1645168700$dc_visit:1$ses_id:1645677542250%3Bexp-session$_pn:2%3Bexp-session",
        "origin": "https://www.flooranddecor.com",
        "referer": "https://www.flooranddecor.com/stores",
        "sec-ch-ua": '"Chromium";v="92", " Not A;Brand";v="99", "Google Chrome";v="92"',
        "sec-ch-ua-mobile": "?0",
        "sec-fetch-dest": "empty",
        "sec-ch-ua-platform": '"Linux"',
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "x-requested-with": "XMLHttpRequest",
        "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36",
    }

    search = DynamicZipSearch(
        country_codes=[SearchableCountries.USA],
        max_search_distance_miles=1000,
        expected_search_radius_miles=1000,
    )

    for postcode in search:
        payload = {
            "dwfrm_storeLocator_search": postcode,
            "search": "search",
            "dwfrm_storeLocator_radius": "999",
            "viewMoreStartPageNum": "undefined",
            "useMyLocation": "",
            "latitude": "undefined",
            "longitude": "undefined",
            "country": "undefined",
        }

        try:
            stores = session.post(base_link, headers=headers, data=payload).json()[
                "stores"
            ]["allStoresList"]
        except:
            continue

        for store in stores:
            location_name = store["name"]
            if store["isUpcomingStore"]:
                continue
            try:
                street_address = (store["address1"] + " " + store["address2"]).strip()
            except:
                street_address = store["address1"]
            city = store["city"]
            state = store["stateCode"]
            zip_code = store["postalCode"]
            country_code = store["countryCode"]
            phone = store["phone"]
            location_type = store["storetype"]
            latitude = store["latitude"]
            longitude = store["longitude"]
            search.found_location_at(latitude, longitude)
            store_number = store["ID"]
            link = "https://www.flooranddecor.com/store?storeID=" + str(store_number)
            hours_of_operation = BeautifulSoup(store["pickupHours"], "lxml").get_text(
                " "
            )
            if store["storeStatus"]["temporarilyClosed"]:
                hours_of_operation = "Temporarily Closed"
            if store["storeStatus"]["comingSoon"]:
                continue
            if store["storeStatus"]["closed"] or "CLOSED" in location_name.upper():
                hours_of_operation = "Closed"

            if "cannot be" in hours_of_operation:
                req = session.get(link, headers=headers2)
                base = BeautifulSoup(req.text, "lxml")
                try:
                    hours_of_operation = " ".join(
                        list(
                            base.find(
                                class_="b-storelocator_hours-list"
                            ).stripped_strings
                        )
                    )
                except:
                    if "closed for rebuild" in base.text.lower():
                        hours_of_operation = "Temporarily Closed"
                    else:
                        hours_of_operation = ""

            sgw.write_row(
                SgRecord(
                    locator_domain=locator_domain,
                    page_url=link,
                    location_name=location_name,
                    street_address=street_address,
                    city=city,
                    state=state,
                    zip_postal=zip_code,
                    country_code=country_code,
                    store_number=store_number,
                    phone=phone,
                    location_type=location_type,
                    latitude=latitude,
                    longitude=longitude,
                    hours_of_operation=hours_of_operation,
                )
            )


with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
    fetch_data(writer)
