$(document).ready(function() {
  // Show Placements - selects / unselects a bet box
  $(document).on('click', '.bet-selection-div', function(e){
    e.preventDefault();
    var highlightBetBox = 'bg-primary text-white';
    var otherBetOption = $(this).siblings();
    $(this).hasClass(highlightBetBox) ? $(this).removeClass(highlightBetBox) : $(this).addClass(highlightBetBox);
    // If sibling div is already highlighted - removeClass
    if ($(otherBetOption).hasClass(highlightBetBox)){
      $(otherBetOption).removeClass(highlightBetBox);
    }
  })

});