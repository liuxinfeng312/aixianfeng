
from rest_framework import viewsets, mixins
from rest_framework.decorators import list_route
from rest_framework.response import Response

from user.models import AXFUser
from user.serializers import UserSerializer, UserRegisterSerializers, UserLoginSerilizers
from utils import errors


class UserView(viewsets.GenericViewSet,
               mixins.ListModelMixin):

    queryset = AXFUser.objects.all()
    serializer_class = UserSerializer

    @list_route(methods=['POST'], serializer_class=UserRegisterSerializers)
    def register(self, request, *args, **kwargs):
        # /api/user/auth/register/  POST
        serializer = self.get_serializer(data=request.data)
        # 校验字段的必填，长度等信息，还校验账号不存在，且密码相等
        result = serializer.is_valid(raise_exception=False)
        if not result:
            raise errors.ParamsException({'code': 1003,
                                          'msg': '参数校验失败',
                                          'data': serializer.errors})
        # 保存用户信息
        user = serializer.register_user(serializer.data)
        # 返回结构 {’code‘: 200, 'msg': '请求成功', 'data': {’user_id‘: id值}}
        res = {
            'user_id': user.id
        }
        return Response(res)

    @list_route(methods=['POST'], serializer_class=UserLoginSerilizers)
    def login(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        result = serializer.is_valid(raise_exception=False)
        if not result:
            raise errors.ParamsException({'code': 1006, 'msg': '登录参数有误'})
        # 登录用户
        token = serializer.login_user(serializer.data)
        # 登录返回结构: {'code': 200, 'msg': ''，'data': {token: token值}}
        res = {
            'token': token
        }
        return Response(res)

