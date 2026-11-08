#!/bin/bash
# Run inside the authenticated IBM Skills Network Cloud IDE.
set -euo pipefail
cd "$(dirname "$0")"
MY_NAMESPACE="$(ibmcloud cr namespaces | awk '/^sn-labs-/ && !/^sn-labsassets/ {print $1; exit}')"
if [ -z "$MY_NAMESPACE" ]; then echo 'No personal SN Labs registry namespace found.' >&2; exit 1; fi
printf 'Using namespace: %s\n' "$MY_NAMESPACE"
IMAGE="us.icr.io/$MY_NAMESPACE/dealership:$(git rev-parse --short HEAD)"
docker build -t "$IMAGE" .
ibmcloud cr login
docker push "$IMAGE"
APP_HOST="nguyenhuy070-8000.theiadockernext-1-labs-prod-theiak8s-4-tor01.proxy.cognitiveclass.ai"
if ! kubectl get secret dealership-config >/dev/null 2>&1; then
APP_SECRET="$(python3 -c 'import secrets; print(secrets.token_urlsafe(48))')"
kubectl create secret generic dealership-config \
  --from-literal=DJANGO_SECRET_KEY="$APP_SECRET" \
  --from-literal=DJANGO_DEBUG=false \
  --from-literal=DJANGO_ALLOWED_HOSTS="localhost,127.0.0.1,$APP_HOST" \
  --from-literal=DJANGO_CSRF_TRUSTED_ORIGINS="https://$APP_HOST" \
  --dry-run=client -o yaml | kubectl apply -f -
unset APP_SECRET
fi
sed "s|us.icr.io/sn-labs-nguyenhuy070/dealership:latest|$IMAGE|" deployment.yaml | kubectl apply -f -
kubectl rollout status deployment/dealership --timeout=300s
printf 'Deployment ready. In a separate terminal run:\nkubectl port-forward deployment.apps/dealership 8000:8000 --address 0.0.0.0\n'
