import grpc
import logging
from ..proto import wx_admin_pb2
from ..proto import wx_admin_pb2_grpc

_logger = logging.getLogger(__name__)


def send_sub_login(address, msg):
    conn = grpc.insecure_channel(address)
    stub = wx_admin_pb2_grpc.WXAdminStub(conn)
    if 'scan' in msg.event:
        key = msg.scene_id
    else:
        key = msg.key
    _logger.info("msg.target %s" % msg.target)
    _logger.info("msg.source %s" % msg.source)
    _logger.info("msg.type %s" % msg.type)
    _logger.info("msg.event %s" % msg.event)
    _logger.info("msg.key %s" % key)
    _logger.info("msg.ticket %s" % msg.ticket)
    req = wx_admin_pb2.SubscribeScanLoginRequest(
        ToUserName=msg.target,
        FromUserName=msg.source,
        # CreateTime=msg.create_time,
        MsgType=msg.type,
        Event=msg.event,
        EventKey=key,
        Ticket=msg.ticket,
    )
    try:
        data = stub.SubscribeScanLogin(req)
        conn.close()
    except Exception as e:
        conn.close()
        _logger.error(f"grpc err,{str(e)}")
        return None
    return data
