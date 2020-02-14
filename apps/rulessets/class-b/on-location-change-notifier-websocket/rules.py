
from krules_core import RuleConst as Const, messages
from krules_core.base_functions import \
    with_self as _, OnSubjectPropertyChanged, Check

from base_functions import WebsocketDevicePublishMessage, NotificationEventClass


## ENABLE RESULTS ##########
from krules_core.providers import results_rx_factory
from krules_env import publish_results_errors

# results_rx_factory().subscribe(
#     on_next=pprint.pprint
# )
results_rx_factory().subscribe(
    on_next=publish_results_errors,
)

rulename = Const.RULENAME
subscribe_to = Const.SUBSCRIBE_TO
ruledata = Const.RULEDATA
filters = Const.FILTERS
processing = Const.PROCESSING


rulesdata = [

    """
    Send all coords variations
    """,
    {
        rulename: "on-coords-changed-notify-websocket",
        subscribe_to: messages.SUBJECT_PROPERTY_CHANGED,
        ruledata: {
            filters: [
                OnSubjectPropertyChanged("coords"),
            ],
            processing: [
                WebsocketDevicePublishMessage(_(lambda _self: {
                    "value": _self.payload["value"],
                })),
            ]
        }
    },

    """
    Send location (cheering)
    """,
    {
        rulename: "on-location-changed-notify-websocket-cheering",
        subscribe_to: messages.SUBJECT_PROPERTY_CHANGED,
        ruledata: {
            filters: [
                OnSubjectPropertyChanged("location"),
                Check(_(lambda _self: _self.payload["old_value"] is None))
            ],
            processing: [
                WebsocketDevicePublishMessage(_(lambda _self: {
                    "event": _self.payload["value"],
                    "event_class": NotificationEventClass.CHEERING,
                })),
            ]
        }
    },

    """
    Send location (normal)
    """,
    {
        rulename: "on-location-changed-notify-websocket-normal",
        subscribe_to: messages.SUBJECT_PROPERTY_CHANGED,
        ruledata: {
            filters: [
                OnSubjectPropertyChanged("location"),
                Check(_(lambda _self: _self.payload["old_value"] is not None))
            ],
            processing: [
                WebsocketDevicePublishMessage(_(lambda _self: {
                    "event": _self.payload["value"],
                    "event_class": NotificationEventClass.NORMAL,
                })),
            ]
        }
    },
]
