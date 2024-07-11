# Teams Connex for Home Assistant


## Home Assistant

### Configuring Webhook and template sensors

The following YAML configuration snippet defines a webhook that is used as a trigger for the following template
binary sensors.

```yaml
template:
  - trigger:
      - platform: webhook
        webhook_id: "teams_meeting_update"
        allowed_methods:
          - PUT
        local_only: false
    binary_sensor:
      - name: "Meeting State is muted"
        unique_id: meeting_state_is_muted
        state: "{{ trigger.json['meetingUpdate']['meetingState']['isMuted'] }}"
      - name: "Meeting State is video on"
        unique_id: meeting_state_is_video_on
        state: "{{ trigger.json['meetingUpdate']['meetingState']['isVideoOn'] }}"
      - name: "Meeting State is hand raised"
        unique_id: meeting_state_is_hand_raised
        state: "{{ trigger.json['meetingUpdate']['meetingState']['isHandRaised'] }}"
      - name: "Meeting State is in meeting"
        unique_id: meeting_state_is_in_meeting
        state: "{{ trigger.json['meetingUpdate']['meetingState']['isInMeeting'] }}"
      - name: "Meeting State is recording on"
        unique_id: meeting_state_is_recording_on
        state: "{{ trigger.json['meetingUpdate']['meetingState']['isRecordingOn'] }}"
      - name: "Meeting State is background blurred"
        unique_id: meeting_state_is_background_blurred
        state: "{{ trigger.json['meetingUpdate']['meetingState']['isBackgroundBlurred'] }}"
      - name: "Meeting State is sharing"
        unique_id: meeting_state_is_sharing
        state: "{{ trigger.json['meetingUpdate']['meetingState']['isSharing'] }}"
      - name: "Meeting State has unread messages"
        unique_id: meeting_state_has_unread_messages
        state: "{{ trigger.json['meetingUpdate']['meetingState']['hasUnreadMessages'] }}"
      - name: "Meeting Permissions can toggle mute"
        unique_id: meeting_permissions_can_toggle_mute
        state: "{{ trigger.json['meetingUpdate']['meetingPermissions']['canToggleMute'] }}"
      - name: "Meeting Permissions can toggle video"
        unique_id: meeting_permissions_can_toggle_video
        state: "{{ trigger.json['meetingUpdate']['meetingPermissions']['canToggleVideo'] }}"
      - name: "Meeting Permissions can toggle hand"
        unique_id: meeting_permissions_can_toggle_hand
        state: "{{ trigger.json['meetingUpdate']['meetingPermissions']['canToggleHand'] }}"
      - name: "Meeting Permissions can toggle blur"
        unique_id: meeting_permissions_can_toggle_blur
        state: "{{ trigger.json['meetingUpdate']['meetingPermissions']['canToggleBlur'] }}"
      - name: "Meeting Permissions can leave"
        unique_id: meeting_permissions_can_leave
        state: "{{ trigger.json['meetingUpdate']['meetingPermissions']['canLeave'] }}"
      - name: "Meeting Permissions can react"
        unique_id: meeting_permissions_can_react
        state: "{{ trigger.json['meetingUpdate']['meetingPermissions']['canReact'] }}"
      - name: "Meeting Permissions can toggle share tray"
        unique_id: meeting_permissions_can_toggle_share_tray
        state: "{{ trigger.json['meetingUpdate']['meetingPermissions']['canToggleShareTray'] }}"
      - name: "Meeting Permissions can toggle chat"
        unique_id: meeting_permissions_can_toggle_chat
        state: "{{ trigger.json['meetingUpdate']['meetingPermissions']['canToggleChat'] }}"
      - name: "Meeting Permissions can stop sharing"
        unique_id: meeting_permissions_can_stop_sharing
        state: "{{ trigger.json['meetingUpdate']['meetingPermissions']['canStopSharing'] }}"
```


## Configuring Teams Connex

### Installing the app


### Starting for the first time


### Pairing


### Setting webhook URL

### Autostart

### Log file

