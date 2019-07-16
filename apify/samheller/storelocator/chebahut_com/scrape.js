const Apify = require('apify');
const axios = require('axios');
const jsdom = require('jsdom');
const { JSDOM } = jsdom;

Apify.main(async () => {
  const links = await pageList();
  return true;
  const requestList = new Apify.RequestList({sources: links});
  await requestList.initialize();
  
  const crawler = new Apify.BasicCrawler({
    requestList,
    handleRequestFunction: async ({request}) => {
      const html = await requestPromise(request.url);
      dom = getDom(html);
    }
  })
  await crawler.run()
});

async function pageList(){
    return await axios({
      method: 'GET',
      url: 'https://chebahut.com/locations'
    }).then((resp) => {
      // console.log(resp);
      dom = new JSDOM(resp.data);
      document = dom.window.document;
      links = document.querySelector('.wi-franchise-list').querySelectorAll('a');
      for (let l of links){
        console.log(l.textContent, l.getAttribute('href'));
      }
    })
}
