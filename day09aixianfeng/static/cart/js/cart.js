$(function () {
    $('.cart').width(innerWidth)

    total()

    $('.cart .confirm-wrapper').click(function () {
        var $span=$(this).find('span')
        request_data={
            'cartid': $(this).attr('data-cardid')


        }
        $.get('/axf/changecartselect/',request_data,function (response) {
            console.log(response)

            if (response.status==1){
                if(response.isselect){
                    $span.removeClass('no').addClass('glyphicon glyphicon-ok')

                }else{
                    $span.removeClass('glyphicon glyphicon-ok').addClass('no')
                }
            total()
            }
        })
    })

    $('.cart .all').click(function () {
        var isall=$(this).attr('data-all')
        $span=$(this).find('span')
        isall=(isall=='false')? true :false
        $(this).attr('data-all',isall)
        if (isall){
            $span.removeClass('no').addClass('glyphicon glyphicon-ok')
        } else {
            $span.removeClass('glyphicon glyphicon-ok').addClass('no')
        }
        request_data={
            'isall':isall
        }
        $.get('/axf/changeall/',request_data,function (response) {
            console.log(response)
            if (response.status==1){
                $('.confirm-wrapper').each(function () {
                    if (isall){
                        $(this).find('span').removeClass('no').addClass('glyphicon glyphicon-ok')
                    }else{
                        $(this).find('span').removeClass('glyphicon glyphicon-ok').addClass('no')
                    }

                    total()
                })



            }

        })


    })



    //
 function total() {
         var sum=0
        $('.cart li').each(function () {
            var $confirm=$(this).find('.confirm-wrapper')
            var $content=$(this).find('.content-wrapper')

            if ($confirm.find('.glyphicon').length){
                var price=$content.find('.price').attr('data-price')
                var num=$content.find('.num').attr('data-number')
                sum+=num*price
            }

        })
      $('.bill .total b').html(sum)
    }
})

