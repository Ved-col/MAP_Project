from database import get_connection

def seed_employees():
    conn = get_connection()
    c = conn.cursor()

    c.execute("SELECT COUNT(*) FROM employees")
    if c.fetchone()[0] == 0:
        employees = [
            (1,"Rahul","Manager","Level 2","West","Sales",5),
            (2,"Anita","Manager","Level 2","East","HR",5),
            (3,"Suresh","HRBP","Level 3","West","HR",None),
            (4,"Meena","CEO","Level 5","All","Leadership",None),
            (5,"Arjun","Admin","Level 4","All","HR",None),
            (6,"Karan","Manager","Level 2","North","Operations",5),
            (7,"Priya","Manager","Level 2","South","Finance",5),
            (8,"Ritika","HRBP","Level 3","East","HR",None),
            (9,"Vikram","HRBP","Level 3","North","HR",None)
        ]

        c.executemany("INSERT INTO employees VALUES (?,?,?,?,?,?,?)", employees)
        conn.commit()

    conn.close()