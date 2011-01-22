/**
 *
 * JQuery Helpers for Quick Upload
 *   
 */    

var TwistranetQuickUpload = {};
var lastUploadUrl = '';
var lastUploadPreviewUrl = '';
var lastUploadMiniUrl = '';
var lastUploadLegend = '';
var lastUploadValue = '';  
var scopeValue = '';
var lastUploadType = '';
    
TwistranetQuickUpload.addUploadFields = function(uploader, domelement, file, id, fillTitles) {
    if (fillTitles)  {
        var labelfiletitle = jQuery('#uploadify_label_file_title').val();
        var blocFile = uploader._getItemByFileId(id);
        if (typeof id == 'string') id = parseInt(id.replace('qq-upload-handler-iframe',''));
        jQuery('.qq-upload-cancel', blocFile).after('\
                  <div class="uploadField">\
                      <label>' + labelfiletitle + '&nbsp;:&nbsp;</label> \
                      <input type="text" \
                             class="file_title_field" \
                             id="title_' + id + '" \
                             name="title" \
                             value="" />\
                  </div>\
                   ')
    }
    TwistranetQuickUpload.showButtons(uploader, domelement);
}

TwistranetQuickUpload.showButtons = function(uploader, domelement) {
    var handler = uploader._handler;
    if (handler._files.length) {
        jQuery('.uploadifybuttons', jQuery(domelement).parent()).show();
        return 'ok';
    }
    return false;
}

TwistranetQuickUpload.sendDataAndUpload = function(uploader, domelement, typeupload) {
    var handler = uploader._handler;
    var files = handler._files;
    var missing = 0;
    for ( var id = 0; id < files.length; id++ ) {
        if (files[id]) {
            var fileContainer = jQuery('.qq-upload-list li', domelement)[id-missing];
            var file_title = '';
            if (fillTitles)  {
                file_title = jQuery('.file_title_field', fileContainer).val();
            }
            uploader._queueUpload(id, {'title': file_title, 'typeupload' : typeupload});
        }
        // if file is null for any reason jq block is no more here
        else missing++;
    }
}

// same method as tn_resource_browser > showPreview
// used when quickuploader is used outside of resource widget
TwistranetQuickUpload.uploadPreview = function(url, miniurl, previewurl, legend, type) {
    newResultContainer = jQuery('#renderer-new');
    if (newResultContainer.length) {
        currentResultContainer = jQuery('#renderer-current');
        result= '\
<a class="image-block image-block-mini"\
   href="'+ url +'"\
   title="' + legend + '">\
   <img src="' + miniurl + '"\
        alt="' + legend + '" />\
</a>\
';
        jQuery('a', newResultContainer).remove();      
        jQuery('.sizes-selection', newResultContainer).remove();
        newResultContainer.append(result);
        newResultContainer.css('visibility', 'visible');
        if (currentResultContainer.length) currentResultContainer.animate({'opacity': '0.4'}, 500);
    }
}


TwistranetQuickUpload.onAllUploadsComplete = function(){
    showPreview (lastUploadUrl, lastUploadMiniUrl, lastUploadPreviewUrl, lastUploadLegend, lastUploadType);
    // fix selector value in a form
    target_selector = jQuery('#selector_target');
    if (target_selector.length) {
        selector.val(lastUploadValue);
        new_selection = lastUploadValue;
        // reload the publisher panel with last upload value if exists
        if (scopeValue && typeof reloadScope != 'undefined') reloadScope(scopeValue.toString(), lastUploadValue, true);
    }

}
TwistranetQuickUpload.clearQueue = function(uploader, domelement) {
    var handler = uploader._handler;
    var files = handler._files;
    for ( var id = 0; id < files.length; id++ ) {
        if (files[id]) {
            handler.cancel(id);
        }
        jQuery('.qq-upload-list li', domelement).remove();
        handler._files = [];
        if (typeof handler._inputs != 'undefined') handler._inputs = {};
    }    
}    
TwistranetQuickUpload.onUploadComplete = function(uploader, domelement, id, fileName, responseJSON) {
    var uploadList = jQuery('.qq-upload-list', domelement);
    if (responseJSON.success) {        
        window.setTimeout( function() {
            jQuery(uploader._getItemByFileId(id)).remove();
            // after the last upload, if no errors, reload the page
            var newlist = jQuery('li', uploadList);
            if (! newlist.length) {
                lastUploadUrl = responseJSON.url;
                lastUploadPreviewUrl = responseJSON.preview_url;
                lastUploadMiniUrl = responseJSON.mini_url;
                lastUploadType = responseJSON.type;
                lastUploadLegend = responseJSON.legend; 
                lastUploadValue = responseJSON.value;
                scopeValue = responseJSON.scope;
                if(scopeValue && typeof Panels!='undefined') Panels[scopeValue.toString()] = 'unloaded';
                window.setTimeout( TwistranetQuickUpload.onAllUploadsComplete, 5);
            }       
        }, 50);
    }
    
}

