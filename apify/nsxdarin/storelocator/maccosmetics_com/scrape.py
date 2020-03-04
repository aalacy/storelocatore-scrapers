import csv
import urllib2
from sgrequests import SgRequests

session = SgRequests()
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36',
           'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
           'cookie': 'has_js=1; client.isMobile=0; MP_CONFIG=%7B%22language_id%22%3A48%2C%22country_id%22%3A1%7D; SESSION=937981927-3742c9ae87b5284400c4b4eb2a66c4e94ff327f85324ceb487a47a7bc77b93ab; ngsession=4a3e09de80041664; LOCALE=en_US; ngglobal=4a3e09de08959879; PSN=%7B%7D; Auser=0%7C0%7C0%7C0%7C0%7C0%7C0%7C0%7C0-null; __ssid=84a7cf3108e05341bbcb11f1ae889ac; AMCVS_3C155B5B54E781000A4C98A2%40AdobeOrg=1; LPVID=k5YWYyODEwNjM2YmE2NGFj; _ga=GA1.3.170030211.1583284793; _gid=GA1.3.1461684607.1583284793; s_sess=%20p17%3Dnohome%3B%20advancednightrepair%3Dnoadvancednightrepair%3B%20bronzegoddess%3Dnobronzegoddess%3B%20cleardifference%3Dnocleardifference%3B%20purecolorenvy%3Dnopurecolorenvy%3B; _mibhv=anon-1583284781586-8513895088_5133; _micpn=esp:-1::1583284793591; _cs_c=1; b_s_id=52ea4832-d44a-4f2d-89db-dd1537d0bd62; _fbp=fb.1.1583284794724.1568309335; b_pg_v=3%2F3%2F2020%2C%205%3A19%3A54%20PM; _b_ccc_id=bf4ae01c-7806-4ad8-9da2-8c7398ae7bc3; __sonar=18408186511761339234; s_cc=true; _sctr=1|1583222400000; _gcl_au=1.1.1691206973.1583284808; _scid=3eba6582-ae38-4f7b-9119-0a1eb2427bd0; extole_access_token=D1T3CSIRI2HFUBDKQHHCEC8U1C; bm_sz=28F321EA93FBD16DCC78C49DA2D0560C~YAAQHM4zuI4BYl9wAQAA2pN/pgc6NgH6B9R3aULfUAlhdF/mSrpwqpeEj5qsWpS9UmScjnsvEjq4t7Cc/6h5UZz/l7J2BdhIECAXuNpC7nYp60QxoGguFdwl1OAbYVg7BnWQsY2U3FG+vY+3WcdJx1dljsh8x619W5JjkR4NrJdz+sG7ZETS/qZojE+QM6LYHUJuPXTk; ak_bmsc=E2304D5486A6206C0A7C344801BCBEC3173FFBC5A54400008C0A605E35E21D33~plFhNEAFW/nmkyUoOoppVZ7JGRQyGfQGspzQekoyyzUsSZaaFCiBuN5B3J+PLnP2eapdvL6J+OlVGLIzMIG45+01mpoELf0rF3jHFmKvKbXpEM0LYkGfLoYbYEITph47/usSFwWDlFGI19NLOV4/uQgxnDlnQEgx11ZVbLUZz55uyDTF2d0McRLYf1C5l23FfHU8dLcJf/+yDfujUVy2zyuc0vDUyuTghmwZj1XEpx2U4=; FE_USER_CART=available%3A%26csr_logged_in%3A0%26current_available%3A%26first_name%3A%26full_name%3A%26is_loyalty_member%3A0%26is_pro%3A0%26is_rewards_eligible%3A0%26item_count%3A%26loyalty_level%3A0%26loyalty_level_name%3A%26next_level%3A1%26next_level_name%3ALover%26pc_email_optin%3A0%26points%3A%26points_to_next_level%3A0%26region_id%3A%26signed_in%3A0; AKA_A2=A; AMCV_3C155B5B54E781000A4C98A2%40AdobeOrg=1406116232%7CMCIDTS%7C18326%7CMCMID%7C39372445773982995283573505286345339253%7CMCAAMLH-1583957287%7C9%7CMCAAMB-1583957287%7CRKhpRz8krg2tLO6pguXWp5olkAcUniQYPHaMWWgdJ3xzPWQmdj0y%7CMCOPTOUT-1583359687s%7CNONE%7CMCAID%7CNONE%7CvVersion%7C2.5.0; LPSID-48719195=gxK5R5GdSOyT15zSdV34tA; adobeRef=https://www.google.com/; OptanonConsent=isIABGlobal=false&datestamp=Wed+Mar+04+2020+12%3A09%3A07+GMT-0800+(Pacific+Standard+Time)&version=5.5.0&landingPath=NotLandingPage&groups=1%3A1%2C2%3A1%2C3%3A1%2C4%3A1%2C0_212330%3A1%2C0_212334%3A1%2C0_228206%3A1%2C0_212355%3A1%2C0_212322%3A1%2C0_217607%3A1%2C0_212326%3A1%2C0_212347%3A1%2C0_212351%3A1%2C0_212339%3A1%2C0_212343%3A1%2C0_212333%3A1%2C0_212337%3A1%2C0_212325%3A1%2C0_212354%3A1%2C0_228209%3A1%2C0_212329%3A1%2C0_229489%3A1%2C0_217606%3A1%2C0_228205%3A1%2C0_212346%3A1%2C0_212321%3A1%2C0_228210%3A1%2C0_212350%3A1%2C0_212338%3A1%2C0_212342%3A1%2C0_212332%3A1%2C0_212336%3A1%2C0_212357%3A1%2C0_212324%3A1%2C0_228208%3A1%2C0_212328%3A1%2C0_228204%3A1%2C0_212349%3A1%2C0_212353%3A1%2C0_212320%3A1%2C0_212341%3A1%2C0_212345%3A1%2C0_212331%3A1%2C0_212356%3A1%2C0_228207%3A1%2C0_212323%3A1%2C0_228203%3A1%2C0_212327%3A1%2C0_217608%3A1%2C0_212348%3A1%2C0_212352%3A1%2C0_212340%3A1%2C0_212344%3A1%2C8%3A1&AwaitingReconsent=false; _gat_tealium_0=1; utag_main=v_id:0170a32079d90015b413a4ee2f2003072001d06a0086e$_sn:2$_ss:0$_st:1583354353804$vapi_domain:maccosmetics.com$ses_id:1583352468359%3Bexp-session$_pn:4%3Bexp-session; _cs_id=02010e5a-02bb-a397-b79b-dbacfe8efd94.1583284794.2.1583352554.1583352487.1.1617448794305.Lax.0; _cs_s=3.1; RT="sl=3&ss=1583352459260&tt=28835&obo=0&bcn=%2F%2F173e2529.akstat.io%2F&sh=1583352553397%3D3%3A0%3A28835%2C1583352547612%3D2%3A0%3A16716%2C1583352486324%3D1%3A0%3A9496&dm=maccosmetics.com&si=83018272-91d4-43f4-99b8-f5c1bde7d9c5&ld=1583352553398&r=https%3A%2F%2Fwww.maccosmetics.com%2Fchoose-location&ul=1583352554456&hd=1583352554674"; csrftoken=4f7b25e9f27fc52b7e02c2e5d6edba336e9ee42a%2C1fdacf2602e3869fa3c3d518f4574b94752e6d37%2C1583352555; _abck=59087718B98982A837013F8F92205E98~0~YAAQxfs/F6VK5J9wAQAAM6oqpwN0qp28gf7uDBZEpRK6RSPPPo+l5KN2DzJoKy/iqoyGuQaPehqAdp9vc/FbP7HRMki8OcdNT8yTOLXyrXL01zWY6aKdOUJrPdFTAOlar5XZAA1g9IfkE+6KRiBuIiyI1+P/Ug//Ctf07FFF4L426fni2wLpFKERZV6y2us38622Z0CdxcNqtkZwvjGuujXc3dBWRmtbatjnXR3Fyv9QDnUFPDumU7niMDjJA4vTF0MdXKruSXKVFtgbTA5chkJ9qjwLAdjyQ8GrTseZenlE2XIUa9alXma5XGj9Aj7FqCYmh+avZC2RINhFUg==~-1~-1~-1; bm_sv=C3CD8848D8D94E3DB827215192333F1B~6LSAiXGTHTQsZcHR+sc6Q5LM94gOvRycNn/pOBkWeIHYVH6cgC8Pbpz8ovRj/4Hl3J1bFwgk+2Hv4NeikR0SV4jK172c7d/ayjJYH//ByMMQkjXK9vHENWwTBL7SHR/DQ3s8twBxzg86nSk2ND/Ai0xA7deOJLK+4GJf5uZQ8+Y=; akavpau_vp_US_www_maccosmetics_com=1583352860~id=c2741da260f715d07c7acb90bd235682'
           }

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def fetch_data():
    locs = []
    url = 'https://www.maccosmetics.com/rpc/jsonrpc.tmpl?dbgmethod=locator.doorsandevents'
    payload = {'JSONRPC': '[{"method":"locator.doorsandevents","id":3,"params":[{"fields":"DOOR_ID, DOORNAME, EVENT_NAME, SUB_HEADING, EVENT_START_DATE, EVENT_END_DATE, EVENT_IMAGE, EVENT_FEATURES, EVENT_TIMES, SERVICES, STORE_HOURS, ADDRESS, ADDRESS2, STATE_OR_PROVINCE, CITY, REGION, COUNTRY, ZIP_OR_POSTAL, PHONE1, PHONE2, STORE_TYPE, LONGITUDE, LATITUDE, COMMENTS","country":"United States","latitude":44.9951298,"longitude":-93.4352207,"uom":"mile","radius":15000,"region_id":"0,47,27"}]}]'
               }
    r = session.post(url, headers=headers, data=payload)
    for line in r.iter_lines():
        if '"DOOR_ID":' in line:
            items = line.split('"DOOR_ID":')
            for item in items:
                if '"STORE_TYPE":"' in item:
                    loc = '<MISSING>'
                    typ = item.split('"STORE_TYPE":"')[1].split('"')[0]
                    store = item.split(',')[0]
                    website = 'maccosmetics.com'
                    hours = ''
                    city = item.split('"CITY":"')[1].split('"')[0]
                    country = item.split('"COUNTRY":"')[1].split('"')[0]
                    if 'United States' in country:
                        country = 'US'
                    if 'Canada' in country:
                        country = 'CA'
                    name = item.split('"DOORNAME":"')[1].split('"')[0] + ' ' + item.split('SUB_HEADING":"')[1].split('"')[0]
                    name = name.strip()
                    phone = item.split('"PHONE1":"')[1].split('"')[0]
                    lat = item.split('"LATITUDE":"')[1].split('"')[0]
                    lng = item.split('"LONGITUDE":"')[1].split('"')[0]
                    add = item.split('"ADDRESS":"')[1].split('"')[0] + ' ' + item.split('"ADDRESS2":"')[1].split('"')[0]
                    add = add.strip()
                    zc = item.split('"ZIP_OR_POSTAL":"')[1].split('"')[0]
                    state = item.split('"STATE_OR_PROVINCE":"')[1].split('"')[0]
                    if 'STORE_HOURS":""' in item:
                        hours = ''
                    else:
                        days = item.split('"STORE_HOURS":[')[1].split(']')[0].split('"hours":"')
                        for day in days:
                            if '"day":"' in day:
                                dname = day.split('"day":"')[1].split('"')[0]
                                hrs = dname + ': ' + day.split('"')[0]
                                if hours == '':
                                    hours = hrs
                                else:
                                    hours = hours + '; ' + hrs
                    if hours == '':
                        hours = '<MISSING>'
                    if typ == '':
                        typ = 'Dept Store'
                    if phone == '':
                        phone = '<MISSING>'
                    if state == '' or state == '.':
                        state = '<MISSING>'
                    if zc == '':
                        zc = '<MISSING>'
                    if country == 'US':
                        yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
