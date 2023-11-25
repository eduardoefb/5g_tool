### Requirements:
- podman;
- linux (as always);
- python3.

### To run:
Start mongodb, download the needed modules and start application:
```shell
bash run.sh
```

To manually start the application:
```shell
python3 -m venv env
source env/bin/activate
pip install -r requirements.txt
hypercorn main:app --bind 0.0.0.0:9090 --workers 4
```


### Creating subscribers:
To create a subscriber, use the following sintax:
```shell
  curl -X 'POST' \
    'http://localhost:9090/subscriber/' \
    -H 'accept: application/json' \
    -H 'Content-Type: application/json' \
    -d '{
    "auc": {
      "enc_key": "465B5CE8B199B49FAA5F0A2EE238A6B0",
      "imsi": "724170000000001",
      "opc_enc_key": "E8ED289DEBA952E4283B54E88E6183C0"
    },
    "udm_5g_data": {
      "udm_imsi": "724170000000001",
      "udm_msisdn": "5521998110001",
      "authentication_data": {
        "authentication_method": "5G_AKA"
      },
      "serving_plmn_id": {
        "plmn_id": "72417",
        "provisioned_data": {
          "access_and_mobility_subscription_data": {
            "gen_public_subscription_ids": [
              "msisdn-5521998110001"
            ],
            "nssai": {
              "single_nssais": "171-121234"
            },
            "ue_ambr": {
              "ue_ambr_down_link": "1 Tbps",
              "ue_ambr_up_link": "10 Tbps"
            }
          }
        }
      }
    }
  }'

```

### UDR APIs:
Query subscriber authentication:
Using curl:
```shell
curl --http2 http://127.0.0.1:9090/nudr-dr/v1/subscription-data/imsi-724170000000001/authentication-data/authentication-subscription     \
  -H':method: GET'    \
  -H'user-agent: UDM'

curl --http2 http://127.0.0.1:9090/nudr-dr/v1/subscription-data/imsi-724170000000001/72417/provisioned-data/am-data     \
  -H':method: GET'    \
  -H'user-agent: UDM'

curl --http2 -X 'PUT'   'http://localhost:9090/nudr-dr/v1/subscription-data/imsi-724170000000001/context-data/amf-3gpp-access'   \
   -H 'accept: text/plain'   \
   -H 'user-agent: UDM' \
   -H 'Content-Type: application/json'   \
   -d '{
          "amfInstanceId": "59d96c58-6233-41ee-ae75-47718ba78e48",
          "deregCallbackUri": "http://10.233.64.199:8080/namf-callback/v1/imsi-724170000000001/dereg-notify",
          "guami": {
            "mcc": "724",
            "mnc": "17",
            "amfId": "020040"
          },
          "ratType": "NR"
        }'


```

Using nghttp2:
```shell
nghttp -v http://127.0.0.1:9090/nudr-dr/v1/subscription-data/imsi-724170000000001/authentication-data/authentication-subscription     \
	-H':method: GET'    \
	-H'user-agent: UDM'

nghttp -v http://127.0.0.1:9090/nudr-dr/v1/subscription-data/imsi-724170000000001/72417/provisioned-data/am-data     \
	-H':method: GET'    \
	-H'user-agent: UDM'  

```

### Mongodb commands:
To list the content:
```shell
podman exec -it mongodb bash
mongosh --host localhost -u mongoadmin -p secret --authenticationDatabase admin
show dbs;
use db01;
show collections;
db.subscriber.find();
```
