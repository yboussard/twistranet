jq(function() 
{
  jq(".view_comments").click(function() 
  {
    var ID = jq(this).attr("id");
    
    jq.ajax({
      type: "GET",
      url: "/comment/" + ID + "/list.xml",
      // data: "msg_id="+ ID, 
      cache: false,
      success: function(html){
        var comments_container = jq("#view_comments"+ID);
        comments_container.prepend(html);
        jq("#view"+ID).remove();
        jq("#two_comments"+ID).remove(); 
        twistranet.showCommentsActions();
        jq('a.confirmbefore', comments_container).click(function(e){
           e.preventDefault();
           initConfirmBox(this);
        } );
      }
    });
    return false;
  });
});

