# PTZ-YALL (YCC365 Plus, Y05 and YOOSEE)

This custom component for Home Assistant allows you to use the Pan and Tilt functions of Chinese cameras that do not fully comply with the ONVIF protocol.

This is a fork from original project available at https://github.com/fjramirez1987/PTZ-YCC365

For some reason, the Home Assistant ONVIF integration does not work with cameras that use the YCC365 Plus, Y05 or YOOSEE apps.

When using ONVIF Device Manager application from PC application it is possible to use pan and tilt functions.

Apparently, these cameras do not fully comply with the ONVIF protocol and the Home Assistant integration cannot integrate them at the moment.

This is a solution to use the pan and tilt functions into Home Assistant cards.

In order to use this custom component, capture your camera signal with [motionEye](https://www.home-assistant.io/integrations/motioneye/), or [Generic Camera](https://www.home-assistant.io/integrations/generic/).

## Considerations
1. YCC365 cameras do not require user and password to connect to ONVIF controls
2. Y05 and YOOSEE cameras must have the user and password defined before using ONVIF controls. Check into your camera manual or search on Google how to setup it.
3. YOOSEE cameras do not accept preset positions, just pan and tilt.
4. For YOOSEE cameras this control works based on move steps, the quantity of times it will be required to move until the desired position. The best that could be done so far.
5. **This component does not integrate the video signal from your cameras, only the pan and tilt functions.**

## Setup
You need to install the custom component as usual. Copy the `ptz_camera` folder from this project to your `/config/custom_components/` directory on your Home Assistant.
If using cameras which relies on apps YOOSEE or Y05, you must set your encrypted password and encryption key into the file `/config/custom_components/_init.py`.
You don't need `WireShark`.
The password is based on native Onvif protocol. Here is also the core HA Onvif component [this](https://github.com/home-assistant/core/blob/dev/homeassistant/components/onvif/__init__.py).

1. If using YOOSEE cameras, firstly make sure to activate the option for "NVR connection" into camera settings in the app.
2. Copy them and modify the file `/config/custom_components/ptz_camera/_init.py` to add your camera's information.
3. Add the `ptz_camera:` entry into your `configuration.yaml` file.
4. Restart Home Assistant.
5. Setup your card with controls (see below) and try your camera with pan and tilt controls (no zoom, but full view with webRTC option is possible. See Y05 and YCC365 examples).

## Services
This custom component creates several services with domain ptz_camera. To obtain information about these services you can use “Developer Tools” > Services. It will have detailed information about the arguments to call each service.

## Camera Entity

You can create a camera in the usual way, with [Generic Camera](https://www.home-assistant.io/integrations/generic/). I recommend you to use the [motionEye](https://www.home-assistant.io/integrations/motioneye/) addon and create a mjpeg camera. It is the best setting I have found with a low delay. An example configuration would be:

```yaml
camera:
  - platform: mjpeg
    name: camera_1
    mjpeg_url: http://192.168.1.111:8083
```

## Card with controls
An easy way to use the pan and tilt controls is to overlay the controls on top of a camera image. Replace the IP address in this example with the IP address of your camera.

Example for YOOSEE camera.

```yaml
type: picture-elements
camera_view: live
camera_image: camera.camera_1
elements:
  - type: icon
    icon: mdi:arrow-left-drop-circle
    hold_action:
      action: none
    tap_action:
      action: call-service
      service: ptz_camera.move_left
      service_data:
        host: 192.168.1.244
        camera_type: YOOSEE
        move_time: 0.7
    style:
      bottom: 45%
      left: 5%
      color: white
      opacity: 0.5
      transform: scale(1.5, 1.5)
  - type: icon
    icon: mdi:arrow-right-drop-circle
    hold_action:
      action: none
    tap_action:
      action: call-service
      service: ptz_camera.move_right
      service_data:
        host: 192.168.1.244
        camera_type: YOOSEE
        move_time: 0.7
    style:
      bottom: 45%
      right: 5%
      color: white
      opacity: 0.5
      transform: scale(1.5, 1.5)
  - type: icon
    icon: mdi:arrow-up-drop-circle
    hold_action:
      action: none
    tap_action:
      action: call-service
      service: ptz_camera.move_up
      service_data:
        host: 192.168.1.244
        camera_type: YOOSEE
        move_time: 0.7
    style:
      top: 10%
      left: 46%
      color: white
      opacity: 0.5
      transform: scale(1.5, 1.5)
  - type: icon
    icon: mdi:arrow-down-drop-circle
    hold_action:
      action: none
    tap_action:
      action: call-service
      service: ptz_camera.move_down
      service_data:
        host: 192.168.1.244
        camera_type: YOOSEE
        move_time: 0.7
    style:
      bottom: 10%
      left: 46%
      color: white
      opacity: 0.5
      transform: scale(1.5, 1.5)
  - type: icon
    icon: mdi:home-circle
    hold_action:
      action: none
    tap_action:
      action: call-service
      service: ptz_camera.move_origin
      service_data:
        host: 192.168.1.244
        camera_type: YOOSEE
        move_time: 0.7
        move_steps: 29
    style:
      bottom: 5%
      right: 5%
      color: white
      opacity: 0.5
      transform: scale(1.5, 1.5)
  - type: icon
    icon: mdi:cctv-off
    hold_action:
      action: none
    tap_action:
      action: call-service
      service: ptz_camera.move_privacy
      service_data:
        host: 192.168.1.244
        camera_type: YOOSEE
        move_time: 0.7
    style:
      bottom: 5%
      left: 5%
      color: white
      opacity: 0.5
      transform: scale(1.5, 1.5)
```
Example for Y05 camera:
```yaml
type: picture-elements
camera_view: live
camera_image: camera.camera_1
elements:
  - type: icon
    icon: mdi:arrow-left-drop-circle
    hold_action:
      action: none
    tap_action:
      action: call-service
      service: ptz_camera.move_left
      service_data:
        host: 192.168.1.244
        camera_type: Y05
    style:
      bottom: 45%
      left: 5%
      color: white
      opacity: 0.5
      transform: scale(1.5, 1.5)
  - type: icon
    icon: mdi:arrow-right-drop-circle
    hold_action:
      action: none
    tap_action:
      action: call-service
      service: ptz_camera.move_right
      service_data:
        host: 192.168.1.244
        camera_type: Y05
    style:
      bottom: 45%
      right: 5%
      color: white
      opacity: 0.5
      transform: scale(1.5, 1.5)
  - type: icon
    icon: mdi:arrow-up-drop-circle
    hold_action:
      action: none
    tap_action:
      action: call-service
      service: ptz_camera.move_up
      service_data:
        host: 192.168.1.244
        camera_type: Y05
    style:
      top: 10%
      left: 46%
      color: white
      opacity: 0.5
      transform: scale(1.5, 1.5)
  - type: icon
    icon: mdi:arrow-down-drop-circle
    hold_action:
      action: none
    tap_action:
      action: call-service
      service: ptz_camera.move_down
      service_data:
        host: 192.168.1.244
        camera_type: Y05
    style:
      bottom: 10%
      left: 46%
      color: white
      opacity: 0.5
      transform: scale(1.5, 1.5)
  - type: icon
    icon: mdi:arrow-expand-all
    hold_action:
      action: none
    tap_action:
      action: fire-dom-event
      browser_mod:
        command: popup
        deviceID:
          - this
        title: Camera Full View
        large: true
        card:
          type: custom:webrtc-camera
          muted: true
          url: rtsp://admin:xxxxxx@192.168.1.244:8554/profile0
    style:
      top: 5%
      right: 5%
      color: white
      opacity: 0.5
      transform: scale(1.5, 1.5)
  - type: icon
    icon: mdi:home-circle
    hold_action:
      action: none
    tap_action:
      action: call-service
      service: ptz_camera.move_origin
      service_data:
        host: 192.168.1.244
        camera_type: Y05
        move_time: 0.7
    style:
      bottom: 5%
      right: 5%
      color: white
      opacity: 0.5
      transform: scale(1.5, 1.5)
  - type: icon
    icon: mdi:cctv-off
    hold_action:
      action: none
    tap_action:
      action: call-service
      service: ptz_camera.move_privacy
      service_data:
        host: 192.168.1.244
        camera_type: Y05
    style:
      bottom: 5%
      left: 5%
      color: white
      opacity: 0.5
      transform: scale(1.5, 1.5)
```

Example for YCC365
```yaml
type: picture-elements
camera_view: live
camera_image: camera.salon
elements:
  - type: icon
    icon: 'mdi:arrow-left-drop-circle'
    tap_action:
      action: call-service
      service: ptz_camera.move_left
      service_data:
        host: 192.168.1.244
    style:
      bottom: 45%
      left: 5%
      color: white
      opacity: 0.5
      transform: 'scale(1.5, 1.5)'
  - type: icon
    icon: 'mdi:arrow-right-drop-circle'
    tap_action:
      action: call-service
      service: ptz_camera.move_right
      service_data:
        host: 192.168.1.244
    style:
      bottom: 45%
      right: 5%
      color: white
      opacity: 0.5
      transform: 'scale(1.5, 1.5)'
  - type: icon
    icon: 'mdi:arrow-up-drop-circle'
    tap_action:
      action: call-service
      service: ptz_camera.move_up
      service_data:
        host: 192.168.1.244
    style:
      top: 10%
      left: 46%
      color: white
      opacity: 0.5
      transform: 'scale(1.5, 1.5)'
  - type: icon
    icon: 'mdi:arrow-down-drop-circle'
    tap_action:
      action: call-service
      service: ptz_camera.move_down
      service_data:
        host: 192.168.1.244
    style:
      bottom: 10%
      left: 46%
      color: white
      opacity: 0.5
      transform: 'scale(1.5, 1.5)'
  - type: icon
    icon: 'mdi:arrow-expand-all'
    tap_action:
      action: more-info
    entity: camera.salon
    style:
      top: 5%
      right: 5%
      color: white
      opacity: 0.5
      transform: 'scale(1.5, 1.5)'
```
![](tarjeta.jpg)
