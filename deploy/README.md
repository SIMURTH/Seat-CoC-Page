# Deployment

## Build and push

```bash
docker build -t <registry>/seat-coc-page:0.1.0 .
docker push <registry>/seat-coc-page:0.1.0
```

## Install (Kubernetes)

```bash
helm upgrade --install seat-coc deploy/helm/seat-coc-page \
  --namespace seat-coc --create-namespace \
  --set image.repository=<registry>/seat-coc-page \
  --set image.tag=0.1.0 \
  --set ingress.enabled=true \
  --set ingress.hosts[0].host=seat-coc.example.internal
```

## Install (OpenShift)

OpenShift uses `Route` instead of `Ingress`, and injects a random UID, so the
chart leaves `runAsUser` unset by default and the image keeps `/app`
group-writable for GID 0.

```bash
helm upgrade --install seat-coc deploy/helm/seat-coc-page \
  --namespace seat-coc \
  --set image.repository=<registry>/seat-coc-page \
  --set image.tag=0.1.0 \
  --set route.enabled=true \
  --set route.host=seat-coc.apps.<cluster-domain>
```

## Notes

- The app stores certificates **in memory**; every pod restart loses data and two
  replicas do not share state. Keep `replicaCount: 1` until a real database is
  added (see the roadmap in the PR description).
- Liveness/readiness probes hit `GET /` (no dedicated health endpoint yet).
- No secrets or environment configuration are required at present.
