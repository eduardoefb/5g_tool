#!/bin/bash
function generate_imsi(){
   imsi=""
   for i in `seq 1 10`; do
      imsi=${imsi}`shuf -i0-9 -n1`
   done
   echo ${MCC}${MNC}${imsi}
}

function generate_msisdn(){
   da=`shuf -i1-9 -n1`
   db=`shuf -i1-9 -n1`
   dc="9"
   msisdn=""
   for i in `seq 1 8`; do
      msisdn=${msisdn}`shuf -i0-9 -n1`
   done
   echo ${CC}${da}${db}${dc}${msisdn}
}

function usage(){
  cat << EOF
Usage:
${0} <number_of_subscribers>

EOF
  exit 1
}

export MCC="724"
export MNC="17"
export CC=55

if [ -z "${1}" ]; then
  usage
fi

num_imsis=${1}
for ((i=1; i<=${num_imsis}; i++)); do
  imsi=`generate_imsi`
  msisdn=`generate_msisdn`
  curl -X 'POST' \
    'http://localhost:9999/subscriber/' \
    -H 'accept: application/json' \
    -H 'Content-Type: application/json' \
    -d "{
    \"auc\": {
      \"enc_key\": \"465B5CE8B199B49FAA5F0A2EE238A6B0\",
      \"imsi\": \"${imsi}\",
      \"opc_enc_key\": \"E8ED289DEBA952E4283B54E88E6183C0\"
    },
    \"udm_5g_data\": {
      \"udm_imsi\": \"${imsi}\",
      \"udm_msisdn\": \"${msisdn}\",
      \"authentication_data\": {
        \"authentication_method\": \"5G_AKA\"
      },
      \"serving_plmn_id\": {
        \"plmn_id\": \"${MCC}${MNC}\",
        \"provisioned_data\": {
          \"access_and_mobility_subscription_data\": {
            \"gen_public_subscription_ids\": [
              \"msisdn-${msisdn}\"
            ],
            \"nssai\": {
              \"single_nssais\": \"171-121234\"
            },
            \"ue_ambr\": {
              \"ue_ambr_down_link\": \"1 Tbps\",
              \"ue_ambr_up_link\": \"10 Tbps\"
            }
          }
        }
      }
    }
  }" || exit 1

  echo
  curl --http2 http://127.0.0.1:9999/nudr-dr/v1/subscription-data/imsi-${imsi}/authentication-data/authentication-subscription     \
    -H':method: GET'    \
    -H'user-agent: UDM' || exit 1


  echo
  curl --http2 http://127.0.0.1:9999/nudr-dr/v1/subscription-data/imsi-${imsi}/${MCC}${MNC}/provisioned-data/am-data     \
    -H':method: GET'    \
    -H'user-agent: UDM' || exit 1

  echo
  curl --http2 -X 'PUT'   "http://localhost:9999/nudr-dr/v1/subscription-data/imsi-${imsi}/context-data/amf-3gpp-access"   \
    -H 'accept: text/plain'   \
    -H 'user-agent: UDM' \
    -H 'Content-Type: application/json'   \
    -d '{
            "amfInstanceId": "59d96c58-6233-41ee-ae75-47718ba78e48",
            "deregCallbackUri": "http://10.233.64.199:8080/namf-callback/v1/imsi-${imsi}/dereg-notify",
            "guami": {
              "mcc": "724",
              "mnc": "17",
              "amfId": "020040"
            },
            "ratType": "NR"
          }' || exit 1
done
