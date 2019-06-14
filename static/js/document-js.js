$(document).ready(function(){
	$('[data-toggle="tooltip"]').tooltip();

    $("#info-teacher").popover({
        html : true,
        trigger: "manual",
        content: function() {
            var content = $(this).attr("data-popover-content");
            return $(content).children("#info-teacher-data").html();
        },
        animation:false
    }).on("mouseenter", function () {
        var _this = this;
        $(this).popover("show");
        $(".popover").on("mouseleave", function () {
            $(_this).popover('hide');
        });
    }).on("mouseleave", function () {
        var _this = this;
        setTimeout(function () {
            if (!$(".popover:hover").length) {
                $(_this).popover("hide");
            }
        }, 300);
})
    });