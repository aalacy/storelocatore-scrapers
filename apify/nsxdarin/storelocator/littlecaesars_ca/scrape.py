import csv
import urllib.request, urllib.error, urllib.parse
from sgrequests import SgRequests
import json

session = SgRequests()
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36',
           'authority': 'api.cloud.littlecaesars.com',
           'method': 'GET',
           'referer': 'https://littlecaesars.ca/en-ca/stores/search/RichmondHill',
           'accept-language': 'en-ca',
           'cache-control': 'no-cache, max-age=0',
           'origin': 'https://littlecaesars.ca'
           }

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

canada = ['Toronto,ON','Montreal,PQ','Calgary,AB','Ottawa,ON','Edmonton,AB','Mississauga,ON','Winnipeg,MB','Vancouver,BC','Brampton,ON','Hamilton,ON','Quebec,PQ','Surrey,BC','Laval,PQ','Halifax,NS','London,ON','Markham,ON','Vaughan,ON','Gatineau,PQ','Saskatoon,SK','Longueuil,PQ','Kitchener,ON','Burnaby,BC','Windsor,ON','Regina,SK','Richmond,BC','Richmond Hill,ON','Oakville,ON','Burlington,ON','Greater Sudbury,ON','Sherbrooke,PQ','Oshawa,ON','Saguenay,PQ','Levis,PQ','Barrie,ON','Abbotsford,BC','Coquitlam,BC','Trois Rivieres,PQ','St Catharines,ON','Guelph,ON','Cambridge,ON','Whitby,ON','Kelowna,BC','Kingston,ON','Ajax,ON','Langley,BC','Saanich,BC','Terrebonne,PQ','Milton,ON','St Johns,NF','Thunder Bay,ON','Waterloo,ON','Delta,BC','Chatham Kent,ON','Red Deer,AB','Strathcona County,AB','Brantford,ON','St Jean sur Richelieu,PQ','Cape Breton,NS','Lethbridge,AB','Clarington,ON','Pickering,ON','Nanaimo,BC','Kamloops,BC','Niagara Falls,ON','North Vancouver,BC','Victoria,BC','Brossard,PQ','Repentigny,PQ','Newmarket,ON','Chilliwack,BC','Maple Ridge,BC','Peterborough,ON','Kawartha Lakes,ON','Drummondville,PQ','St Jerome,PQ','Prince George,BC','Sault Ste Marie,ON','Moncton,NB','Sarnia,ON','Wood Buffalo,AB','New Westminster,BC','St John,NB','Caledon,ON','Granby,PQ','St Albert,AB','Norfolk County,ON','Medicine Hat,AB','Grande Prairie,AB','Airdrie,AB','Halton Hills,ON','Port Coquitlam,BC','Fredericton,NB','Blainville,PQ','St Hyacinthe,PQ','Aurora,ON','North Vancouver,BC','Welland,ON','North Bay,ON','Belleville,ON','Mirabel,PQ','Shawinigan,PQ','Dollard Des Ormeaux,PQ','Brandon,MB','Rimouski,PQ','Chateauguay,PQ','Mascouche,PQ','Cornwall,ON','Victoriaville,PQ','Whitchurch Stouffville,ON','Haldimand County,ON','Georgina,ON','St Eustache,PQ','Quinte West,ON','West Vancouver,BC','Rouyn Noranda,PQ','Timmins,ON','Boucherville,PQ','Woodstock,ON','Salaberry de Valleyfield,PQ','Vernon,BC','St Thomas,ON','Mission,BC','Vaudreuil Dorion,PQ','Brant,ON','Lakeshore,ON','Innisfil,ON','Charlottetown,PE','Prince Albert,SK','Langford,BC','Bradford West Gwillimbury,ON','Sorel Tracy,PQ','New Tecumseth,ON','Spruce Grove,AB','Moose Jaw,SK','Penticton,BC','Port Moody,BC','West Kelowna,BC','Campbell River,BC','St Georges,PQ','Val dOr,PQ','Cote St Luc,PQ','Stratford,ON','Pointe Claire,PQ','Orillia,ON','Alma,PQ','Fort Erie,ON','LaSalle,ON','Leduc,AB','Ste Julie,PQ','North Cowichan,BC','Chambly,PQ','Orangeville,ON','Okotoks,AB','Leamington,ON','St Constant,PQ','Grimsby,ON','Boisbriand,PQ','Magog,PQ','St Bruno de Montarville,PQ','Conception Bay South,NF','Ste Therese,PQ','Langley,BC','Cochrane,AB','Courtenay,BC','Thetford Mines,PQ','Sept Iles,PQ','Dieppe,NB','Whitehorse,YT','Prince Edward County,ON','Clarence Rockland,ON','Fort Saskatchewan,AB','La Prairie,PQ','East Gwillimbury,ON','Lincoln,ON','Tecumseh,ON','Mount Pearl,NF','Beloeil,PQ','LAssomption,PQ','Amherstburg,ON','St Lambert,PQ','Collingwood,ON','Kingsville,ON','Baie Comeau,PQ','Paradise,NF','Brockville,ON','Owen Sound,ON','Varennes,PQ','Candiac,PQ','Strathroy Caradoc,ON','St Lin Laurentides,PQ','Wasaga Beach,ON','Joliette,PQ','Essex,ON','Westmount,PQ','Mont Royal,PQ','Fort St John,BC','Kirkland,PQ','Cranbrook,BC','White Rock,BC','St Lazare,PQ','Chestermere,AB','Huntsville,ON','Corner Brook,NF','Riverview,NB','Lloydminster (Part),AB','Yellowknife,NT','Squamish,BC','Riviere du Loup,PQ','Cobourg,ON','Beaconsfield,PQ','Dorval,PQ','St Augustin de Desmaures,PQ','Thorold,ON','Camrose,AB','Mont St Hilaire,PQ','Pitt Meadows,BC','Port Colborne,ON','Quispamsis,NB','Oak Bay,BC','Ste Marthe sur le Lac,PQ','Salmon Arm,BC','Port Alberni,BC','Esquimalt,BC','Miramichi,NB','Niagara on the Lake,ON','Deux Montagnes,PQ','Beaumont,AB','Middlesex Centre,ON','Stony Plain,AB','Petawawa,ON','Pelham,ON','St Basile le Grand,PQ','Ste Catherine,PQ','Midland,ON','Colwood,BC','Central Saanich,BC','Port Hope,ON','Swift Current,SK','Edmundston,NB','LAncienne Lorette,PQ','North Grenville,ON','Yorkton,SK','Tracadie,NB','St Colomban,PQ','Bracebridge,ON','Greater Napanee,ON','Tillsonburg,ON','Steinbach,MB','Ste Sophie,PQ','Kenora,ON']


def fetch_data():
    ids = []
    for place in canada:
        city = place.split(',')[0]
        prov = place.split(',')[1]
        url = 'https://api.cloud.littlecaesars.com/bff/api/stores?city=' + city + '&province=' + prov
        website = 'littlecaesars.ca'
        print(('%s...' % city))
        r = session.get(url, headers=headers)
        for item in json.loads(r.content)['stores']:
            name = "Little Caesar's"
            city = item['address']['city']
            state = item['address']['state']
            country = 'CA'
            add = item['address']['street'] + ' ' + item['address']['street2']
            add = add.strip()
            zc = item['address']['zip']
            lat = item['latitude']
            lng = item['longitude']
            phone = item['phone']
            store = item['storeId']
            typ = item['storeType']
            purl = 'https://order.littlecaesars.com/en-us/stores/' + str(store)
            try:
                hours = item['storeOpenTime'] + '-' + item['storeCloseTime']
            except:
                hours = '<MISSING>'
            if store not in ids:
                ids.append(store)
                yield [website, purl, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
