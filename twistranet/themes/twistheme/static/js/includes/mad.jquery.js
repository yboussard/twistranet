/*---------------------------------------------------------------- 
  Copyright: 
  Copyright (C) 2009 danielfajardo web
  
  License:
  GPL Software 
  
  Author: 
  danielfajardo - http: //wwww.danielfajardo.com
---------------------------------------------------------------- */

jq(document).ready(function(){

    
    // Forms tab switching
    jq("fieldset.fieldset-inline-form legend a").click(function(event){
        event.preventDefault();
        event.stopPropagation();
        jq(this).parents("fieldset").hide();
        jq(jq(this).attr('href')).show();
        return false;
    });
    


  // Superfish mainmenu
  //
  jq("#mainmenu ul.sf-menu").superfish({
    animation: {width:'show'},
    speed: 2,   // speed for submenu apparition
    delay: 400, // the delay in milliseconds that the mouse can remain outside a submenu without closing 
    minWidth: 10,
    maxWidth: 20,
    extraWidth: 0
  });
  if( BrowserDetect.browser=="Explorer" && BrowserDetect.version<9 ) {
    jq("#mainmenu").mouseenter(
      function(){
        jq("#breadcrumb").fadeOut();
      }
    ).mouseleave(
      function(){
        jq("#breadcrumb").fadeIn(1000);
      }
    );
  }


  // Links effect
  //
  /*
  if( BrowserDetect.browser!="Explorer" ) {
    jq("a").hover(
      function(){
        jq(this).parent().addClass("selected");
        jq(this).animate({opacity: 0.5},200);
        jq(this).animate({opacity: 1},100);
      },
      function(){
        jq(this).parent().removeClass("selected");
        jq(this).animate({opacity: 1},100);
      }
    );
  }*/

  // External Links
  //
  jq("ul.links li a").append(" <img src='/images/icons/external.png' border ='0' />");
  jq("a.external").append(" <img src='/images/icons/external.png' border ='0' />");

  // Go To Top
  //
  /*
  jq("span#gototop a").click( function() {
    jq.scrollTo(jq("body"), 1000);
    return false;
  });
  */
});
