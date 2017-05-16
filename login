
set +x

spawn ssh macys@172.17.3.16 "sudo -u postgres psql postgres -h 172.17.3.169<<EOF
\c subscription;
delete from user_entl_notification_history;
delete from user_entl_status_history;
delete from user_entitlement;
\copy user_entitlement FROM EntitlementIds_150K.csv WITH DELIMITER ',' NULL AS ' '
EOF"
expect "assword:"
send "Wv0DhHGqfNq\r"
interact


