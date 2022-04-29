import json
from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sglogging import sglog

session = SgRequests()
logger = sglog.SgLogSetup().get_logger(logger_name="liverpool.com.mx")

headers = {
    "content-type": "application/json",
    "cookie": 'dtCookie=v_4_srv_8_sn_1C9D90FA6898102E28A5EAF69A17791A_perc_100000_ol_0_mul_1_app-3Afb4b113cea6706c5_0; DCC=SiteC; rxVisitor=165028435529989NR676SJVDREL4PP9JCI0VF4Q9I4QGJ; PIM-SESSION-ID=o9iiP3VLnunMEdUR; _evga_fb08={%22uuid%22:%229e6409e25a9ee0e3%22}; genero=x; segment=fuero; _sfid_a127={%22anonymousId%22:%229e6409e25a9ee0e3%22%2C%22consents%22:[]}; gbi_visitorId=cl24ops4x00013071xjzylee7; _gcl_au=1.1.1284697809.1650284401; _tt_enable_cookie=1; _ttp=c060f861-6971-4630-b6d7-b113b3adb9e7; dtSa=-; _pin_unauth=dWlkPU1HSmxORGRtWlRndE9HRm1OUzAwTXpZeUxXSTNOR1l0WVdObFltTXdNR0l3T1RZMg; _fbp=fb.2.1650284438814.1015482645; FPID=FPID2.3.p2YPmHw6adnbe1h%2FT9CG9u4wwkLtJT4XSPrE582RRgc%3D.1650284401; mf_ab2c90eb-0ce8-4da9-87ed-971baf81bd44=|.-4185382347.1650284456612|1650284401700||0|||0|0|81.51857; AKA_A2=A; _abck=E1B4056BC86D4D1640F5403D1FE27C61~0~YAAQv2PUF/O0TUKAAQAANZg9aQc0TSEdLLSsn1KxqIWDvGvJSL6XmgM+Ep+7J23tgIVKrBo3yfuVnZGpLZa6rwoSiTMD5SmOZEpl1K3Vzj8eNJQn2mWkYRgBDLTOEGxBT9LYu53Dcw0WQWvVefegVRDKW28SHzZj+jvgrsJyLJaIca0Oq74MH/eDFSijtO3TJ5GcPGZhK8mjqcSZOeXIjRFCguhyQCzy/sZdeMW+qn0QMrIWTrdXR/3Yrb+EdrcXGsDV2pF48g2zeDS/pQGlYknKBVBNdIi6KcjyR0jwMwuVKVr+LZ4FxGGriDvCLDV9BGyT7Rjij5ksJqH31x9UmXGHmldEZq+JTAbyXZYZeu5lqthJy24LLjubVUXBA2TGKiAy00qTyCaVtdoG2BMSygwkzBCyjwEVi2RPp3g=~-1~-1~-1; ak_bmsc=28030AE65D7F58AA2C44E3ED15061206~000000000000000000000000000000~YAAQv2PUF/S0TUKAAQAANZg9aQ+QbWql70JU8eit9CaqZaoEzXjsJLZwI+2w0PQsYnn+dS26fQ0Eg9H8IA4m234MDhnKVRwX90/FRbq+ZBtauDBE2VPDxl2XbAsWD57ZSlG66W1KIORY+NxMBOB22WABc0IK5xvDpnXHzLZxwekUrMZ5IayGJLTgu44ptZivQIOq125+NAAl9CEvR0OcWT61RCe1dXghu2ssrh7lGipyklYkh3S+msLb77NDvc8R1SAXWVM6ytGdefCYSMyiKqTglE0wk0bVmc6snidpp9vDlo8p+t3FxPbQYPz8jIUDaJbF8Fs4ozj8F5RxvtkcIJJRkfESWQL38edaXHQX4jerK1VLQd3LvkhWr8w5pV26IQCrWgkqh51Uj2XI7UWCxg==; bm_sz=100B310B345C43FFD940C4AB3596816B~YAAQv2PUF/W0TUKAAQAANZg9aQ/T+ThCycdE2Gwr7y4hL0v1s+JUVh43vbbYceaXBMYszuIgHhPzpff8AdxDZVsnEuyipMptKqZ6v90wYlIb1La4BlV/a4GTFabSa5Mv6jadK8ckvizR6nDsh0kt4YfRWX4pu730klunwYZ5UslWkRD5Swb4eIjEjGbzQL6g2/i9YgkI2ouTeBMFFsN40kfrTuUzGYi1yv2+itCS5iuOXjbxdcJw3DPZzGIszuBCdW8GRUXZzaYRHhUqyr8fhXdRy67Au1zvB+IaAgEHK1avtWKt6eugkac=~3486265~3158595; session_dc_qv=1; _gid=GA1.3.1893788404.1651033088; JSESSIONID=57NpPawYs1j2vpzBQF-JKsRX3tbPj1ASeF51pDEXCWjSzbMRHVXd!-803858014; nearByStore=; homeDeliveryStore=; _ga=GA1.1.1064617581.1650284401; _scid=a0c4066a-ed74-4b0b-8330-f88a763b19f5; _sctr=1|1650996000000; akavpau_allow=1651033222~id=51ecae62621c32c07de52a8c70c2c3e5; bm_sv=5156E89638E9C93CC065EE1EF6162C7F~FHAxinY3j4q6TJRwhtRhPIHUizdJjKDyG87rephQuQfYv+sSDfpWOO+ZPV6dske6Hui/kq+T/+x4wJrxdVASnUq9HFsjl1RXZigA3dm03IgDnUMAzHBt/ylj3CuIcV3BaHZKg1Y3GQO+u9PjxUVR46ONSan4KhId+F471Njyr4w=; RT="z=1&dm=www.liverpool.com.mx&si=88ed0040-4993-44e1-920f-5be112f94588&ss=l2h2gy0a&sl=1&tt=48j&rl=1&ld=48u&ul=1mpp&hd=1nj9"; _ga_0WY68EFMNB=GS1.1.1651033162.3.0.1651033162.0; _ga_171XPPQ282=GS1.1.1651033091.1.1.1651033162.60; _ga_ZF6SNY8CLK=GS1.1.1651033091.2.1.1651033162.60; dtPC=8$433162923_130h1vRGPKGQNSDGELAWHKQUDNOPGSOHPDFHRH-0e0; dtLatC=137; rxvt=1651034962941|1651033086802; mf_4b65f806-7a98-46e9-bed7-78c70a09f4dd=|.-4185382347.1651033163150|1651033088204||0|||0|0|23.22971; _abck=E1B4056BC86D4D1640F5403D1FE27C61~-1~YAAQF8IRYGn8tE+AAQAAeqZLaQc/L8tk0M/KUzQZK77bRa4xw7hSSlzm8jrolLMgSoEizd4MKfT14z/9qJNO6XMI4VI2XiRvug7+/8MUZYQ0GIkSHbK6lICRF4MNy+ZkbaLIJjRHXjNfML41f/yj6m5gqhGOWU7gz9qSPzjQ1+z1Z3M8nCX7UbopRytLs4IPQCZseAKUnF5RhQKn9ouXUkJobSN4NIS6dT3zB1ei80F+haYJwAjcNVjYH1lowOv6Tj5BghPljx2i+M4OunVxyXoYr5nHnx/nXDGhtauQm4qQQ3u3v8DO8KTwItzL75gcXKXDjEcp9kOr2mxgxm0GtoDsIuphY7JsjcOmexEWJa4kaQLKZVUQzLuadgks3O60OyHuw1JWD0MOPV/obdwlWCgc9DOfymYsYK2eAiY=~0~-1~-1; bm_sv=5156E89638E9C93CC065EE1EF6162C7F~FHAxinY3j4q6TJRwhtRhPIHUizdJjKDyG87rephQuQfYv+sSDfpWOO+ZPV6dske6Hui/kq+T/+x4wJrxdVASnUq9HFsjl1RXZigA3dm03IgczrvHUKhVWUN+HES0etH5R3Q4NxqLOXIsceM2uge1dmqIVkyD95WhQXyPChEGmpQ=; akavpau_allow=1651034067~id=844ddbb3c97c17b875a8453eb0065457',
    "referer": "https://www.liverpool.com.mx/tienda/browse/storelocator",
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36",
}


def fetch_data():

    start_url = "https://www.liverpool.com.mx/tienda/browse/storelocator"
    domain = "liverpool.com.mx"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    logger.info(f"Crawling {start_url}, Response: {response}")
    dom = etree.HTML(response.text)
    data = dom.xpath('//script[@id="__NEXT_DATA__"]/text()')[0]
    data = json.loads(data)

    all_locations = data["props"]["pageProps"]["data"]["StoreDataContent"]["stores"]
    for poi in all_locations:
        store_number = poi["storeId"]
        frm = json.dumps({"storeId": store_number})
        post_url = "https://www.liverpool.com.mx/getstoredetails"
        response2 = session.post(post_url, data=frm, headers=headers)
        logger.info(f"{store_number} Response: {response2}")
        poi_data = response2.json()
        city = poi["city"].replace("-", "")
        if not poi_data.get("storeDetails"):
            continue
        street_address = (
            poi_data["storeDetails"]["StoreDetails"]["1"]["generalDetails"]
            .split("\n")[0]
            .strip()
            .split("<br")[0]
            .replace(",", "")
            .replace("<p>", "")
            .split("Col.")[0]
            .replace("</br>", "")
        )
        if city:
            street_address = street_address.split(city)[0]
        poi_html = etree.HTML(
            poi_data["storeDetails"]["StoreDetails"]["1"]["generalDetails"]
        )
        hoo = (
            [e.strip() for e in poi_html.xpath("//text()") if "horario" in e.lower()][0]
            .split("ienda:")[-1]
            .strip()
        )
        if not hoo:
            hoo = poi_html.xpath("//text()")[-1]

        item = SgRecord(
            locator_domain=domain,
            page_url=start_url,
            location_name=poi["name"],
            street_address=street_address,
            city=city,
            state=poi["state"],
            zip_postal=poi["postalCode"],
            country_code=poi_data["storeDetails"]["StoreDetails"]["1"]["country"],
            store_number=store_number,
            phone=poi_data["storeDetails"]["StoreDetails"]["1"]["phone"],
            location_type=poi["storeType"],
            latitude=poi["lpLatitude"],
            longitude=poi["lpLongitude"],
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
