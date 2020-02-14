from datetime import datetime, timedelta

from krules_core.base_functions import \
    CheckPayload, SetSubjectProperty, SetSubjectProperties, SetSubjectExtendedProperty, FlushSubject, \
    OnSubjectPropertyChangedNotIn, OnSubjectPropertyChangedIn, Route, DispatchPolicyConst, SetPayloadProperty, \
    OnSubjectPropertyChangedValue, PyCall, with_subject, with_self as _, CheckPayloadPropertyValue, Check, \
    OnSubjectPropertyChanged, RuleFunctionBase

from krules_core import RuleConst as Const, messages

from geopy import distance
from geopy.geocoders import Nominatim

geolocator = Nominatim(user_agent="KRules", timeout=10)


## ENABLE RESULTS ##########
from krules_core.providers import results_rx_factory

from krules_env import publish_results_errors, publish_results_all, publish_results_filtered

import pprint

# results_rx_factory().subscribe(
#     on_next=pprint.pprint
# )
results_rx_factory().subscribe(
    on_next=publish_results_errors,
)
# results_rx_factory().subscribe(
#     on_next=lambda result: publish_results_filtered(result, "$.processed", True)
# )

rulename = Const.RULENAME
subscribe_to = Const.SUBSCRIBE_TO
ruledata = Const.RULEDATA
filters = Const.FILTERS
processing = Const.PROCESSING


class SetLocationProperties(RuleFunctionBase):

    def execute(self):

        coords = (float(self.payload["data"]["lat"]), float(self.payload["data"]["lng"]))
        self.subject.coords = str(coords)
        # ensure ref point is already set
        if "m_refCoords" not in self.subject:
            self.subject.m_refCoords = str(coords)
        # set location if not already set or if tolerance is exceeded
        if "location" not in self.subject or distance.distance(
                self.subject.m_refCoords, coords
            ).meters > float(self.subject.tolerance):
            self.subject.location = geolocator.reverse("{}, {}".format(coords[0], coords[1])).address
            self.subject.m_refCoords = coords


rulesdata = [

    """
    Always store coords in subject, Initialize starting point too if needed
    """,
    {
        rulename: "on-data-received-store-coords",
        subscribe_to: "data-received",
        ruledata: {
            processing: [
                SetLocationProperties()
                #     # store coords in payload for later use
                #     SetPayloadProperty("coords", _(lambda _self:
                #                                    (float(_self.payload["data"]["lat"]),
                #                                     float(_self.payload["data"]["lng"]))
                #                                    )),
                #     # always store received coords
                #     SetSubjectProperty("coords", _(lambda _self: str(_self.payload["coords"]))),
                #     # set starting point if not already set
                #     SetSubjectProperty("m_refCoords",
                #                        condition=_(lambda _self: "m_refCoords" not in _self.subject),
                #                        value=_(lambda _self: str(_self.payload["coords"]))),
                #     # set location if not already set or if tolerance is exceeded
                #     SetSubjectProperty("location",
                #                        condition=_(lambda _self:
                #                             "location" not in _self.subject or
                #                                 distance.distance(
                #                                     _self.subject.m_refCoords, _self.coords
                #                                 ).meters > float(_self.subject.tolerance)
                #                        ),
                #                        value=_(lambda _self: geolocator.reverse("{}, {}".format(
                #                            _self.payload["coords"][0],
                #                            _self.payload["coords"][1]))))
            ]
        }
    },

]
