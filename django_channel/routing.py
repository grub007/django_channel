#!/usr/bin/env python
# -*- coding:utf-8 -*-

from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import myproject.routing

application = ProtocolTypeRouter({
    # (http->django views is added by default)
    'websocket': AuthMiddlewareStack(
        URLRouter(
            myproject.routing.websocket_urlpatterns
        )
    )
})