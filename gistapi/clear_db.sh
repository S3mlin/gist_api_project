#!/bin/bash
chmod +x /home/sema/gistapi/clear_db.sh
echo "DELETE FROM User; DELETE FROM Link;" | sqlite3 app.db