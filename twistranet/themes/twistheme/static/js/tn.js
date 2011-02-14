/*
 * TwistraNet Main  javascript methods
 */


// global vars


var defaultDialogMessage = '';
var curr_url = window.location.href;
// live searchbox disparition effect
var ls_hide_effect_speed = 300;

// helpers

// set first and last class on subblocks
setFirstAndLast = function(block, sub, modulo) {
   jq(block).each(function() {
      if (typeof modulo=='undefined')  {
        jq(sub+':first', jq(this)).addClass('first');
        jq(sub+':last', jq(this)).addClass('last');
      }
      else {
        jq(sub, jq(this)).each(function(i) {
            if ((i+1)%modulo==0) jq(this).addClass('last');
            if ((i+1)%modulo==1) jq(this).addClass('first');
        })
      }
   })
}

// confirm boxes using jqueryui
initConfirmBox = function(elt){
    actionLabel = jq(elt).attr('title');
    actionLink = jq(elt).attr('href');
    dialogBox = jq('#tn-dialog');
    // the title of the box is kept using link title + ' ?'
    jq('#ui-dialog-title-tn-dialog').text(actionLabel+ ' ?');
    // the legend of the box is kept inside a invisible block with class 
    // confirm-message 
    // inside the link
    actionLegend = jq('.confirm-message', elt);
    if (actionLegend.length) jq('#tn-dialog-message').text(actionLegend.text());
    // translations for buttons are kept in the current page 
    // (could also be done using django javascript translations tools >> TODO)
    var cancelLabel = jq('#tn-dialog-button-cancel', dialogBox).text();
    var okLabel = jq('#tn-dialog-button-ok', dialogBox).text();
    var tnbuttons = {};  
    tnbuttons[okLabel] = function() {
      // ok action for now just redirect to the link
      window.location.replace(actionLink);
    };
    tnbuttons[cancelLabel] = function() {
      jq( this ).dialog( "close" );
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
    jq('>ul>li', menu).each (function(i){
      topic = jq(this);
      jq('a', topic).each(function(){
          href = jq(this).attr('href'); 
          if (href && typeof href!='undefined' && ! selected) {
             if (absolutizeURL(href) == curr_url) { 
               selected = true;
               topic.addClass('selected');
               return false; }
          } 
      });
    });
    if (!selected) jq('>ul>li:first', menu).addClass('selected');
}

liveSearchDisplayResult = function(link, thumblink, type, title, description) {
    template= ' \
<div class="ls-result"> \
   <a href="' + link + '" \
      title="' + title + '" \
      class="image-block image-block-tile image-block-alone"> \
       <img src="' + thumblink + '" \
            alt="'+ title + '" /> \
   </a> \
  <p><span class="ls-result-title">' + title + '</span><span class="ls-result-type"> ' + type + '</span></p> \
  <p class="ls-result-description">' + description + '</p> \
  <div class="clear"><!-- --></div> \
</div> \
';    
// remove empty fields
template = template.replace('<span class="ls-result-type"> </span>', '');
template = template.replace('<span class="ls-result-title"></span>', '');
template = template.replace('<p></p>', '');
return template;
}



// Live search ajax
liveSearch = function(searchTerm) {
    livesearchurl = home_url + 'search/json' ;
    var liveResults = jq('#search-live-results');
    var nores_text = jq('#no-results-text').val();
    if (searchTerm) {
      jq.get(livesearchurl+'?q='+searchTerm, 
          function(data) {
              jsondata = eval( "(" + data + ")" );
              results = jsondata.results;
              liveResults.hide();
              liveResults.html('');
              if (results.length) {        
                  jq(results).each(function(){
                      html_result = liveSearchDisplayResult(this.link, this.thumb, this.type, this.title, this.description);
                      liveResults.append(html_result);
                  });
                  if (jsondata.has_more_results) {
                      html_more_results = '<div class="ls-result ls-allresults-link">';
                      html_more_results += '<a href="' + jsondata.all_results_url + '" title="' +  jsondata.all_results_text + '">';
                      html_more_results += jsondata.all_results_text + '</a>';
                      html_more_results += '<div class="clear"></div></div>';
                      liveResults.append(html_more_results);
                  }
                  allResults = jq('>.ls-result', liveResults);
                  lenResults = allResults.length;
                  allResults.each( function(){
                      var resBlock = jq(this);
                      resBlock.click( function(e){
                          jq("#search-text").unbind('focusout');
                          liveResults.stop();
                          location = jq('a', this).attr('href');
                      });
                      jq('a', resBlock).click(function(e){
                          e.preventDefault();
                          e.stopPropagation();
                          resBlock.trigger('click');
                          return false;
                      });
                  });
                  var activeResult = jq('.ls-result:first', liveResults);
                  activeResult.addClass('ls-result-active');       
                  var i = 0;
                  // live search results keyboard behavior
                  jq("#search-text").keydown(function(e){       
                      if (e.keyCode == '13') {
                          e.preventDefault();
                          e.stopPropagation();
                          activeResult.trigger('click');
                          return false;
                      }                          
                      else {
                          changes = false;
                          if (e.keyCode == '38' && i>0) {
                              e.preventDefault();
                              i-=1;       
                              changes = true;
                          }
                          else if ( e.keyCode == '40' && i<lenResults-1 ) {
                              e.preventDefault();
                              i+=1;           
                              changes = true;               
                          }
                          if (changes) {          
                              activeResult.removeClass('ls-result-active');
                              activeResult = jq(allResults[i]);
                              activeResult.addClass('ls-result-active');
                          }
                      }
                  });
                  setFirstAndLast('#search-live-results','.ls-result');
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


/* fix grid styles depending on Cols Number 
   the number is given by className
   ng  : 'tngridcols-9x' = 9 columns
 */

gridStyle = function(grid) {
    className = grid.className;
    /* define cols */
    if ( className.split('tngridcols-').length ) {
        ncols = parseInt(className.split('tngridcols-')[1].split('x')[0]);
        if (ncols) {
            jq('.tnGridItem', grid).each(function(i) {
                if ((i+1)%ncols==1) jq(grid).append('<div class="tnGridRow"></div>');
                gridRow= jq('.tnGridRow:last', grid);
                gridRow.append(jq(this));
                
            })
        }
    }            
    // see if something is selected
    gridOnChange(grid);
    // IMPORTANT : the grid is always shown at the end 
    // to avoid bad moving effect      
    jq(grid).css('display', 'table');
}

/* When something has changed on grid
   called on load or when selecting
   a radio button to check/uncheck elements */
   
gridOnChange = function(grid) {
    jq('.tnGridItem', grid).each(function(){
        var item = jq(this);       
        var checkbox = jq('>input:checkbox, >input:radio', this);
        if (checkbox.length) {
            if (checkbox.is(':checked')) {
                jq(this).addClass('itemSelected');
            }
            else {
                jq(this).removeClass('itemSelected');    
            }
        }
    });
}

/* actions on grid selection
   eg : check/uncheck value before submit */

gridOnSelect = function(grid) {
    jq('.tnGridItem', grid).each(function() {
        var item = jq(this);       
        var checkbox = jq('>input:checkbox, >input:radio', this);
        var radio = jq('>input:radio', this);
        if (checkbox.length) {
            item.click(function(e) {
                if (checkbox.is(':checked')) {
                    jq(this).removeClass('itemSelected');
                    checkbox.removeAttr("checked");
                }
                else {
                    checkbox.attr('checked', 'checked');
                    jq(this).addClass('itemSelected');
                }
                // for radios buttons unselect other items
                if (radio.length) gridOnChange(grid);
            })
        }
        jq('a', item).click(function(e) {
            e.preventDefault();
            e.stopPropagation();
            item.trigger("click");
        })
    })
}


// TODO in future : remove cache: true
// and improve ajax request with data (type = image etc ... see ticket #1196,
// and uploaderid=toto for multiple uploaders in a same page )
loadQuickUpload = function(obj) {
    var uploadUrl = home_url + 'resource_quickupload/' ;
    var tnUploader = jq(obj);
    jq.ajax({
        type: "GET",
        url: uploadUrl,
        dataType: 'html', 
        contentType: 'text/html; charset=utf-8', 
        cache: true,
        data: '',
        success: function(content){
            tnUploader.html(content);
        }
    });
}

var FileBrowserDialogue = {
    init : function () {
        // Here goes your code for setting your custom things onLoad.
    },
    submit : function (URL,title) {
        //var URL = document.my_form.my_field.value;
        var win = tinyMCEPopup.getWindowArg("window");

        // insert information now
        win.document.getElementById(tinyMCEPopup.getWindowArg("input")).value = URL;

        // are we an image browser
        if (typeof(win.ImageDialog) != "undefined") {
            // we are, so update image dimensions and title...
            if (win.ImageDialog.getImageData)
                win.ImageDialog.getImageData();
                win.document.getElementById('title').value = title;
                win.document.getElementById('alt').value = title;
            // ... and preview if necessary
            if (win.ImageDialog.showPreviewImage)
                win.ImageDialog.showPreviewImage(URL);
        }
        else win.document.getElementById('linktitle').value = title;

        // close popup window
        tinyMCEPopup.close();
    }
}

// main class
var twistranet = {
    browser_width: 0,
    browser_height: 0,
    __init__: function(e) {
        /* finalize styles */
        twistranet.setBrowserProperties();
        twistranet.finalizestyles();
        twistranet.showContentActions();
        twistranet.showCommentsActions();
        twistranet.initconfirmdialogs();
        twistranet.initformserrors();
        twistranet.formsautofocus();
        twistranet.setEmptyCols(); 
        twistranet.enableLiveSearch();
        twistranet.prettyCombosLists(); 
        twistranet.tnGridActions();
        twistranet.formUndo(); 
        twistranet.formProtection();
        twistranet.formInputsHints();
        twistranet.loadUploaders();
        twistranet.initWysiwygBrowser();
    },
    setBrowserProperties : function(e) {
        if (! twistranet.browser_width){
            twistranet.browser_width = jq(window).width();
            twistranet.browser_height = jq(window).height();
        } 
    },
    prettyCombosLists: function(e) {
        // sexy combo list for permissions widget
        jq("select.permissions-widget").msDropDown();
        // remove the forced width (see also.dd .ddTitle in css) 
        jq(document).ready(function(){jq('.dd').css('width','auto')});
        // permission description after all
        jq(document).ready(twistranet.displayPermissionsDescriptions);
    },
    displayPermissionsDescriptions: function(e) {
        jq('.permissions-widget').each(function(){
            var pwidget = jq(jq(this).parent()).parent();
            var pdescriptions = jq('.hint', pwidget);
            jq('.ddChild a', pwidget ).each(function(i){
                jq(this).mouseenter(function(){jq(pdescriptions[i]).show()});
                jq(this).mouseleave(function(){jq(pdescriptions[i]).hide()});
            });
        })
    },
    enableLiveSearch: function(e) {
        var defaultSearchText = jq("#default-search-text").val();
        searchGadget = jq("#search-text");                
        var liveResults = jq('#search-live-results');
        searchGadget.bind('focusin',function(){
            if (liveResults.html()!='') liveResults.show();
        });
        searchGadget.bind('focusout',function(){
            liveResults.delay(50).hide(ls_hide_effect_speed);
        });  
        if (searchGadget.length) {
            searchGadget.livesearch({
                searchCallback: liveSearch,
                innerText: defaultSearchText,
                queryDelay: 200,
                minimumSearchLength: 2
                });
        }
    },
    finalizestyles: function(e) {
        /* set some first and last classes  */
        jq([['.content-actions', 'li'],['#mainmenu > ul > li', '> ul> li'],['#content','.post']]).each(function(){
           setFirstAndLast(this[0], this[1]);
        } );         
        // set how many thumbs by line in different blocks
        jq([['.tn-box', '.thumbnail-50-bottom']]).each(function(){
           setFirstAndLast(this[0], this[1], 3);
        } );
        jq([['.tn-box', '.thumbnail-32-none']]).each(function(){
           setFirstAndLast(this[0], this[1], 5);
        } );   
        /* set selected topic in menus*/    
        setSelectedTopic(jq('#mainmenu'));
        /* finalize grids style */
        jq('.tnGrid').each(function(){
            gridStyle(this);
        });
    },
    setEmptyCols : function(e) {
        if (! $('#globalbar .tn-box-container:first').children().size() &
            ! $('#contextbar .tn-box-container:first').children().size() ) {
            $('body').addClass('nocol');
        } else if (! $('#contextbar .tn-box-container:first').children().size() ) {
            $('body').addClass('noleftcol');
        }
    },
    showContentActions: function(e){
        /* show content actions on post mouseover */
        jq('.post').bind('mouseenter', function(){
          jq(this).addClass('activepost');
        });
        jq('.post').bind('mouseleave', function(){
          jq(this).removeClass('activepost');
        });                                          
    },
    showCommentsActions: function(e){
        /* show content actions on post mouseover */
        jq('.comment').bind('mouseenter', function(){
          jq(this).addClass('activecomment');
          jq(this).parents('.post').removeClass('activepost');
        });
        jq('.comment').bind('mouseleave', function(){
          jq(this).removeClass('activecomment'); 
          jq(this).parents('.post').addClass('activepost');
        });                                          
    },
    initconfirmdialogs: function(e){
        if (jq('#tn-dialog-message').length) {
            defaultDialogMessage = jq('#tn-dialog-message').text();
            jq("#tn-dialog").dialog({  
              resizable: false,
              draggable: false,
              autoOpen: false,
              height: 120,
              width: 410,
              modal: true,
              close: function(ev, ui) { 
                jq('#tn-dialog-message').text(defaultDialogMessage);
                jq(this).hide(); 
              },
              focus: function(event, ui) { 
                ;
              }
            });
            links = 'a.confirmbefore';
            jq(links).click(function(e){
               e.preventDefault();
               initConfirmBox(this);
            } );       
        }
    },
    initformserrors: function(e) {
      jq('.fieldWrapper .errorlist').each(function(){
          jq(jq(this).parent()).addClass('fieldWrapperWithError');
      })
    },
    formsautofocus: function(e) {
     if (jq("form .fieldWrapperWithError :input:first").focus().length) return;
         jq("form.enableAutoFocus :input:visible:first").focus();
    },
    formUndo: function(e) {
        jq('.edit-form .form-controls button.reset').click( function(){
            if (jq('#referer_url').length) location.href = jq('#referer_url').val();
        })
    },
    formProtection: function(e) {
        var form_has_changes = false;
        oform = jq('.enableUnloadProtect');
        if (oform.length) {
            jq('input, textarea, select', oform).change(function() {
                form_has_changes = true;
            });
            jq(oform).submit(function(){
                form_has_changes = false;
                if (typeof tinyMCE != 'undefined') tinyMCE.activeEditor.isNotDirty;
            });
            jq(window).bind('beforeunload', function(e){
                if (typeof tinyMCE != 'undefined') {
                    if (tinyMCE.activeEditor.isDirty()) form_has_changes = true;
                }
                if (form_has_changes) {
                    // use the standard navigator beforeunload method
                    msg = jq('#form-protect-unload-message').html();
                    return msg;
                }
            })
        }
    },
    formInputsHints : function(e) {
        var inputs_with_hints = 'input[type="text"], input[type="checkbox"], input[type="radio"], select, textarea';
        jq(inputs_with_hints).focusin(function(e) {
            jq('.hint', jq(this).parent()).show();
        });
        jq(inputs_with_hints).focusout(function(e) {
            jq('.hint', jq(this).parent()).hide();
        });
    },
    tnGridActions: function(e) {
     jq('.tnGrid').each(function(){
            gridOnSelect(this);
        });
    },
    loadUploaders: function(e) {
        jq('.tnQuickUpload').each(function(){
            loadQuickUpload(this);
        });
    },
    tinymceBrowser: function(field_name, url, type, win) {
        var cmsURL = home_url + 'resource_browser/?allow_browser_selection=1&type=' + type;    // script URL - use an absolute path!
        var browser_width = parseInt(twistranet.browser_width*70/100);     
        var browser_height = parseInt(twistranet.browser_height*90/100);
        tinyMCE.activeEditor.windowManager.open({
            file : cmsURL,
            title : 'Twistranet Browser',
            width : browser_width,  // Your dimensions may differ - toy around with them!
            height : browser_height,
            resizable : "yes",
            inline : "yes",  // This parameter only has an effect with inlinepopups plugin!
            close_previous : "no"
        }, {
            window : win,
            input : field_name
        });
        return false;
    },
    initWysiwygBrowser: function() {
        if (typeof tinyMCEPopup != 'undefined') tinyMCEPopup.onInit.add(FileBrowserDialogue.init, FileBrowserDialogue);
        // put here the code for other editors (ckeditor ....)
    }
}

jq(document).ready(twistranet.__init__)
