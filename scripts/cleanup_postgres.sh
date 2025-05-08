#!/bin/bash
docker exec -i cybersec_postgres psql -U devlinux -d arista-cyber <<EOF
DELETE FROM logs_network_event WHERE waktu < NOW() - INTERVAL '30 days';
EOF
