#!/bin/bash
find /media/it/01DBBF1A4D698EE0/log_data/ -type f -mtime +30 -exec rm {} \;
