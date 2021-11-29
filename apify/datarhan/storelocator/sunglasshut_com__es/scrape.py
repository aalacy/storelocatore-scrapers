from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries


def fetch_data():
    session = SgRequests("es")
    start_url = "https://www.sunglasshut.com/AjaxSGHFindPhysicalStoreLocations?latitude={}&longitude={}&radius=100"
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
        "Cookie": "WC_PERSISTENT=pvxfymwCzALvOSrfP9gbF121F%2FojaK4uV%2FbZCdPZ%2BMw%3D%3B2021-11-21+18%3A09%3A14.739_1634211929715-371697_13251_1455022385%2C-5%2CEUR%2CTh6ylU01ZhPdhnri1Vbt6aUe1tQd8fhLQ2M4HQhPeTjjZF0fYRwtFI1ahwOdGpkct53Jtu1LPmZuA2ZJrsewzw%3D%3D_13251; forterToken=b62cfed74f08415a93f7554e6c3284a1_1637519194741__UDF43_6; utag_main=v_id:017c7e9f3485004a7991916f2a1800052003900f00838$_sn:6$_se:14$_ss:0$_st:1637520995341$vapi_domain:sunglasshut.com$dc_visit:6$ses_id:1637517997986%3Bexp-session$_pn:9%3Bexp-session$dc_event:7%3Bexp-session$dc_region:eu-central-1%3Bexp-session; AMCV_125138B3527845350A490D4C%40AdobeOrg=-1303530583%7CMCIDTS%7C18953%7CMCMID%7C37154648669072542591651943396872180891%7CMCAAMLH-1638119816%7C6%7CMCAAMB-1638119816%7C6G1ynYcLPuiQxYZrsz_pkqfLG9yMXBpb2zX5dvJdYQJzPXImdj0y%7CMCOPTOUT-1637522216s%7CNONE%7CMCSYNCSOP%7C411-18960%7CMCAID%7CNONE%7CvVersion%7C3.3.0; mt.v=2.1070531774.1634211935915; ftr_ncd=6; CONSENTMGR=consent:true%7Cts:1634211939030; s_ecid=MCMID%7C37154648669072542591651943396872180891; _gcl_au=1.1.2144750046.1634211940; _scid=f0b35c0a-5a69-4c65-971a-98af2eb8a726; __utma=110589831.161057800.1634211941.1635843999.1637515022.5; __utmz=110589831.1634211941.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); _fbp=fb.1.1634211941551.302339796; cto_bundle=ja3ZE19zYnpVc0xndE84SnFFcFZPeGZYdjZzMEI5Zk1FQnk2VWhteDRnaXphVmtWSkxETkZzWFNsMFVBR2Vwakt0cldiSkEyRU5Yem5MTEY2WmhoUDNVaFZTVWVRS3V6U2ViU1kzUlpKTXR5OGZxTHF5Y05VMDd6Y1VnY3RIVFRsdXFzRkdRN3QlMkZoeU1iTFZ3SExNaW9oekJEb1liTiUyQmdLQjBYdkR4ZVRqemw4Q2ZNVTUlMkZVT25obG9WNWRXZCUyQkx3RkVZTkxUODNXZm4xZTZJNzkzR2NCWG8wQkElM0QlM0Q; ak_bmsc=6D00854A612AD53BC042143350569E2A~000000000000000000000000000000~YAAQZmwQAoI4/y19AQAAFjaAQw2gc9o1IhKmgLUo3AY1UrG/iyNBjP3p0nZ9ak5u5BC9uMxegdbwDnj5/MYGkCfreZDtOILa97R9NqagYqmJNvnBL4ZmXrxOiwKYyvT6SGs55q1xIM6zw8I/olkJ2L8s/6qdDqy52azvJfkwVHnE4+MdYJJWfYCC5ekMdfFBEhRvCiQaycSlycyRUYyEnyTizjIAE6pUFy6GAnsck1LDqnqaatJC6j59ItGXk/4nxcUxmBARDa5ta+MA22N/PsLp5MVVzxwFocFiTkhrYUtzjrEaNZZOTnDazni2aHdUGNTR9er5ufXez8V/bc8pElvY1LRwBBpTD7lnSmUS/RSS4OhuT81jnd/WnGZDIr5vLfS68n7+0dOz0h7D/eLdtsiYsqAo68Hm3CkwkWX3f0LSozAcuCxZpfK5yxXQfJCdbow1q+EK7Tm+J8+D2OP1m6hKk6UY24SY5n0A3qtIo0nOWlII5r3XK1vu7b5ntM8e+kahBGF4+y04aFOFa1Gi/ErkH5lVFo/kHA==; SGPF=3qVzDMEOvpkmcgxWwb1KF9pQIw0rlwpKtZH5cJCkWqx9XuLx4u6rqMA; dtCookie=v_4_srv_3_sn_97MBOCCJA7UBTG2MBVSR0EGTO12EMCGQ_app-3Ab359c07662f0b428_0_ol_0_perc_100000_mul_1; rxVisitor=1637402952738CCBKVT8E1CEPUNPV5TLT4U3BQG4RD618; dtPC=3$7133372_607h1vNFOFQJFNKCOMEKCMCBKRQMVEOMHEPKAW-0; rxvt=1637407803343|1637406003343; dtLatC=351; dtSa=-; TS011f624f=015966d292f1ee628de75afe37dbc9b36fcd72c99cf8b3ffad20ae05d451ab17d61fe7ea464747690a7afe2538ed66dff5cc9fd3af3d6f5ede200f73516fedcc421e7d0f5e29304b1337dc5ab742d4acafe99e9719ffb66e7591669a42f820facec7dd7324ad0bf41b30f50b894b7f63988d186302604d11fa0a8e27b3cdd132aff3334943695fffe95b50870cd8c63c8258deb7b7; sgh-desktop-facet-state-plp=categoryid:undefined|gender:true|brands:partial|polarized:true|price:true|frame-shape:partial|color:true|face-shape:false|fit:false|materials:false|lens-treatment:false; sgh-desktop-facet-state-search=; JSESSIONID=00007HW1exQDohu9splhr69g6FC:1c7qtq78c; bm_sv=A5BF8F32106FBFA5485F089E36F18910~8lswO4cbZyvHo2+w/t2kkaRqTxbt7uRG16JwVVyysOzpAkLW5OSC94cRBREV9N8ID8jqDEofHvc59gYLtI2zVwfHal4HULXDLpY0fuEhhmOL0ihcHhlfNpuIByakfx321AumgIRqDUA6r2dlQna9oA5Ql9/TwGAGaWAPvFuodeA=; tealium_data_session_timeStamp=1637515015022; userToken=undefined; TrafficSource_Override=1; __wid=128941861; AMCVS_125138B3527845350A490D4C%40AdobeOrg=1; s_cc=true; __utmc=110589831; MGX_UC=JTdCJTIyTUdYX1AlMjIlM0ElN0IlMjJ2JTIyJTNBJTIyYzNmNWViMzAtNTY1NC00N2RmLTk0ZWMtZmZmMDk5Y2U4YmMyJTIyJTJDJTIyZSUyMiUzQTE2MzgwNDA2MzQzOTYlN0QlMkMlMjJNR1hfUFglMjIlM0ElN0IlMjJ2JTIyJTNBJTIyYzc0Mjk2MjctYmU4OC00MmQ2LWJkZjEtZGQyNzE5NWI3Mjk3JTIyJTJDJTIycyUyMiUzQXRydWUlMkMlMjJlJTIyJTNBMTYzNzUxNjgzOTE4NiU3RCUyQyUyMk1HWF9DSUQlMjIlM0ElN0IlMjJ2JTIyJTNBJTIyOTY4Yzc5NGYtYzNlYy00ZjAxLWIxNjUtM2U4ZTNjMzA4NDZiJTIyJTJDJTIyZSUyMiUzQTE2MzgwNDA2MzQzOTglN0QlMkMlMjJNR1hfVlMlMjIlM0ElN0IlMjJ2JTIyJTNBMSUyQyUyMnMlMjIlM0F0cnVlJTJDJTIyZSUyMiUzQTE2Mzc1MTY4MzkxODYlN0QlMkMlMjJNR1hfRUlEJTIyJTNBJTdCJTIydiUyMiUzQSUyMm5zX3NlZ18wMDAlMjIlMkMlMjJzJTIyJTNBdHJ1ZSUyQyUyMmUlMjIlM0ExNjM3NTE2ODM5MTg2JTdEJTdE; _pin_unauth=dWlkPU56UTFNbUV5TUdNdE5EQTNNUzAwTlRNMExUaGpNbVl0WlROall6TmhNREE1TVRKaA; _cs_c=1; _cs_cvars=%7B%221%22%3A%5B%22Page%20Type%22%2C%22Static%22%5D%2C%222%22%3A%5B%22Page%20Name%22%2C%22Yext%3AStatic%22%5D%2C%223%22%3A%5B%22Page%20Section%201%22%2C%22Yext%22%5D%2C%224%22%3A%5B%22Action%22%2C%22AU%3AEN%3AD%3AYext%3AStatic%20%22%5D%2C%228%22%3A%5B%22User%20Login%20Status%22%2C%22undefined%22%5D%7D; _cs_id=b714dc55-a793-a139-927e-f1d21f0cf252.1637515039.2.1637518027.1637517993.1.1671679039921; s_sq=lux-sgh-prod%3D%2526c.%2526a.%2526activitymap.%2526page%253D%25252Fes%25252Fsunglasses%25252Fstore-locations%25252Fmap%2526link%253DBuscar%2526region%253Dcontent_wrapper_box%2526pageIDType%253D1%2526.activitymap%2526.a%2526.c%2526pid%253D%25252Fes%25252Fsunglasses%25252Fstore-locations%25252Fmap%2526pidt%253D1%2526oid%253DBuscar%2526oidt%253D3%2526ot%253DSUBMIT; _ga=GA1.2.161057800.1634211941; _gid=GA1.2.140689895.1637515049; _cs_s=4.0.0.1637519827847; __utmb=110589831.9.9.1637518157452; _cs_mk=0.9902537894095322_1637518001686; _uetsid=dfc111704aee11ec84ef61a511c0996b; _uetvid=dfc12d804aee11ecbb2f25e0c3b34998; aka-cc=ES; aka-ct=MADRID; aka-zp=; WC_SESSION_ESTABLISHED=true; WC_AUTHENTICATION_1455022385=1455022385%2CPr1z7P4PRyU91vjkagsQodgH1f7suy5d8nyTlAogX5c%3D; WC_ACTIVEPOINTER=-5%2C13251; WC_USERACTIVITY_1455022385=1455022385%2C13251%2Cnull%2Cnull%2C1637518154742%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2C2140635307%2Ccj6RwcBbF4RGSmzprk25xCmwXB5jkP%2FIBl9iShE535z57m2fOIAhueLJXhiCxbYoer%2BwBxzzndn0JvNTz4wD4uBIqq5NMpyoQRNUG8CIv38ESeY0TVeE0lPmdqF2T1lv1Mws6mgYZ%2FaunevMQf14s%2B9yl%2F0%2BjbFBna8Bcy%2B9NHNPhtPJElTpLBCXb5vR0Gdy6hn6kV4jEImRyeOhQLSxFKrtaQk4o7y1jXg9YGBAt3Y7WJwrs7G4iWzuVnhTXf3AstYZnn9jmKkhiBsAnAwFeg%3D%3D",
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
