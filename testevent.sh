curl -v -H "Content-Type: application/json" \
 -H "Ce-Id: 08f4b3bd-59c2-4fd3-85ba-e409174eaa3f" \
 -H "Ce-Source: localhost" \
 -H "Ce-Specversion: 0.3" \
 -H "Ce-Type: test-event" \
 -H "Ce-Originid: 08f4b3bd-59c2-4fd3-85ba-e409174eaa3f" \
 -H "Ce-Subject: 000001" \
 -H "Ce-Time: 2019-12-09T11:02:56.496847+00:00" \
 -H "Accept-Encoding: gzip" \
 -d "{}" -X POST http://localhost:8000