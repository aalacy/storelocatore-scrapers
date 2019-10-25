const request=require('request');
const Apify = require('apify');
const esriUtils = require('@esri/arcgis-to-geojson-utils');
const epsg = require('epsg');
const reproject = require('reproject');
const wicket = require('wicket');
const polygonCenter = require('geojson-polygon-center')

function esriJsonEpsg3857ToGeojsonEpsg4326(esriJson) {
	const geoJson = esriUtils.arcgisToGeoJSON(esriJson);
	return reproject.reproject(geoJson, epsg['EPSG:3857'], epsg['EPSG:4326']);
}

function geoJsonToCentroid(geoJson) {
	return polygonCenter(geoJson).coordinates;
}

function geoJsonToWkt(geoJson) {
	const wkt = new wicket.Wkt();
	const parsed = wkt.fromObject(geoJson);
	return parsed.write();
}

var items=[]
var stop=false
var cnt=1
var req=1
let errors = 0;

async function scrape(){
	return new Promise(async (resolve,reject) => {
		setInterval(()=> {
			for (i=0;i<500;i++) {
				if (req<500) {
					req=req+1;
					request(`https://server3.tplgis.org/arcgis3/rest/services/ParkServe/ParkServe_Parks/MapServer/0/${cnt}?f=pjson`,(err,res)=>{
						try {
							var data=JSON.parse(res.body)
							if (data.hasOwnProperty("error")) {
								stop=true
								clearInterval(this)
								resolve(items)
							} else {
								const esriJson = data['feature']['geometry'];
								const geoJson = esriJsonEpsg3857ToGeojsonEpsg4326(esriJson);
								const centroid = geoJsonToCentroid(geoJson);
								const polygonWkt = geoJsonToWkt(geoJson);
								const item = {
									locator_domain: "https://www.tpl.org",
									location_name:data["feature"]["attributes"]["Park_Name"]?data["feature"]["attributes"]["Park_Name"]:"<MISSING>",
									street_address: data["feature"]["attributes"]["Park_Address_1"]?data["feature"]["attributes"]["Park_Address_1"]:"<MISSING>",
									city:data["feature"]["attributes"]["Park_UrbanArea"]?data["feature"]["attributes"]["Park_UrbanArea"]: "<MISSING>",
									state:data["feature"]["attributes"]["Park_UrbanArea"]?data["feature"]["attributes"]["Park_UrbanArea"]:"<MISSING>",
									zip:"<MISSING>",
									country_code:"US",
									store_number:data["feature"]["attributes"]["ParkID"]?data["feature"]["attributes"]["ParkID"]:"<MISSING>",
									phone:"<MISSING>",
									location_type: "<MISSING>",
									latitude: centroid[1],
									longitude: centroid[0],
									hours_of_operation:"<MISSING>",
									page_url:`https://server3.tplgis.org/arcgis3/rest/services/ParkServe/ParkServe_Parks/MapServer/0/${cnt}?f=pjson`,
									wkt:polygonWkt
								}
								items.push(item);
								req=req-1
							}
						} catch(exce) {
							console.log(res.body);
							console.log(exce);
							errors++;
							console.log(`error count: ${errors}`);
						}
					})
					cnt=cnt+1;
				}
			}
		},5000)
	});
}

Apify.main(async () => {
	const data = await scrape();
	await Apify.pushData(data);
});
