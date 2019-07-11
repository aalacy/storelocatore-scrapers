const Apify = require('apify');
const axios = require('axios');
const jsdom = require("jsdom");
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
      dom = getDom(html);
    }
  })
  await crawler.run();
});

async function pageList(){
  return await axios({
    method: "",
    url: ""
  }).then((resp) => {
    dom = getDom(resp.data);
    links = [];
    for (let l of dom.querySelectorAll('')){
        links.push({url: '' + l.getAttribute('href')})
    }
  })
}

function getDom(markup){
  dom = new JSDOM(markup);
  return dom.window.document;
}

function getRecord(domain = '<MISSING>'){
  return {
    locator_domain: domain,
    location_name: '<MISSING>',
    street_address: '<MISSING>',
    city: '<MISSING>',
    state: '<MISSING>',
    zip: '<MISSING',
    country_code: '<MISSING>',
    store_number: '<MISSING>',
    phone: '<MISSING>',
    location_type: '<MISSING>',
    latitude: '<MISSING>',
    longitude: '<MISSING>',
    hours_of_operation: '<MISSING>',
  };    
}
