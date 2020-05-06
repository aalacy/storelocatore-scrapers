import csv
import urllib2
from sgrequests import SgRequests

session = SgRequests()
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36',
           'content-type': 'application/x-www-form-urlencoded',
           'cookie': '__cfduid=d9155e1df8c5b8b8b3298bc4428fbac011588175732; dwac_9d1228ad4643ec1468172ec451=TyKPxfmGWTwrRSLZl-WVptjQk_jSoBE01bk%3D|dw-only|||USD|false|US%2FEastern|true; cqcid=abCayRrImMvl3IzIa16So7Kksg; sid=TyKPxfmGWTwrRSLZl-WVptjQk_jSoBE01bk; dwanonymous_8a2bdb544ba8c883737645984d659e87=abCayRrImMvl3IzIa16So7Kksg; __cq_dnt=0; dw_dnt=0; dwsid=fSHXpU_sFxI2arWXx6TQT-rTy5hkyl8ayJZ-4X3iWPWahyUhNw-BochlneA41jtT8MBLMvJWX6iOFTDPtHpo7Q==; og_session_id=4dcff40029ab11e5b9c4bc764e106cf4.185788.1588175734; dw=1; dw_cookies_accepted=1; og_autoship=0; _gcl_au=1.1.405460616.1588175735; dtm_token=AQEKb0zjW6M-SQFOdbvvAQEJ1wE; _ga=GA1.2.690033303.1588175737; _gid=GA1.2.1666924229.1588175737; _pxvid=ddbe61dc-8a31-11ea-b11b-0242ac120008; TURNTO_VISITOR_SESSION=1; TT3bl=false; TURNTO_VISITOR_COOKIE=ZUrRNBq7k5P33AL,1,0,0,null,,,0,0,0,0,0,0,0; _li_dcdm_c=.gnc.com; _lc2_fpi=ed6a7a1c2bb5--01e73ad45190ea1gzksnf3v2sc; rdt_uuid=b7182f6c-510d-4d0b-aaab-3a43e9e40039; _fbp=fb.1.1588175737483.1018897570; _scid=a4f69f78-34d0-4559-ba1d-69ce05dbff6a; fs_uid=rs.fullstory.com#K8ANT#5009132774244352:4589156389109760/1619711737; _sctr=1|1588136400000; __qca=P0-1377769346-1588175741020; rdf-uuid=fc47ee21-2d15-484d-984f-47737a18f80c_1588175739385; rdf-count=1; __cq_seg=0~0.00!1~0.00!2~0.00!3~0.00!4~0.00!5~0.00!6~0.00!7~0.00!8~0.00!9~0.00; __cq_uuid=54db18e0-10a3-11ea-abf6-c165fe0275af; ysession=2321cc8d59da-5bb4ac11312e5802564a04fc; rkglsid=h-ecf5b404209dc63735afa31171c6a687_t-1588177056; _pxff_axt=540; _pxff_wa=1,702; _pxff_tm=1; _gat_UA-76347002-1=1; _dc_gtm_UA-76347002-1=1; TURNTO_TEASER_SHOWN=1588177119078; _uetsid=_uet93d8a100-1360-c922-8dac-7cb2c5238928; _br_uid_2=uid%3D7025917300837%3Av%3D11.8%3Ats%3D1588175737513%3Ahc%3D14; mp_gnc_mixpanel=%7B%22distinct_id%22%3A%20%22171c6a69239d6-0599d45663c2df-6373664-1fa400-171c6a6923a32b%22%2C%22bc_persist_updated%22%3A%201588175737405%7D; _px3=cc8ee8c1937f958a18d9f45de742d1c1ceeacdf44a38c825bf3936e8c39211c1:TIufIuezTFM1okA5kMUHoTNCIuyhtROQ5tvsRRXKjCA3t8FLgTgKLWgS5CpeaWTlNewCB7nfe30MgNWbvkav4Q==:1000:W/X08gZs06tLr/hwSEHJOMRdlj1l3oELFjD3iAVNiFs2J5B1fgr/R/AoGwKDMgBxPSiPC1JYG+9IGuwyOk8PRy+hdjPcsDGbskGFcsJDhc4lwe5uqz+gzcIT4v6NLRREezh+x483dvTIT7UdWlqw8gsWmRadKMC5JeXC1CH2WjY=; _derived_epik=dj0yJnU9U2hGRTFDV2RoNHQ4R1lFS0J1dUNTbExLN1JNM2lhZl8mbj1JdmJxQVFnelMzOGx5YUpJNWR3bE9BJm09NyZ0PUFBQUFBRjZwcU9B; _gali=primary'
           }

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def fetch_data():
    ids = []
    r = session.get('https://www.gnc.com/stores', headers=headers)
    zips = ['60007','10002','90210','96795','99515','98115','88901','87101','59715','80014','75001','32034','70032','37011','63101','58102','55408']
    for zipcode in zips:
        print(zipcode)
        url = 'https://www.gnc.com/on/demandware.store/Sites-GNC2-Site/default/Stores-FindStores'
        payload = {'dwfrm_storelocator_countryCode': 'US',
                   'dwfrm_storelocator_distanceUnit': 'mi',
                   'dwfrm_storelocator_postalCode': zipcode,
                   'dwfrm_storelocator_maxdistance': '500',
                   'dwfrm_storelocator_findbyzip': 'Search'
                   }
        r = session.post(url, headers=headers, data=payload)
        for line in r.iter_lines():
            if 'map.data.addGeoJson(' in line:
                items = line.split('"title":"')
                for item in items:
                    if '"storenumber":"' in item:
                        store = item.split('"storenumber":"')[1].split('"')[0]
                        website = 'gnc.com'
                        hours = ''
                        phone = ''
                        typ = '<MISSING>'
                        name = item.split('"')[0]
                        loc = 'https://www.gnc.com/store-details?StoreID=' + store
                        add = item.split('"address1":"')[1].split('"')[0]
                        if '"address2":"' in item:
                            add = add + ' ' + item.split('"address2":"')[1].split('"')[0]
                        zc = item.split('"postalCode":"')[1].split('"')[0]
                        city = item.split('"city":"')[1].split('"')[0]
                        state = item.split('"state":"')[1].split('"')[0]
                        lat = item.split('"coordinates":[')[1].split(',')[0]
                        lng = item.split('"coordinates":[')[1].split(',')[1].split(']')[0]
                        country = 'US'
                        if store not in ids:
                            ids.append(store)                        
                            if hours == '':
                                hours = '<MISSING>'
                            if phone == '':
                                phone = '<MISSING>'
                            r2 = session.get(loc, headers=headers)
                            print('Pulling Store #%s...' % store)
                            for line2 in r2.iter_lines():
                                if 'class="store-phone">' in line2:
                                    phone = line2.split('class="store-phone">')[1].split('<')[0]
                                if 'class="storeLocatorHours"><span><span>' in line2:
                                    hours = line2.split('class="storeLocatorHours"><span><span>')[1].split('</span></div>')[0]
                                    hours = hours.replace('</span><span><span>','; ').replace('</span>','').replace('<span>','')
                            yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
