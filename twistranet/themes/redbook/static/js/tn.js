/*
 * TwistraNet Main  javascript methods
 */


// global vars

var defaultDialogMessage = '';
var curr_url = window.location.href;

// helpers

// set first and last class on subblocks
setFirstAndLast = function(block, sub, modulo) {
   jQuery(block).each(function() {
      if (typeof modulo=='undefined')  {
        jQuery(sub+':first', jQuery(this)).addClass('first');
        jQuery(sub+':last', jQuery(this)).addClass('last');
      }
      else {
        jQuery(sub, jQuery(this)).each(function(i) {
            if ((i+1)%modulo==0) jQuery(this).addClass('last');
            if ((i+1)%modulo==1) jQuery(this).addClass('first');
        })
      }
   })
}

// confirm boxes using jqueryui
initConfirmBox = function(elt){
    actionLabel = jQuery(elt).attr('title');
    actionLink = jQuery(elt).attr('href');
    dialogBox = jQuery('#tn-dialog');
    // the title of the box is kept using link title + ' ?'
    jQuery('#ui-dialog-title-tn-dialog').text(actionLabel+ ' ?');
    // the legend of the box is kept inside a invisible block with class 
    // confirm-message 
    // inside the link
    actionLegend = jQuery('.confirm-message', elt);
    if (actionLegend.length) jQuery('#tn-dialog-message').text(actionLegend.text());
    // translations for buttons are kept in the current page 
    // (could also be done using django javascript translations tools >> TODO)
    var cancelLabel = jQuery('#tn-dialog-button-cancel', dialogBox).text();
    var okLabel = jQuery('#tn-dialog-button-ok', dialogBox).text();
    var tnbuttons = {};  
    tnbuttons[okLabel] = function() {
    // ok action for now just redirect to the link
      window.location.replace(actionLink);
    };
    tnbuttons[cancelLabel] = function() {
      jQuery( this ).dialog( "close" );
    }; 
    dialogBox.dialog({   
      buttons: tnbuttons 
    });
    dialogBox.dialog('open');
}


escapeHTML = function(s) {
    return s.split('&').join('&amp;').split('<').join('&lt;').split('"').join('&quot;');
}
// absolutize url : the browser make the job
absolutizeURL = function(url) {
    var el= document.createElement('div');
    el.innerHTML= '<a href="'+escapeHTML(url)+'">x</a>';
    return el.firstChild.href;
}

// set selected class on a menu
// depending on current url
setSelectedTopic = function(menu) {   
    selected = false;
    jQuery('>ul>li', menu).each (function(i){
      topic = jQuery(this);
      jQuery('a', topic).each(function(){
          href = jQuery(this).attr('href'); 
          if (href && typeof href!='undefined' && ! selected) {
             if (absolutizeURL(href) == curr_url) { 
               selected = true;
               topic.addClass('selected');
               return false; }
          } 
      });
    });
    if (!selected) jQuery('>ul>li:first', menu).addClass('selected');
}

liveSearchDisplayResult = function(link, thumblink, type, title, description) {
    template= ' \
<div class="ls-result"> \
   <a href="' + link + '" \
      title="' + title + '" \
      class="image-block image-block-50-50 image-block-alone"> \
       <img src="' + thumblink + '" \
            alt="'+ title + '" /> \
   </a> \
  <p><span class="ls-result-title">' + title + '</span><span class="ls-result-type">' + type + '</span></p> \
  <p class="ls-result-description">' + description + '</p> \
  <div class="clear"></div> \
</div> \
';    
return template.replace('<span class="ls-result-title"></span>', '');
}


// Live search ajax
liveSearch = function(searchTerm) {
    livesearchurl = '/search/json' ;
    var liveResults = jQuery('#search-live-results');
    var nores_text = jQuery('#no-results-text').val();
    if (searchTerm) {
      jQuery.get(livesearchurl+'?q='+searchTerm, 
          // get json data (eval)
          function(data) {
              results = eval(data);
              liveResults.hide();
              liveResults.html('');
              if (results.length) {
                  jQuery(results).each(function(){
                      html_result = liveSearchDisplayResult(this.link, this.thumb, this.type, this.title, this.description);
                      liveResults.append(html_result);
                      
                  });   
                  jQuery(document).ready(function() {
                      jQuery('.ls-result').click( function(){
                          location.replace( jQuery('a', this).attr('href'));
                      })
                  });
              }
              else {
                  liveResults.append('<p>' + nores_text + '</p>');
              }            
              liveResults.show(); 
          }
          );      
    }  
    else {
        liveResults.hide();
        liveResults.html('');
    } 
}

// main class
var twistranet = {
    __init__: function(e) {
        /* finalize styles */
        twistranet.finalizestyles();
        twistranet.showContentActions();
        twistranet.initconfirmdialogs();
        twistranet.initformserrors();
        twistranet.formsautofocus();
        twistranet.setEmptyCols(); 
        twistranet.enableLiveSearch();
    },
    enableLiveSearch: function(e) {
        var defaultSearchText = jQuery("#default-search-text").val();
        searchGadget = jQuery("#search-text");
        var liveResults = jQuery('#search-live-results');
        liveResults.bind('mouseenter', function(){
            jQuery(this).show();
        });
        liveResults.bind('mouseleave', function(){
            jQuery(this).hide('slow');
        });        
        searchGadget.bind('blur', function(){
            liveResults.trigger('mouseleave');
        });       
        searchGadget.bind('mouseenter',function(){
            if (liveResults.html()!='') liveResults.trigger('mouseenter'); 
        }); 
        searchGadget.livesearch({
    				searchCallback: liveSearch,
    				innerText: defaultSearchText,
    				queryDelay: 200,
    				minimumSearchLength: 2
    			});
    },
    finalizestyles: function(e) {
        /* set some first and last classes  */
        jQuery([['.content-actions', 'li'],['#mainmenu > ul > li', '> ul> li']]).each(function(){
           setFirstAndLast(this[0], this[1]);
        } );         
        // set how many thumbs by line in different blocks
        jQuery([['.tn-box', '.thumbnail-50-bottom']]).each(function(){
           setFirstAndLast(this[0], this[1], 3);
        } );
        jQuery([['.tn-box', '.thumbnail-32-none']]).each(function(){
           setFirstAndLast(this[0], this[1], 5);
        } );   
        /* set selected topic in menus*/    
        setSelectedTopic(jQuery('#mainmenu'));
        /* set classes for some inline fields > todo : place it in template */
        jQuery('ul.inline-form #id_permissions, ul.inline-form #id_language, ul.inline-form :submit').each(function(){
          jQuery(this).parents('li').addClass('inlinefield');
        });
    },
    setEmptyCols : function(e) {
        if (! $('#contextbar .tn-box-container:first').children().size() ) $('body').addClass('noleftcol');
    },
    showContentActions: function(e){
        /* show content actions on post mouseover */
        jQuery('.post').bind('mouseenter', function(){
          jQuery(this).addClass('activepost');
        });
        jQuery('.post').bind('mouseleave', function(){
          jQuery(this).removeClass('activepost');
        });                                          
    },
    initconfirmdialogs: function(e){
        if (jQuery('#tn-dialog-message').length) {
            defaultDialogMessage = jQuery('#tn-dialog-message').text();
            jQuery("#tn-dialog").dialog({  
              resizable: false,
              draggable: false,
              autoOpen: false,
              height: 120,
              width: 410,
              modal: true,
              close: function(ev, ui) { 
                jQuery('#tn-dialog-message').text(defaultDialogMessage);
                jQuery(this).hide(); 
              },
              focus: function(event, ui) { 
                ;
              }
            });
            links = 'a.confirmbefore';
            jQuery(links).click(function(e){
               e.preventDefault();
               initConfirmBox(this);
            } );       
        }
    },
    initformserrors: function(e) {
      jQuery('.fieldWrapper .errorlist').each(function(){
          jQuery(jQuery(this).parent()).addClass('fieldWrapperWithError');
      })
    },
    formsautofocus: function(e) {
     if (jQuery("form .fieldWrapperWithError :input:first").focus().length) return;
         jQuery("form.enableAutoFocus :input:visible:first").focus();
    }  
}

jQuery(document).ready(twistranet.__init__)