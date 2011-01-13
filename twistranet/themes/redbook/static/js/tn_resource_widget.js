// reource widget helper
jQuery(
    function(){
        reswidget = jQuery('.resource-widget');
        theform = reswidget.parents('form');
        target_selector = jQuery('#selector_target', reswidget);
        if (target_selector.length) {
            theform.bind('submit', function(){
                 selectedfield = jQuery('.tnGrid input:checked', reswidget);
                 if (selectedfield.length) {
                     jQuery('#' + target_selector.val()).val(selectedfield.val());
                 }
                 target_selector.remove();
                 jQuery('input .tnGrid', reswidget).remove();
            })
        }
    }
)