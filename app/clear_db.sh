#!/bin/bash
chmod +x /home/sema/gist_api_project/app/clear_db.sh
cd app/
echo "DELETE FROM User; DELETE FROM Link;" | sqlite3 app.db