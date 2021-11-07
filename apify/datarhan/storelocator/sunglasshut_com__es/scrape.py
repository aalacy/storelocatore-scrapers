from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries


def fetch_data():
    session = SgRequests("es")
    start_url = "https://www.sunglasshut.com/AjaxSGHFindPhysicalStoreLocations?latitude={}&longitude={}&radius=200"
    domain = "sunglasshut.com/es"
    hdr = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:93.0) Gecko/20100101 Firefox/93.0",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,ru-RU;q=0.8,ru;q=0.5,en;q=0.3",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "Pragma": "no-cache",
        "Cache-Control": "no-cache",
        "Cookie": "WC_PERSISTENT=BYYp6atpXXFj9KRWOtK%2BwcrHMuhQkQYC3MCKgzG%2FMGw%3D%3B2021-11-02+09%3A06%3A32.545_1634211929715-371697_13251_1454297134%2C-5%2CEUR_13251; SGPF=3B8o3cxU_dhqnD8S0Xertgw6-GQAVrfkg6p1lE4wlhefrT_m2gQNZEQ; forterToken=b62cfed74f08415a93f7554e6c3284a1_1635843992011__UDF43_6; utag_main=v_id:017c7e9f3485004a7991916f2a1800052003900f00838$_sn:4$_se:1$_ss:1$_st:1635845793995$vapi_domain:sunglasshut.com$dc_visit:4$ses_id:1635843993995%3Bexp-session$_pn:1%3Bexp-session$dc_event:1%3Bexp-session$dc_region:eu-central-1%3Bexp-session; AMCV_125138B3527845350A490D4C%40AdobeOrg=-1303530583%7CMCIDTS%7C18934%7CMCMID%7C37154648669072542591651943396872180891%7CMCAAMLH-1636448794%7C6%7CMCAAMB-1636448794%7C6G1ynYcLPuiQxYZrsz_pkqfLG9yMXBpb2zX5dvJdYQJzPXImdj0y%7CMCOPTOUT-1635851194s%7CNONE%7CMCSYNCSOP%7C411-18939%7CMCAID%7CNONE%7CvVersion%7C3.3.0; mt.v=2.1070531774.1634211935915; ftr_ncd=6; CONSENTMGR=consent:true%7Cts:1634211939030; s_ecid=MCMID%7C37154648669072542591651943396872180891; _gcl_au=1.1.2144750046.1634211940; _scid=f0b35c0a-5a69-4c65-971a-98af2eb8a726; __utma=110589831.161057800.1634211941.1635695818.1635843999.4; __utmz=110589831.1634211941.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); _fbp=fb.1.1634211941551.302339796; cto_bundle=FYKfxl9zYnpVc0xndE84SnFFcFZPeGZYdjZudTFsJTJGczRETWROMTVHTHEwc1dDV0dNQjVzc1pPSHN4d1Y0WU02STVCbm9iM05ZS0FNVFVlRlJ0UFFkdGZTWU5OT1hXSjlNOFFMJTJGWVVaYUNRRXFNVjZJM1RVS3NGSFp6cVdBZlpjbllHJTJGUXhodyUyRkRiM0VrdDJ5RVk0eGolMkZGbFVUallSZjV0Yk9EREc4Z1FBcldmUHViQUdUNlF0d280VzFjMHBKSzRZUUhoVWdKRlVOc1J6Sll4ektDNGdOSmdGQSUzRCUzRA; __wid=181321761; JSESSIONID=0000ogMA-GWIfaAXSXQ-a_nMopo:1c7qtpec2; metroCode=0; COUNTRY=HK; CATALOG_ASSORTMENT=SGH; WC_SESSION_ESTABLISHED=true; TS011f624f=015966d29290b9310bb29d38a14635e1d6fe5c01104aa5a7108be6d8c20ec87e8610f6e781f524156f2206ddec93d343e2cb04c7187a3b363501ccab73fa96e2b08b2908e7c1c6ab8814a6f363719ed4cce3da6c9014c99313e852d88955955ddc350a5249eef3dc1e9fd43ef8ed3a7efd9b1893d0ec42fef372fbace3f32711b58c6216f6f89fc7dfd0be35533145b689d4a2b5035a589b541632287fdb5bb74fdcfa214cfd0cc74222224b7fdb5dc63e6f1583a5151c7569260913461d335bffecd8db6d; aka-cc=ES; aka-ct=BARCELONA; aka-zp=; ak_bmsc=B022A205385E9362C470F2B68A82B72D~000000000000000000000000000000~YAAQZmwQAo667s18AQAALnXm3w1rFoVjhDeZIiHWkRHoHiC+h+vNvaXrtkQAFZbM9Dv0WyfBtHhjlTnUz8tIQt95/mfBAKOUYNYQ13pm+7se6gCRleZ/4LeNKqPOU7OA0RcXuPqHRf9xWNQdPyxckA4vCKiDRvPaHBTmKxwUbwU3UM2QHhy0B0nlRVCuW2tH+EkzXJwL9nnOnlJBzB54ChE/c0H4IFCNQnfmopdY+NTsy9GGvaUMZTzJGAllG3PzVCtXp9C7hkop23aerhhxNV+zhWJQfjRYhPbcrjwSBLGT5uC3yAGxxtM0pIN2NeidcFi2e+tI5ZefU64S5oVSGBT9g63KZLVLw5Lk05wINVq6GHA+FEoVOk6xKmOIWdvXOGngUIsVkdwsXAZMEZRGt0yeVN7Puhm9O239SFw65UpRwwyuflfzyL0RdXey460CeZahRT85A87PdTLfR6GtOKEDbfJWDPc4GQR5AuNQmDF3v8HA438azqyDabSmpQl3IrijgMOaT4NbVfIKzzxVByLAhVZCv8AQUA==; dtCookie=v_4_srv_6_sn_E9P3DJ3D7ENQG1QS7QD03BONQ8B8VVEH_app-3Ab359c07662f0b428_0_ol_0_perc_100000_mul_1; rxVisitor=163584399095795JLRVTROKIQ83PKVHC2MV8R0BK78KSD; dtPC=-6$243990942_808h-vCACPVFDCMUGLSVLEUEDQWQPDKCPRAFSA-0; rxvt=1635845796188|1635843990960; dtLatC=259; dtSa=-; sgh-desktop-facet-state-plp=categoryid:undefined|gender:true|brands:partial|polarized:true|price:true|frame-shape:partial|color:true|face-shape:false|fit:false|materials:false|lens-treatment:false; sgh-desktop-facet-state-search=; WC_AUTHENTICATION_1454297134=1454297134%2C5az0Naf5fL%2BXviCuJor%2BjwFQQI8VhLViyikeoHRnYrM%3D; WC_ACTIVEPOINTER=-5%2C13251; WC_USERACTIVITY_1454297134=1454297134%2C13251%2Cnull%2Cnull%2C1635843992548%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2C1892784604%2C%2BF7j2CaroB6k01KHlsKIuZSDNRe26a6bZKHpxJJ3jdtbThCBXDMjE3UckEReSTTpLI0U4F3XqlM1gXVw%2Boz%2FVT2tdFbQ%2Fu894awwd0AzAQ4MkqxjfPx14tqzzckSbUOim5%2F5iH5CCdBj32oek5Vh4imufjuM92Am9xcEhcT1l2987IbOFMk0LvhDJv7XvonB1qgx9alM%2FQCfHNgJKZ5dkGhl6fHXixX9qyuMtGJrjQZX10k19JXvvIPc4AtxVvkncvRi74ddW4cop23UXCFALQ%3D%3D; bm_sv=55D24D8DC72734C09899CAFFCBC47EB3~LIO89syKkHlcEVvJBwJ90UqXyWEWa+mDiKjfEX1+8WHnPL0/5E2ekCup8CAOKGESXFmkrtfAe3u5+mylm0576zD8wdVf1a+W34x0+zwfFq0e0psry2x7ybEBdoY+ZwhjKUEDPo0SxJgrRA/Uxh5PvypWeNHhnp5gzvhxOii7eYA=; tealium_data_session_timeStamp=1635843994029; userToken=undefined; TrafficSource_Override=1; AMCVS_125138B3527845350A490D4C%40AdobeOrg=1; _cs_mk=0.8143903819341953_1635843995295; s_cc=true; __utmb=110589831.2.9.1635843999; __utmc=110589831; __utmt=1",
    }
    all_coords = DynamicGeoSearch(
        country_codes=[SearchableCountries.SPAIN], expected_search_radius_miles=100
    )
    for lat, lng in all_coords:
        data = session.get(start_url.format(lat, lng), headers=hdr).json()
        all_locations = data["locationDetails"]
        for poi in all_locations:
            hoo = []
            for e in poi["hours"]:
                hoo.append(f'{e["day"]} {e["open"]} - {e["close"]}')
            hoo = " ".join(hoo)
            item = SgRecord(
                locator_domain=domain,
                page_url="https://www.sunglasshut.com/es/sunglasses/store-locations",
                location_name=poi["displayAddress"],
                street_address=poi["shippingDetails"]["street"],
                city=poi["shippingDetails"]["city"],
                state="",
                zip_postal=poi["shippingDetails"]["zipCode"],
                country_code=poi["shippingDetails"]["country"],
                store_number=poi["id"],
                phone=poi["phone"],
                location_type=poi["storeType"],
                latitude=poi["latitude"],
                longitude=poi["longitude"],
                hours_of_operation=hoo,
            )

            yield item


def scrape():
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {SgRecord.Headers.LOCATION_NAME, SgRecord.Headers.STREET_ADDRESS}
            )
        )
    ) as writer:
        for item in fetch_data():
            writer.write_row(item)


if __name__ == "__main__":
    scrape()
