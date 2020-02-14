import os

import requests
from geopy.geocoders import Nominatim
from krules_core import RuleConst as Const, messages
from krules_core.base_functions import \
    PyCall, with_self as _, OnSubjectPropertyChanged, CheckPayloadPropertyValueNotIn, PayloadConst, Check

geolocator = Nominatim(user_agent="KRules", timeout=10)

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
    Location changed (changed from a known location)
    """,
    {
        rulename: "on-location-changed-moving-notify-slack",
        subscribe_to: messages.SUBJECT_PROPERTY_CHANGED,
        ruledata: {
            filters: [
                OnSubjectPropertyChanged("location"),
                Check(_(lambda _self: _self.payload["old_value"] is not None))  # moving
            ],
            processing: [
                PyCall(
                    requests.post,
                    os.environ["MATTERMOST_CHANNEL_URL"],
                    json=_(lambda _self: {
                        "text": ":rocket: device *{}* moved to {}".format(
                            _self.subject.name, _self.payload.get("value")
                        )
                    })
                ),
            ]
        }
    },

    """
    Location changed (first location)
    """,
    {
        rulename: "on-location-changed-starting-notify-slack",
        subscribe_to: messages.SUBJECT_PROPERTY_CHANGED,
        ruledata: {
            filters: [
                OnSubjectPropertyChanged("location"),
                Check(_(lambda _self: _self.payload["old_value"] is None))
            ],
            processing: [
                PyCall(
                    requests.post,
                    os.environ["MATTERMOST_CHANNEL_URL"],
                    json=_(lambda _self: {
                        "text": ":triangular_flag_on_post: device *{}* located in {}".format(
                            _self.subject.name, _self.payload.get("value")
                        )
                    })
                ),
            ]
        }
    },

]
