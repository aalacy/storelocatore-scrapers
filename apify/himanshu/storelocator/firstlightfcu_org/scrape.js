const Apify = require('apify');
const request=require('request');
const cheerio=require('cheerio');
 
 var tmp_url ='https://www.firstlightfcu.org';
var url = 'https://www.firstlightfcu.org/branches';
async function scrape(){

  return new Promise(async (resolve,reject)=>{
 
request(url,(err,res,html)=>{

  if(!err && res.statusCode==200){
   
     const $  =cheerio.load(html);
        var items=[];
        var main = $('.content_area_container').find('.branches_listing').find('li');
        function mainhead(i)

        {
            if(main.length>i)

                {
          var link = tmp_url+$('.content_area_container').find('.branches_listing').find('li').eq(i).find('a').attr('href');

          request(link,(err,res,html)=>{

            if(!err && res.statusCode==200){
              const $  =cheerio.load(html);
              var location_name = $('.content_area_container').find('.h2').text();
              var address = $('#branch').find('.col-md-6:nth-child(3)').find('.address').text();
              var city_tmp = $('#branch').find('.col-md-6:nth-child(3)').find('.city_state_zip').text();
              var city_tmp1 = city_tmp.split(',');
              var city = city_tmp1[0];
              var state_tmp = city_tmp1[1].split(' ');
              var state = state_tmp[1];
              var zip = state_tmp[2];
              var city_tmp = $('#branch').find('.col-md-6:nth-child(3)').find('.city_state_zip').text();
              var hour = $('#branch').find('.col-md-6:nth-child(3)').find('.hours').text().replace(/\n/g, '');
              var phone = $('#branch').find('.col-md-6:nth-child(3)').find('.phone').text().replace('Phone:','').trim();
              var lat = $('script').html()
              console.log(lat)
              items.push({
                locator_domain : 'https://www.firstlightfcu.org',
                location_name : location_name,
                street_address : address,
                city:city,
                state:state,
                zip:zip,
                country_code: 'US',
                store_number:'<MISSING>',
                phone:phone,
                location_type:'<MISSING>',
                latitude:'<MISSING>',
                longitude :'<MISSING>',
                hours_of_operation:hour,
                page_url:'<MISSING>'
                
                });  
            
                mainhead(i+1);
             
            }

          });

         
        }
     

        else{
    
        resolve(items);
    
        }
 } 

mainhead(0);
        
             
        
         
            }
    });
  });
}

  
    
   
  
  Apify.main(async () => {
  
      
  
      const data = await scrape();
      
      await Apify.pushData(data);
    
    });