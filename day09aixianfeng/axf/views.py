import hashlib
import random
import time

from django.http import JsonResponse
from django.shortcuts import render, redirect

# Create your views here.
from axf.models import Wheel, Nav, Mustbuy, Shop, Mainshow, Foodtype, Goods, User, Cart


def home(request):
    wheels=Wheel.objects.all()
    navs=Nav.objects.all()
    mustbuys=Mustbuy.objects.all()
    shops=Shop.objects.all()
    shophead=shops[0]
    shoptabs=shops[1:3]
    shopclass_list=shops[3:7]
    shopcommends=shops[7:11]
    mainshows=Mainshow.objects.all()
    data={
        'wheels':wheels,
        'navs':navs,
        'mustbuys':mustbuys,
        'shophead':shophead,
        'shoptabs':shoptabs,
        'shopclass_list':shopclass_list,
        'shopcommends':shopcommends,
        'mainshows':mainshows
    }



    return render(request,'home/home.html' ,context=data)


def market(request,childid='0',sortid='0'):
    foodtypes=Foodtype.objects.all()

    # goods_list=Goods.objects.all()[0:5]
    # goods_list = Goods.objects.filter(categoryid=categoryid)
    index=int(request.COOKIES.get('index','0'))
    categoryid=foodtypes[index].typeid

    if childid == '0':
        goods_list = Goods.objects.filter(categoryid=categoryid)
    else:
        goods_list = Goods.objects.filter(categoryid=categoryid).filter(childcid=childid)

    if sortid == '1':
        goods_list = goods_list.order_by('-productnum')
    elif sortid == '2':
        goods_list = goods_list.order_by('price')
    elif sortid == '3':
        goods_list = goods_list.order_by('-price')

    # if childid == '0':
    #     goods_list = Goods.objects.filter(categoryid=categoryid)
    # else:
    #     goods_list = Goods.objects.filter(categoryid=categoryid).filter(childcid=childid)

    # goods_list=Goods.objects.filter(categoryid=categoryid)


    childtypenames=foodtypes[index].childtypenames
    childtype_list=[]
    for item in childtypenames.split('#'):
        item_arr=item.split(':')
        temp_dir={
            'name':item_arr[0],
            'id':item_arr[1]
        }
        childtype_list.append(temp_dir)

    token=request.session.get('token','')
    if token:
        user=User.objects.get(token=token)
        carts = user.cart_set.filter(number__gt=0)
    else:
        carts=None

    response_dir = {
        'foodtypes': foodtypes,
        'goods_list': goods_list,
        'childtype_list':childtype_list,
        'childid': childid,
        'carts':carts
    }

    back=request.COOKIES.get('back')


    return render(request,'market/market.html',context=response_dir)


def mine(request):

    token=request.session.get('token')
    user=None
    if token:
        user=User.objects.get(token=token)



    return render(request,'mine/mine.html',context={'user':user})


def cart(request):
    token=request.session.get('token')


    if token :
        user=User.objects.get(token=token)
        carts = user.cart_set.filter(number__gt=0)
        isall=True
        for cart in carts:
            if not cart.isselect:
                isall=False
        return render(request,'cart/cart.html',context={'carts': carts,
                                                        'isall':isall})
    else:


        return render(request,'mine/login.html')


def generate_token():
    token = str(time.time()) + str(random.random())
    md5 = hashlib.md5()
    md5.update(token.encode('utf-8'))

    return md5.hexdigest()


def generate_password(param):
    md5 = hashlib.md5()
    md5.update(param.encode('utf-8'))
    return md5.hexdigest()


def register(request):
    if request.method == "GET":
        return render(request, 'mine/register.html')
    elif request.method == "POST":
        email=request.POST.get('email')
        password=request.POST.get('password')
        name=request.POST.get('name')
        token=generate_token()
        try:
            user=User()
            user.email=email
            user.password=generate_password(password)
            user.name=name
            user.token=token
            user.save()
            response=redirect('axf:mine')
            request.session['token']=user.token

            return response
        except:
            return render(request,'mine/register.html')


def login(request):
    if request.method=='GET':
        return render(request,'mine/login.html')
    elif request.method=='POST':
        back=request.COOKIES.get('back')
        print(back)

        name=request.POST.get('name')
        password=request.POST.get('password')
        users=User.objects.filter(name=name).filter(password=password)
        if users.exists():
            user=users.first()
            user.token=generate_token()

            user.save()
            request.session['token']=user.token

            if back == 'mine':
                return  redirect('axf:mine')

            elif back =='market':
                return redirect('axf:marketbase')
        else:
            return  render(request,'mine/login.html')

def logout(request):
    request.session.flush()
    return redirect('axf:mine')


def addcart(request):
    token=request.session.get('token','')

    response_data={}
    if token :

        goodid=request.GET.get('goodid')
        good=Goods.objects.get(pk=goodid)


        response_data['statue']=1
        user=User.objects.get(token=token)
        carts=Cart.objects.filter(user=user).filter(goods=good)
        if carts.exists():
            cart=carts.first()
            cart.number+=1
            cart.save()
        else:
            cart=Cart()
            cart.user=user
            cart.goods=good
            cart.number=1
            cart.save()

        response_data['statue'] = 1
        response_data['number'] = cart.number
        response_data['msg']='添加{}商品成功到购物车{}'.format(cart.goods.productlongname,cart.number)
        return JsonResponse(response_data)
    else:
        response_data['statue']=-1
        return JsonResponse(response_data)


def subcart(request):
    goodid=request.GET.get('goodid')
    print(goodid)
    response_data={}

    token=request.session.get('token','')
    print(token)
    if token:
        response_data={}
        good=Goods.objects.get(pk=goodid)
        user=User.objects.get(token=token)
        carts = Cart.objects.filter(user=user).filter(goods=good)
        if carts.exists():
            cart=carts.first()
            if cart.number>=1:
                cart.number-=1

                cart.save()
                response_data['number'] = cart.number
        response_data['statue'] = 1

        response_data['msg'] = '删减商品成功{},商品剩余数量：{}'.format(cart.goods.productlongname,cart.number)
        return JsonResponse(response_data)

    else:
        response_data['statue']=-2


        return JsonResponse(response_data)


def changecartselect(request):
    cartid=request.GET.get('cartid')
    cart=Cart.objects.get(pk=cartid)
    cart.isselect= not cart.isselect
    cart.save()
    print(cartid)

    response_data={
        'msg':'修改状态成功',
        'status':'1',
        'isselect':cart.isselect
    }
    return JsonResponse(response_data)


def changeall(request):
    isall=request.GET.get('isall')
    token=request.session.get('token')
    user=User.objects.get(token=token)
    carts=user.cart_set.all()
    if isall=='true':
        isall=True
    else:
        isall=False
    for cart in carts:
        cart.isselect=isall
        cart.save()
    # print(isall)
    response_data={
        'msg':'success',
        'status':'1'
    }

    return JsonResponse(response_data)


def generateorder(request):
    return render(request, 'order/orderdetail.html')


def orderlist(request):
    return None


def orderdetail(request):
    return None