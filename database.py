import sqlite3

def get_connection():
    return sqlite3.connect("map.db", check_same_thread=False)

def init_db():
    conn = get_connection()
    c = conn.cursor()

    # Employees table
    c.execute("""
    CREATE TABLE IF NOT EXISTS employees (
        employee_id INTEGER PRIMARY KEY,
        name TEXT,
        role TEXT,
        level TEXT,
        zone TEXT,
        function TEXT,
        reporting_manager_id INTEGER
    )
    """)

    # Action plans table
    c.execute("""
    CREATE TABLE IF NOT EXISTS action_plans (
        action_plan_id INTEGER PRIMARY KEY AUTOINCREMENT,
        manager_id INTEGER,
        framework_element INTEGER,
        title TEXT,
        description TEXT,
        status TEXT,
        created_date TEXT,
        last_updated TEXT,
        UNIQUE(manager_id, framework_element)
    )
    """)

    # Progress updates table
    c.execute("""
    CREATE TABLE IF NOT EXISTS progress_updates (
        update_id INTEGER PRIMARY KEY AUTOINCREMENT,
        action_plan_id INTEGER,
        updated_by INTEGER,
        update_text TEXT,
        update_date TEXT
    )
    """)

    # Notification log table
    c.execute("""
    CREATE TABLE IF NOT EXISTS notifications (
        notification_id INTEGER PRIMARY KEY AUTOINCREMENT,
        message TEXT,
        created_date TEXT
    )
    """)

    conn.commit()
    conn.close()