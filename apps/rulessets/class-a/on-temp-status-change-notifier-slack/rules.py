from datetime import datetime, timedelta

from dateutil.parser import parse

from base_functions import Schedule, WebsocketDevicePublishMessage, NotificationEventClass
from krules_core.base_functions import \
    CheckPayload, SetSubjectProperty, SetSubjectProperties, SetSubjectExtendedProperty, FlushSubject, \
    OnSubjectPropertyChangedNotIn, OnSubjectPropertyChangedIn, Route, DispatchPolicyConst, SetPayloadProperty, \
    OnSubjectPropertyChangedValue, PyCall, with_subject, with_self as _, CheckPayloadPropertyValue, \
    CheckPayloadPropertyValueNotIn, CheckPayloadPropertyValueIn, Check, OnSubjectPropertyChanged

from krules_core import RuleConst as Const, messages

import requests
import os


## ENABLE RESULTS ##########
from krules_core.providers import results_rx_factory
from krules_env import publish_results_all, publish_results_errors

import pprint

# results_rx_factory().subscribe(
#     on_next=pprint.pprint
# )
results_rx_factory().subscribe(
    on_next=publish_results_all,
)

rulename = Const.RULENAME
subscribe_to = Const.SUBSCRIBE_TO
ruledata = Const.RULEDATA
filters = Const.FILTERS
processing = Const.PROCESSING
rulesdata = [


    """
    On status NORMAL notify
    """,
    {
        rulename: "on-temp-status-back-to-normal-websocket-notifier",
        subscribe_to: "temp-status-back-to-normal",
        ruledata: {
            processing: [
                PyCall(
                    requests.post,
                    os.environ["MATTERMOST_CHANNEL_URL"],
                    json=_(lambda _self: {
                        "text": " :sunglasses:  device *{}* temp status back to normal! ".format(_self.subject.name)
                    })
                ),
            ],
        },
    },

    """
    Status COLD or OVERHEATED
    """,
    {
        rulename: "on-temp-status-bad-websocket-notifier",
        subscribe_to: "temp-status-bad",
        ruledata: {
            processing: [
                PyCall(
                    requests.post,
                    os.environ["MATTERMOST_CHANNEL_URL"],
                    json=_(lambda _self: {
                        "text": ":scream:  device *{}* is *{}* ({}°C)".format(
                            _self.subject.name, _self.payload.get("status"), _self.payload.get("tempc")
                        )
                    })
                ),
           ],
        },
    },

    """
    Recheck
    """,
    {
        rulename: "on-temp-status-recheck-websocket-notifier",
        subscribe_to: "temp-status-still-bad",
        ruledata: {
            processing: [
                PyCall(
                    requests.post,
                    os.environ["MATTERMOST_CHANNEL_URL"],
                    json=_(lambda _self: {
                        "text": ":neutral_face: device *{}* is still *{}* from {} secs".format(
                            _self.subject.name,
                            _self.payload.get("status"),
                            _self.payload.get("seconds")
                        )
                    })
                ),
            ],
        },
    },

]
