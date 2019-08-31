const Apify = require('apify');
const axios = require('axios');
const jsdom = require('jsdom');
const { JSDOM } = jsdom;
const requestPromise = require('request-promise');

Apify.main(async () => {
  const links = await pageList();
  const requestList = new Apify.RequestList({sources: links});
  await requestList.initialize();

  const crawler = new Apify.BasicCrawler({
    requestList,
    handleRequestFunction: async ({request}) => {
      const html = await requestPromise(request.url);
      document = new JSDOM(html).window.document;
      entry = document.querySelector('.column-content');
      store = request.url
        .split("/")
        .filter((e) => {return e !== ''})
        .pop()
      latlon = latLonFromLink(entry.querySelector('a').getAttribute('href'));
      address = entry.querySelector('p:nth-child(2)').textContent.split("\n");
      address = handleEdgeCases(address, store);
      area = parseArea(address[1]);
      hours = entry.querySelector('p:nth-child(5)').textContent;


      Apify.pushData([{
        locator_domain: 'corelifeeatery.com',
        location_name: store,
        street_address: address[0],
        city: area.city,
        state: area.state,
        zip: fixZip(area.zip, store),
        country_code: 'US',
        store_number: '<MISSING>',
        phone: address.pop().replace('Phone:', '').trim(),
        location_type: '<MISSING>',
        latitude: latlon.lat,
        longitude: latlon.lon,
        hours_of_operation: hours,
      }])
    }
  })
  await crawler.run()
});

async function pageList(){
  return await axios({
    method: "GET",
    url: "https://www.corelifeeatery.com/locations/"
  }).then((resp) => {
    document = new JSDOM(resp.data).window.document;    
    links = [];
    for (let d of document.querySelectorAll('.grid-item')){
      links.push({url: d.querySelector('a').getAttribute('href')});
    }
    return links;
  });
}

function parseArea(area){
  parsed = {city: '', state: '', zip: ''};
  area = area.split(',');
  parsed.city = area[0];
  area = area[1].split(' ');
  parsed.zip = area.pop();
  parsed.state = area.join(' ').trim();
  return parsed;
}

function latLonFromLink(href){
  [lat, lon] = href
    .replace(/^.*\@/, '') //strip everything up to latlong string
    .replace(/\/.*/, '') // strip everything after latlong string
    .split(','); //split on comma

  //Handle link extraction failures
  if (lat == 'https' || lon == undefined){return {lat: '<MISSING>', lon: '<MISSING>'}}
  return {lat: lat, lon: lon}
}

function sanitize(textRow){
  sane = [];
  for (s of textRow.split("\n")){
    s = s.trim();
    if (s !== ''){sane.push(s);}
  }
  return sane;
}

function handleEdgeCases(address){
  //Edge case with Unit prefix to address
  if (address[1].startsWith('Unit')){
    return [address[0] + " " + address[1], address[2], '', address[3]]
  }
  
  if (address.length == 3){
    return [address[0], address[1], '', address[2]]
  }
  
  //Edge case where address and location name are reversed
  if (address[1].match(/^[0-9]/) !== null){
    return [address[1], address[2], address[0], address[3]]
  }

  //Edge case with extra data in the address map
  if (address.length == 5){
    return [address[0], address[2], address[3], address[4]]
  }

  //Super sparse edgecase
  if (address.length == 2){
    return [address[0], '<MISSING>', address[1], '<MISSING>', '<MISSING>']
  }

  return address;
}


function fixZip(zip, store){
  //3 pages with weird parsing errors manually handling zipcodes
  switch (store){
    case 'webster-ny-2' : zip = 14580; break;
    case 'lancaster-pa-2' : zip = 17601; break;
    case 'syracuse-ny-2' : zip = 13212; break;
    default: break;
  }
  return Number(zip);
}
