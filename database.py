import sqlite3
import os

DB_NAME = "database/fmea.db"


def get_connection():
    os.makedirs("database", exist_ok=True)

    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def create_tables():

    conn = get_connection()
    cursor = conn.cursor()

    # ==========================================
    # PROJECTS
    # ==========================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_name TEXT NOT NULL,
            product_name TEXT,
            customer TEXT,
            project_number TEXT,
            created_date TEXT
        )
    """)

    # ==========================================
    # FUNCTIONAL ANALYSIS
    # ==========================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS functional_analysis (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER,
            function TEXT,
            requirement TEXT,
            FOREIGN KEY (project_id) REFERENCES projects(id)
        )
    """)

    # ==========================================
    # BOUNDARY DIAGRAM
    # ==========================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS boundary_diagram (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER,
            external_element TEXT NOT NULL,
            interaction TEXT,
            direction TEXT,
            description TEXT,
            FOREIGN KEY (project_id) REFERENCES projects(id)
        )
    """)

    # ==========================================
    # PRODUCT STRUCTURE
    # ==========================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS product_structure (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            parent_id INTEGER,
            component_name TEXT NOT NULL,
            component_type TEXT,
            label TEXT,
            part_number TEXT,
            level INTEGER DEFAULT 0,
            description TEXT,
            FOREIGN KEY (project_id) REFERENCES projects(id),
            FOREIGN KEY (parent_id) REFERENCES product_structure(id)
        )
    """)

    # ==========================================
    # KEY CHARACTERISTICS
    # ==========================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS key_characteristics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER,
            component_id INTEGER,
            characteristic TEXT,
            specification TEXT,
            tolerance TEXT,
            severity INTEGER,
            responsibility TEXT,
            FOREIGN KEY (project_id) REFERENCES projects(id),
            FOREIGN KEY (component_id) REFERENCES product_structure(id)
        )
    """)

    # ==========================================
    # FUNCTION TO STRUCTURE LINK
    # ==========================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS functional_links (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER,
            function_id INTEGER,
            component_id INTEGER,
            requirement TEXT,
            FOREIGN KEY (project_id) REFERENCES projects(id),
            FOREIGN KEY (function_id) REFERENCES functional_analysis(id),
            FOREIGN KEY (component_id) REFERENCES product_structure(id)
        )
    """)

    # ==========================================
    # DFMEA
    # ==========================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS dfmea (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER,
            component_id INTEGER,
            function TEXT,
            failure_mode TEXT,
            failure_effect TEXT,
            severity INTEGER,
            cause TEXT,
            occurrence INTEGER,
            prevention_control TEXT,
            detection_control TEXT,
            detection INTEGER,
            rpn INTEGER,
            recommended_action TEXT,
            responsibility TEXT,
            target_date TEXT,
            action_status TEXT,
            FOREIGN KEY (project_id) REFERENCES projects(id),
            FOREIGN KEY (component_id) REFERENCES product_structure(id)
        )
    """)

    # ==========================================
    # PFMEA
    # ==========================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pfmea (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER,
            component_id INTEGER,
            process_step TEXT,
            process_function TEXT,
            failure_mode TEXT,
            failure_effect TEXT,
            severity INTEGER,
            cause TEXT,
            occurrence INTEGER,
            prevention_control TEXT,
            detection_control TEXT,
            detection INTEGER,
            rpn INTEGER,
            recommended_action TEXT,
            responsibility TEXT,
            target_date TEXT,
            action_status TEXT,
            FOREIGN KEY (project_id) REFERENCES projects(id),
            FOREIGN KEY (component_id) REFERENCES product_structure(id)
        )
    """)

    # ==========================================
    # CONTROL PLAN
    # ==========================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS control_plan (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER,
            component_id INTEGER,
            process_step TEXT,
            characteristic TEXT,
            specification TEXT,
            control_method TEXT,
            measurement_method TEXT,
            sample_size TEXT,
            frequency TEXT,
            responsibility TEXT,
            reaction_plan TEXT,
            FOREIGN KEY (project_id) REFERENCES projects(id),
            FOREIGN KEY (component_id) REFERENCES product_structure(id)
        )
    """)

    conn.commit()
    conn.close()


if __name__ == "__main__":
    create_tables()
    print("Database tables created successfully.")