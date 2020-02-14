import os
from datetime import datetime, timedelta

import requests
from dateutil.parser import parse
from krules_core import RuleConst as Const, messages
from krules_core.base_functions import \
    SetSubjectProperty, Route, DispatchPolicyConst, PyCall, with_self as _, CheckPayloadPropertyValue, \
    CheckPayloadPropertyValueNotIn, CheckPayloadPropertyValueIn, Check
## ENABLE RESULTS ##########
from krules_core.providers import results_rx_factory

from base_functions import Schedule
from krules_env import publish_results_all

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
        rulename: "on-temp-status-back-to-normal",
        subscribe_to: messages.SUBJECT_PROPERTY_CHANGED,
        ruledata: {
            filters: [
                CheckPayloadPropertyValue("value", "NORMAL"),
                CheckPayloadPropertyValueNotIn("old_value", (None,))  # skip initial state
            ],
            processing: [
                Route(message="temp-status-back-to-normal",
                      dispatch_policy=DispatchPolicyConst.DIRECT),
                SetSubjectProperty("m_lastTempStatusChanged", _(lambda _: datetime.now().isoformat()))

            ],
        },
    },

    """
    Status COLD or OVERHEATED schedule a new check
    """,
    {
        rulename: "on-temp-status-bad",
        subscribe_to: messages.SUBJECT_PROPERTY_CHANGED,
        ruledata: {
            filters: [
                CheckPayloadPropertyValueIn("value",  ("COLD", "OVERHEATED")),
            ],
            processing: [
                Route(message="temp-status-bad", payload=_(lambda _self: {
                    "tempc": str(_self.subject.tempc),
                    "status": _self.payload.get("value")
                }), dispatch_policy=DispatchPolicyConst.DIRECT),
                SetSubjectProperty("m_lastTempStatusChanged", _(lambda _: datetime.now().isoformat())),
                Schedule(message="temp-status-recheck",
                         payload=_(lambda _self: {"old_value": _self.payload["value"]}),
                         when=_(lambda _: (datetime.now()+timedelta(seconds=30)).isoformat())),
            ],
        },
    },

    """
    Recheck
    """,
    {
        rulename: "on-temp-status-recheck",
        subscribe_to: "temp-status-recheck",
        ruledata: {
            filters: [
                Check(
                    _(lambda _self: _self.payload.get("old_value") == _self.subject.temp_status)
                )
            ],
            processing: [
                Route(message="temp-status-still-bad", payload=_(lambda _self: {
                    "status": _self.payload.get("old_value"),
                    "seconds": (datetime.now() - parse(_self.subject.m_lastTempStatusChanged)).seconds
                }), dispatch_policy=DispatchPolicyConst.DIRECT),
                Schedule(message="temp-status-recheck",
                         payload=_(lambda _self: {"old_value": _self.payload["old_value"]}),
                         when=_(lambda _: (datetime.now()+timedelta(seconds=15)).isoformat())),
            ],
        },
    },

]
