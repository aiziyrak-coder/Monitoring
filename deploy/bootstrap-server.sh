#!/usr/bin/env bash
# Bir marta root sifatida serverda ishga tushiring (SSH kalit bilan).
# Masalan: bash deploy/bootstrap-server.sh
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

install -m 644 "$ROOT/deploy/systemd/clinicmonitoring-backend.service" /etc/systemd/system/clinicmonitoring-backend.service
install -m 644 "$ROOT/deploy/nginx/clinicmonitoring-ziyrak.conf" /etc/nginx/sites-available/clinicmonitoring-ziyrak.conf
ln -sf /etc/nginx/sites-available/clinicmonitoring-ziyrak.conf /etc/nginx/sites-enabled/clinicmonitoring-ziyrak.conf

if [[ ! -f /etc/clinicmonitoring.env ]]; then
  install -m 600 "$ROOT/deploy/clinicmonitoring.env.example" /etc/clinicmonitoring.env
  echo ">>> /etc/clinicmonitoring.env yaratildi. DJANGO_SECRET_KEY ni o'zgartiring!"
fi

systemctl daemon-reload
systemctl enable clinicmonitoring-backend
nginx -t
systemctl reload nginx

echo "Bootstrap yakunlandi. certbot va DNS tekshiring (DEPLOY.md)."
