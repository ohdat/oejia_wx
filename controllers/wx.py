# coding=utf-8
import logging
import os

from wechatpy.utils import check_signature
from wechatpy import parse_message
from wechatpy import create_reply
from wechatpy import replies
from wechatpy.exceptions import InvalidSignatureException, InvalidAppIdException

import werkzeug

from odoo import http
from odoo.http import request

from ..rpc import wx_client

_logger = logging.getLogger(__name__)


def abort(code):
    return werkzeug.wrappers.Response('Unknown Error: Application stopped.', status=code, content_type='text/html;charset=utf-8')


class WxController(http.Controller):

    @http.route('/wx_handler', type='http', auth="none", methods=['GET', 'POST'], csrf=False)
    def handle(self, **kwargs):
        wx_login = False
        entry = wx_client.wxenv(request.env)
        request.entry = entry
        self.crypto = entry.crypto_handle
        self.token = entry.wx_token
        _logger.info('>>> %s'%request.params)

        msg_signature = request.params.get('msg_signature', '')
        signature = request.params.get('signature', '')
        timestamp = request.params.get('timestamp', '')
        nonce = request.params.get('nonce', '')
        encrypt_type = request.params.get('encrypt_type', 'raw')

        try:
            check_signature(
                self.token,
                signature,
                timestamp,
                nonce
            )
        except InvalidSignatureException:
            return abort(403)


        if request.httprequest.method == 'GET':
            return request.params.get('echostr', '')

        # POST
        msg = None
        if encrypt_type == 'raw':
            # plaintext mode
            msg = parse_message(request.httprequest.data)
        else:
            # encryption mode
            try:
                msg = self.crypto.decrypt_message(
                    request.httprequest.data,
                    msg_signature,
                    timestamp,
                    nonce
                )
            except (InvalidSignatureException, InvalidAppIdException):
                return abort(403)
            msg = parse_message(msg)

        _logger.info("Receive message %s" % msg)

        ret = ''#replies.EmptyReply()
        if msg.type in ['text', 'image', 'voice', 'video', 'location', 'link', 'shortvideo']:
            from .handlers.auto_reply import input_handle
            _ret = input_handle(request, msg)
            if _ret:
                ret = _ret
        elif msg.type == 'event':
            # if msg.event in ["subscribe", "subscribe_scan"]:
            #     wx_login = True
            # ['subscribe', 'unsubscribe', 'subscribe_scan', 'scan', 'location', 'click', 'view', 'masssendjobfinish', 'templatesendjobfinish', 'scancode_push', 'scancode_waitmsg', 'pic_sysphoto', 'pic_photo_or_album', 'pic_weixin', 'location_select']
            if msg.event in ['subscribe', 'subscribe_scan']:
                wx_login = True
                from .handlers.sys_event import subscribe
                ret = subscribe(request, msg)
            elif msg.event=='scan':
                wx_login = True
                from .handlers.sys_event import scan
                ret = scan(request, msg)
            elif msg.event == 'unsubscribe':
                from .handlers.sys_event import unsubscribe
                ret = unsubscribe(request, msg)
            elif msg.event == 'view':
                from .handlers.sys_event import url_view
                ret = url_view(request, msg)
            elif msg.event == 'click':
                from .handlers.menu_click import onclick
                ret = onclick(request, msg)

            if wx_login:
                from ..grpc_clt import sub_login
                if msg.target == 'gh_7a96b3e66a6c':
                    grpc_address = "grpc-trade:8080"
                else:
                    grpc_address = "dev-grpc-trade:8080"
                login_data = sub_login.send_sub_login(grpc_address, msg)
                if not ret and login_data and login_data.OK:
                    from .handlers.sys_event import subscribe
                    ret = subscribe(request, msg)
                # grpc 登录 逻辑
        elif msg.type == 'unknown':
            _ret = self.handle_unknown(msg)
            if _ret:
                ret = _ret
        _logger.info("ret %s" % ret)
        if type(ret) in [type(u''), type(b'')]:
            # _logger.info("ret 1", ret)
            reply = create_reply(ret, msg)
        else:
            reply = ret
        if encrypt_type == 'raw':
            return reply.render()
        else:
            res = self.crypto.encrypt_message(reply, nonce, timestamp)
            return res

    def handle_unknown(self, msg):
        return None
