import os

import requests
from krules_core import RuleConst as Const, messages
from krules_core.base_functions import \
    with_self as _, OnSubjectPropertyChanged, Check, CheckPayloadJPMatch

from datetime import datetime, timedelta
import pytz
import jsonpath_rw_ext as jp


from base_functions import Schedule

from krules_core.base_functions import RuleFunctionBase, Route, CheckPayload


## ENABLE RESULTS ##########
from krules_core.providers import results_rx_factory
from krules_env import publish_results_errors, publish_results_all

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


class PostExtApi(RuleFunctionBase):

    def execute(self, url, req_kwargs, on_response):

        resp = requests.post(url, **req_kwargs)
        self.payload["response_status"] = resp.status_code
        self.payload["response_text"] = resp.text
        on_response(self, resp)



rulesdata = [

    """
    Dispose api call
    """,
    {
        rulename: "on-location-changed-notify-postextapi",
        subscribe_to: messages.SUBJECT_PROPERTY_CHANGED,
        ruledata: {
            filters: [
                OnSubjectPropertyChanged("location"),
            ],
            processing: [
                 Route("do-extapi-post", payload=_(lambda _self: {
                     "url": os.environ["EXTAPI_URL"], # https://europe-west3-krules-dev-254113.cloudfunctions.net/store_devices_location
                     "req_kwargs": {
                         "headers": {"x-api-key": os.environ["EXTAPI_X_API_KEY"]},
                         "json": {
                            "device": _self.subject.name,
                            "timestamp": datetime.utcnow().replace(tzinfo=pytz.UTC).isoformat(),
                            "coords": _self.subject.coords,
                            "location": _self.payload["value"],
                         }
                     }
                 }))
            ]
        }
    },

    """
    Do call api
    """,
    {
        rulename: "on-do-extapi-post",
        subscribe_to: "do-extapi-post",
        ruledata: {
            processing: [
                PostExtApi(
                    url=_(lambda _self: _self.payload["url"]),
                    req_kwargs=_(lambda _self: _self.payload["req_kwargs"]),
                    on_response=lambda _self, resp: (
                        resp.raise_for_status(),
                        resp.status_code == 503 and resp.raise_for_status()
                        ## do something when success...,
                        # eg: Route("on-extapi-post.success", payload=resp.json())
                    )
                )
            ]
        }
    },

    """
    Manage exception
    """,
    {
        rulename: "on-do-extapi-post-errors",
        subscribe_to: "{}-errors".format(os.environ["K_SERVICE"]),
        ruledata: {
            filters: [
                CheckPayload(lambda x:
                             x.get("rule_name") == "on-do-extapi-post" and
                             jp.match1("$.processing[*].exception", x) == "requests.exceptions.HTTPError" and
                             jp.match1("$.processing[*].exc_extra_info.response_code", x) == 503)
            ],
            processing: [
                Schedule(message="do-extapi-post",
                         payload=_(lambda _self: _self.payload["payload"]),
                         when=_(lambda _: (datetime.now()+timedelta(seconds=30)).isoformat())),
            ]
        }
    }


]
