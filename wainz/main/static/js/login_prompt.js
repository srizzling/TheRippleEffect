!function($) {
    
    if(!$){console.log('jquery required'); return;}

    var LoginPrompt = function(elem, opts){
        this.$elem = $(elem);
        this.$prompt = $("<div class='arrow_box login alert alert-error' data-dismiss='alert' style='cursor:pointer'>Please login to use this feature</div>");
        this.$prompt.css({"position":"fixed"});
        this.$prompt.css({"z-index":"1000"});
        this.opts = opts;
    };

    LoginPrompt.prototype = {
        constructor: LoginPrompt,
        listen : function () {
            var that = this;
            this.$elem.click(function (e) {
                e.preventDefault();
                that.show();
            });
            $(window).resize(function() { 
              that.opts.left = $(".login-button").offset().left*0.79; 
		that.$prompt.animate({"top":parseInt(that.opts.top)+"px", "left":that.opts.left+"px"}, 1);
            });
        },
        show : function () {
            $('.login.alert').remove();
            $('.main.container').append(this.$prompt);
            var that = this;
            this.$prompt.animate({"top":parseInt(this.opts.top)+"px", "left":this.opts.left+"px"}, function() {
                that.$prompt.fadeIn();
            });
        }
    }

    $.fn.loginPrompt = function(options){
        return this.each(function() {
            var $this = $(this), data = $this.data('loginPrompt'), options = $.extend({}, $.fn.loginPrompt.defaults, typeof options == 'object');
            if(!data) $this.data('loginPrompt', (data = new LoginPrompt(this, options)));
            data.listen();
        });
    }

    $.fn.loginPrompt.defaults = {
        top  : "60",
        left : $(".login-button").offset().left*0.79
    }

}(window.jQuery);
