#!/bin/bash

  curl -X 'POST' \
    'http://localhost:9999/subscriber/' \
    -H 'accept: application/json' \
    -H 'Content-Type: application/json' \
    -d '{
    "auc": {
      "enc_key": "465B5CE8B199B49FAA5F0A2EE238A6B0",
      "imsi": "724170000000010",
      "opc_enc_key": "E8ED289DEBA952E4283B54E88E6183C0"
    },
    "udm_5g_data": {
      "udm_imsi": "724170000000010",
      "udm_msisdn": "5521998110010",
      "authentication_data": {
        "authentication_method": "5G_AKA"
      },
      "serving_plmn_id": {
        "plmn_id": "72417",
        "provisioned_data": {
          "access_and_mobility_subscription_data": {
            "gen_public_subscription_ids": [
              "msisdn-5521998110010"
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


  curl --http2 http://127.0.0.1:9999/nudr-dr/v1/subscription-data/imsi-724170000000010/authentication-data/authentication-subscription     \
  -H':method: GET'    \
  -H'user-agent: UDM'
