###
# Onvif documentation
# http://www.onvif.org/ver20/ptz/wsdl/ptz.wsdl
####
import requests
import time
import logging
from datetime import datetime
from enum import Enum
import base64
import hashlib
from numpy import random

_LOGGER = logging.getLogger(__name__)

DOMAIN = "ptz_camera"

class CameraType(Enum):
    YOOSEE = "YOOSEE"
    YCC365 = "YCC365"
    Y05 = "Y05"

ATTR_HOST = "host"
DEFAULT_HOST = "192.168.1.244"
ATTR_MOVE_TIME = "move_time"
DEFAULT_MOVE_TIME = 0.5
ATTR_CAMERA_TYPE = "camera_type"
DEFAULT_CAMERA_TYPE = CameraType.YOOSEE.name
ATTR_MOVE_DIRECTION = "move_direction"
DEFAULT_MOVE_DIRECTION = "none"
ATTR_MOVE_STEPS = "move_steps"
DEFAULT_MOVE_STEPS = 60

# credentials used by Y05 and YOOSEE
USR = "admin"
YOUR_ONVIF_PWD = "your_onvif_password"
IS_INVERT_UPDOWN = False

ATTR_PRESET_TOKEN = "preset_token"
ATTR_PAN_TIME = "pan_time"
ATTR_TILT_TIME = "tilt_time"
ATTR_PAN = "pan"
ATTR_TILT= "tilt"

_DEFAULT_PROFILE = "dummy"
_DEFAULT_PRESET_TOKEN = "dummy"
_PWD = "dummy"
_NONCE = "dummy"
_SERVICE_PATH = "dummy"

# Used by YCC365 moving
YCC365_DEFAULT_PANT_TIME = 4
YCC365_DEFAULT_TILT_TIME = 1
YCC365_DEFAULT_PAN = 0.1
YCC365_DEFAULT_TILT = 0.1
YCC365_DEFAULT_HEADERS = {'Content-Type': 'application/soap+xml;charset=UTF8'}
YCC365_DEFAULT_PROFILE = "Profile_1"

# Used by Y05
Y05_DEFAULT_PROFILE = "PROFILE_000"
Y05_DEFAULT_PRESET_TOKEN = "Preset1"
Y05_SERVICE_PATH = ":6688/onvif/ptz_service"

# Used by YOOSEE
YOOSEE_DEFAULT_PROFILE = "IPCProfilesToken1"
YOOSEE_SERVICE_PATH = ":5000/onvif/deviceio_service"

CREATION_DATE = datetime.utcnow().isoformat()[:-3] + 'Z'
YOOSEE_NONCE_STR = str(random.randint(1000000))
YOOSEE_NONCE_BASE64 = str(base64.b64encode( YOOSEE_NONCE_STR.encode() ))
YOOSEE_DIGEST_BASE64 = str(base64.b16encode( hashlib.sha1( (YOOSEE_NONCE_STR + CREATION_DATE + YOUR_ONVIF_PWD).encode() ).digest() ))

ONVIF_SERVICE_ENVELOPE = """
<?xml version="1.0" encoding="utf-8"?>
<s:Envelope xmlns:s="http://www.w3.org/2003/05/soap-envelope">
    <s:Header>
    <Security s:mustUnderstand="1" xmlns="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd">
        <UsernameToken>
            <Username>""" + USR + """</Username>
            <Password Type="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-username-token-profile-1.0#PasswordDigest">""" + YOOSEE_DIGEST_BASE64 + """</Password>
            <Nonce EncodingType="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-soap-message-security-1.0#Base64Binary">""" + YOOSEE_NONCE_BASE64 + """</Nonce>
            <Created xmlns="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd">""" + CREATION_DATE + """</Created>
        </UsernameToken>
    </Security>
    </s:Header>
    <s:Body xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema">
    _service_content_
    </s:Body>
</s:Envelope>"""

def setup(hass, config):
    def stop(host, cameraType):
        if cameraType == CameraType.Y05.name or cameraType == CameraType.YOOSEE.name:
            service = 'Stop'

            if cameraType == CameraType.Y05.name:
                _DEFAULT_PROFILE = Y05_DEFAULT_PROFILE
                _SERVICE_PATH = Y05_SERVICE_PATH

            if cameraType == CameraType.YOOSEE.name:
                _DEFAULT_PROFILE = YOOSEE_DEFAULT_PROFILE
                _SERVICE_PATH = YOOSEE_SERVICE_PATH

            service_call = """<Stop xmlns="http://www.onvif.org/ver20/ptz/wsdl">
                                  <ProfileToken>""" + _DEFAULT_PROFILE + """</ProfileToken>
                                  <PanTilt>true</PanTilt>
                                  <Zoom>true</Zoom>
                              </Stop>"""

            xml = ONVIF_SERVICE_ENVELOPE.replace("_service_content_", service_call)

            r = requests.post('http://' + host + _SERVICE_PATH, data=xml, headers={'Content-Type': 'application/soap+xml;charset=UTF8; action="http://www.onvif.org/ver20/ptz/wsdl/' + service})

        elif cameraType == CameraType.YCC365.name:

            xml = """<?xml version="1.0" encoding="utf-8"?>
                     <soap:Envelope xmlns:soap="http://www.w3.org/2003/05/soap-envelope" xmlns:tptz="http://www.onvif.org/ver20/ptz/wsdl">
                        <soap:Body>
                            <tptz:Stop>
                                <tptz:ProfileToken>""" + YCC365_DEFAULT_PROFILE + """</tptz:ProfileToken>
                                <tptz:PanTilt>true</tptz:PanTilt>
                                <tptz:Zoom>true</tptz:Zoom>
                            </tptz:Stop>
                        </soap:Body>
                     </soap:Envelope>"""

            r = requests.post('http://' + host + '/onvif/PTZ', data=xml, headers=YCC365_DEFAULT_HEADERS)

        if r.status_code != requests.codes.OK:
            _LOGGER.error(__name__ + ": Invalid [stop] Response [" + str(r.status_code) + "]")

    def move(call, move_time, x_coord=0.0, y_coord=0.0, use_stop=True):
        host = call.data.get(ATTR_HOST, DEFAULT_HOST)
        cameraType = call.data.get(ATTR_CAMERA_TYPE, DEFAULT_CAMERA_TYPE)

        if cameraType == CameraType.Y05.name or cameraType == CameraType.YOOSEE.name:
            service = 'ContinuousMove'

            if cameraType == CameraType.Y05.name:
                _DEFAULT_PROFILE = Y05_DEFAULT_PROFILE
                _SERVICE_PATH = Y05_SERVICE_PATH

            if cameraType == CameraType.YOOSEE.name:
                _DEFAULT_PROFILE = YOOSEE_DEFAULT_PROFILE
                _SERVICE_PATH = YOOSEE_SERVICE_PATH

            service_call = """<ContinuousMove xmlns="http://www.onvif.org/ver20/ptz/wsdl">
                                  <ProfileToken>""" + _DEFAULT_PROFILE + """</ProfileToken>
                                  <Velocity>
                                      <PanTilt x="_x_coord_" y="_y_coord_" xmlns="http://www.onvif.org/ver10/schema"/>
                                  </Velocity>
                              </ContinuousMove>""".replace("_x_coord_", str(x_coord)).replace("_y_coord_", str(y_coord))

            xml = ONVIF_SERVICE_ENVELOPE.replace("_service_content_", service_call)

            r = requests.post('http://' + host + _SERVICE_PATH, data=xml, headers={
                'Content-Type': 'application/soap+xml;charset=UTF8; action="http://www.onvif.org/ver20/ptz/wsdl/' + service})

        elif cameraType == CameraType.YCC365.name:
            xml = """<?xml version="1.0" encoding="utf-8"?>
                     <soap:Envelope xmlns:soap="http://www.w3.org/2003/05/soap-envelope" xmlns:tptz="http://www.onvif.org/ver20/ptz/wsdl" xmlns:tt="http://www.onvif.org/ver10/schema">
                         <soap:Body>
                             <tptz:ContinuousMove>
                                 <tptz:ProfileToken>""" + YCC365_DEFAULT_PROFILE + """</tptz:ProfileToken>
                                 <tptz:Velocity>
                                     <tt:PanTilt x="_x_" y="_y_"/>
                                     <tt:Zoom x="1"/>
                                 </tptz:Velocity>
                             </tptz:ContinuousMove>
                         </soap:Body>
                     </soap:Envelope>""".replace("_x_", str(x_coord)).replace("_y_", str(y_coord))

            r = requests.post('http://' + host + '/onvif/PTZ', data=xml, headers=YCC365_DEFAULT_HEADERS)

        if r.status_code != requests.codes.OK:
            _LOGGER.error(__name__ + ": Invalid [move] Response [" + str(r.status_code) + "]")

        time.sleep(move_time)

        if use_stop and cameraType != CameraType.YOOSEE.name:
            stop(host, cameraType)

    def move_origin(call):
        host = call.data.get(ATTR_HOST, DEFAULT_HOST)
        cameraType = call.data.get(ATTR_CAMERA_TYPE, DEFAULT_CAMERA_TYPE)
        move_steps = call.data.get(ATTR_MOVE_STEPS, DEFAULT_MOVE_STEPS)

        if cameraType == CameraType.Y05.name:
            service = 'GotoHomePosition'

            if cameraType == CameraType.Y05.name:
                _DEFAULT_PROFILE = Y05_DEFAULT_PROFILE
                _SERVICE_PATH = Y05_SERVICE_PATH

            service_call = """<GotoHomePosition xmlns="http://www.onvif.org/ver20/ptz/wsdl">
                                  <ProfileToken>""" + _DEFAULT_PROFILE + """</ProfileToken>
                              </GotoHomePosition>"""

            xml = ONVIF_SERVICE_ENVELOPE.replace("_service_content_", service_call)

            r = requests.post('http://' + host + _SERVICE_PATH, data=xml, headers={
                'Content-Type': 'application/soap+xml;charset=UTF8; action="http://www.onvif.org/ver20/ptz/wsdl/' + service})

            if r.status_code != requests.codes.OK:
                _LOGGER.error(__name__ + ": Invalid [move_origin] Response [" + str(r.status_code) + "]")

        elif cameraType == CameraType.YOOSEE.name:
            move_time = call.data.get(ATTR_MOVE_TIME, DEFAULT_MOVE_TIME)
            #Move Privacy first
            move_privacy(call)

            #Move to Origin
            count = 1
            while count < move_steps:
                count += 1
                move(call, move_time, -0.5, 0, False)
        elif cameraType == CameraType.YCC365.name:
            pan_time = call.data.get(ATTR_PAN_TIME, YCC365_DEFAULT_PANT_TIME)
            tilt_time = call.data.get(ATTR_TILT_TIME, YCC365_DEFAULT_TILT_TIME)

            pan = call.data.get(ATTR_PAN, YCC365_DEFAULT_PAN)
            tilt = call.data.get(ATTR_TILT, YCC365_DEFAULT_TILT)

            if pan != 0:
                #Move to the end
                _pan = pan * -1
                move(call, pan_time, _pan, 0)
                time.sleep(pan_time)
                #Execute based on position in the parameter
                pan_timer = pan_time * abs(pan)
                time.sleep(pan_timer)
                move(call, pan_timer, pan, 0)

            #Move to the end
            _tilt = tilt * -1
            move(call, tilt_time, 0, _tilt)
            #Execute based on position in the parameter
            tilt_timer = tilt_time * abs(tilt)
            time.sleep(tilt_timer)
            move(call, tilt_timer, 0, tilt)

    def move_to_direction(call):
        direction = call.data.get(ATTR_MOVE_DIRECTION, DEFAULT_MOVE_DIRECTION).lower()

        if direction == "down":
            move_down(call)
        elif direction == "up":
            move_up(call)
        elif direction == "left":
            move_left(call)
        elif direction == "right":
            move_right(call)

    def move_left(call):
        move_time = call.data.get(ATTR_MOVE_TIME, DEFAULT_MOVE_TIME)
        move(call, move_time, -0.1, 0.0)

    def move_right(call):
        move_time = call.data.get(ATTR_MOVE_TIME, DEFAULT_MOVE_TIME)
        move(call, move_time, 0.1, 0.0)

    def move_up(call):
        move_time = call.data.get(ATTR_MOVE_TIME, DEFAULT_MOVE_TIME)
        cameraType = call.data.get(ATTR_CAMERA_TYPE, DEFAULT_CAMERA_TYPE)
        if IS_INVERT_UPDOWN:
            move(call, move_time, 0.0, -0.1)
        else:
            move(call, move_time, 0.0, 0.1)

    def move_down(call):
        move_time = call.data.get(ATTR_MOVE_TIME, DEFAULT_MOVE_TIME)
        cameraType = call.data.get(ATTR_CAMERA_TYPE, DEFAULT_CAMERA_TYPE)
        if IS_INVERT_UPDOWN:
            move(call, move_time, 0.0, 0.1)
        else:
            move(call, move_time, 0.0, -0.1)

    def move_privacy(call):
        move_time = call.data.get(ATTR_MOVE_TIME, DEFAULT_MOVE_TIME)
        cameraType = call.data.get(ATTR_CAMERA_TYPE, DEFAULT_CAMERA_TYPE)
        move_steps = call.data.get(ATTR_MOVE_STEPS, DEFAULT_MOVE_STEPS)

        if cameraType == CameraType.Y05.name:
            move(call, move_time, -1.0, 1.0, False)
        elif cameraType == CameraType.YOOSEE.name:
            count = 0
            while count < move_steps:
                count += 1
                move(call, move_time, 0.5, 0, False)
        elif cameraType == CameraType.YCC365.name:
            pan_time = call.data.get(ATTR_PAN_TIME, YCC365_DEFAULT_PANT_TIME)
            tilt_time = call.data.get(ATTR_TILT_TIME, YCC365_DEFAULT_TILT_TIME)

            move(call, pan_time, 1, 0, False)
            move(call, tilt_time, 0, 1, False)

    def move_to_preset(call):
        host = call.data.get(ATTR_HOST, DEFAULT_HOST)
        cameraType = call.data.get(ATTR_CAMERA_TYPE, DEFAULT_CAMERA_TYPE)
        preset_token = call.data.get(ATTR_PRESET_TOKEN, Y05_DEFAULT_PRESET_TOKEN)

        if cameraType == CameraType.Y05.name or cameraType == CameraType.YOOSEE.name:
            service = "GotoPreset"

            if cameraType == CameraType.Y05.name:
                _DEFAULT_PROFILE = Y05_DEFAULT_PROFILE
                _SERVICE_PATH = Y05_SERVICE_PATH

            if cameraType == CameraType.YOOSEE.name:
                _DEFAULT_PROFILE = YOOSEE_DEFAULT_PROFILE
                _SERVICE_PATH = YOOSEE_SERVICE_PATH

            service_call = """<GotoPreset xmlns="http://www.onvif.org/ver20/ptz/wsdl">
                                <ProfileToken>""" + _DEFAULT_PROFILE + """</ProfileToken>
                                <PresetToken>"""+ preset_token + """</PresetToken>
                              </GotoPreset>"""

            xml = ONVIF_SERVICE_ENVELOPE.replace("_service_content_", service_call)

            r = requests.post('http://' + host + _SERVICE_PATH, data=xml, headers={'Content-Type': 'application/soap+xml;charset=UTF8; action="http://www.onvif.org/ver20/ptz/wsdl/' + service})

            if r.status_code != requests.codes.OK:
                _LOGGER.error(__name__ + ": Invalid [move_to_preset] Response [" + str(r.status_code) + "]")

    hass.services.register(DOMAIN, "move_to_direction", move_to_direction)
    hass.services.register(DOMAIN, "move_left", move_left)
    hass.services.register(DOMAIN, "move_right", move_right)
    hass.services.register(DOMAIN, "move_up", move_up)
    hass.services.register(DOMAIN, "move_down", move_down)
    hass.services.register(DOMAIN, "move_origin", move_origin)
    hass.services.register(DOMAIN, "move_privacy", move_privacy)
    hass.services.register(DOMAIN, "move_to_preset", move_to_preset)

    # Return boolean to indicate that initialization was successfully.
    return True
