var deleteMemo = function(memo) {
  var url = $SCRIPT_ROOT + '/_destroy';
  var data = {memo: memo};
  console.log("DELETEMEMO:" memo);
  $.ajax({
    type: "DELETE",
    url: url,
    data: data,
    success: function() {
      console.log("Something should have happened...")
    }
  }).fail(function() {
    console.log("ERROR");
  });
  
}

$('a[name="destroy"]').on("click", function(){
  var self = $(this);
  var memoObject = self.parents(".row").find("#memo-text");
  var memo = memoObject.text();
  deleteMemo(memo);
});