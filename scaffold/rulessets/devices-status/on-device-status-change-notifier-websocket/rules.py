from datetime import datetime, timedelta

from krules_core.base_functions import \
    CheckPayload, SetSubjectProperty, SetSubjectProperties, SetSubjectExtendedProperty, FlushSubject, \
    OnSubjectPropertyChangedNotIn, OnSubjectPropertyChangedIn, Route, DispatchPolicyConst, SetPayloadProperty, \
    OnSubjectPropertyChangedValue, PyCall, CheckPayloadPropertyValue

from krules_core.base_functions import with_self as _


from krules_core import RuleConst as Const, messages

import requests
import os


## ENABLE RESULTS ##########
from krules_core.providers import results_rx_factory

from base_functions import WebsocketDevicePublishMessage, NotificationEventClass
from krules_env import publish_results_errors

import pprint

# results_rx_factory().subscribe(
#     on_next=pprint.pprint
# )
results_rx_factory().subscribe(
    on_next=publish_results_errors
)

rulename = Const.RULENAME
subscribe_to = Const.SUBSCRIBE_TO
ruledata = Const.RULEDATA
filters = Const.FILTERS
processing = Const.PROCESSING


rulesdata = [

    """
    Notify onboarded (READY)
    """,
    {
        rulename: "on-device-ready-notify-websocket",
        subscribe_to: messages.SUBJECT_PROPERTY_CHANGED,
        ruledata: {
            filters: [
                CheckPayloadPropertyValue("value", "READY"),
            ],
            processing: [
                WebsocketDevicePublishMessage(_(lambda _self: {
                    "device_class": _self.subject.get_ext("deviceclass"),
                    "status": _self.subject.status,
                    "event": "Onboarded",
                    "event_class": NotificationEventClass.CHEERING,
                }))
            ],
        },
    },

    """
    Notify ACTIVE
    """,
    {
        rulename: "on-device-active-notify-websocket",
        subscribe_to: messages.SUBJECT_PROPERTY_CHANGED,
        ruledata: {
            filters: [
                CheckPayloadPropertyValue("value",  "ACTIVE"),
            ],
            processing: [
                WebsocketDevicePublishMessage({
                    "status": "ACTIVE",
                    "event": "Receiving data",
                    "event_class": NotificationEventClass.NORMAL,
                })

            ],
        },
    },

    """
    Notify INACTIVE
    """,
    {
        rulename: "on-device-inactive-notify-websocket",
        subscribe_to: messages.SUBJECT_PROPERTY_CHANGED,
        ruledata: {
            filters: [
                CheckPayloadPropertyValue("value",  "INACTIVE"),
            ],
            processing: [
                WebsocketDevicePublishMessage({
                    "status": "INACTIVE",
                    "event": "No more data receiving",
                    "event_class": NotificationEventClass.WARNING,
                })

            ],
        },
    },

]
