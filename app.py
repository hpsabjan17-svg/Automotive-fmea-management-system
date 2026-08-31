from flask import Flask, render_template, request, redirect, url_for
from openpyxl import Workbook
from flask import send_file
from io import BytesIO
import sqlite3
import os

app = Flask(__name__)

DATABASE = os.path.join("database", "fmea.db")


# =========================================================
# DATABASE CONNECTION
# =========================================================

def get_db():
    os.makedirs("database", exist_ok=True)

    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row

    return conn


# =========================================================
# DATABASE SETUP
# =========================================================

def setup_database():

    conn = get_db()
    cursor = conn.cursor()

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

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS functional_analysis (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER,
            function TEXT,
            requirement TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS boundary_diagram (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER,
            external_element TEXT,
            interaction TEXT,
            direction TEXT,
            description TEXT
        )
    """)

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
            description TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS key_characteristics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER,
            component_id INTEGER,
            characteristic TEXT,
            specification TEXT,
            tolerance TEXT,
            severity INTEGER,
            responsibility TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS functional_links (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER,
            function_id INTEGER,
            component_id INTEGER,
            requirement TEXT
        )
    """)

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
            action_status TEXT
        )
    """)

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
            action_status TEXT
        )
    """)

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
            reaction_plan TEXT
        )
    """)

    conn.commit()
    conn.close()


# =========================================================
# DASHBOARD
# =========================================================

@app.route("/")
def dashboard():

    conn = get_db()

    projects = conn.execute("""
        SELECT *
        FROM projects
        ORDER BY id DESC
    """).fetchall()

    conn.close()

    return render_template(
        "dashboard.html",
        projects=projects
    )


# =========================================================
# PROJECT DETAILS
# =========================================================

@app.route("/project", methods=["GET", "POST"])
def project():

    if request.method == "POST":

        project_name = request.form.get("project_name", "").strip()
        product_name = request.form.get("product_name", "").strip()
        customer = request.form.get("customer", "").strip()
        project_number = request.form.get("project_number", "").strip()
        created_date = request.form.get("created_date", "").strip()

        if project_name:

            conn = get_db()

            conn.execute("""
                INSERT INTO projects
                (
                    project_name,
                    product_name,
                    customer,
                    project_number,
                    created_date
                )
                VALUES (?, ?, ?, ?, ?)
            """, (
                project_name,
                product_name,
                customer,
                project_number,
                created_date
            ))

            conn.commit()
            conn.close()

        return redirect(url_for("project"))

    conn = get_db()

    projects = conn.execute("""
        SELECT *
        FROM projects
        ORDER BY id DESC
    """).fetchall()

    conn.close()

    return render_template(
        "project.html",
        projects=projects
    )


# =========================================================
# FUNCTIONAL ANALYSIS
# =========================================================

@app.route("/functional-analysis", methods=["GET", "POST"])
def functional_analysis():

    conn = get_db()

    if request.method == "POST":

        project_id = request.form.get("project_id", "")
        function = request.form.get("function", "").strip()
        requirement = request.form.get("requirement", "").strip()

        if project_id and function:

            conn.execute("""
                INSERT INTO functional_analysis
                (
                    project_id,
                    function,
                    requirement
                )
                VALUES (?, ?, ?)
            """, (
                project_id,
                function,
                requirement
            ))

            conn.commit()

    projects = conn.execute("""
        SELECT *
        FROM projects
        ORDER BY project_name
    """).fetchall()

    records = conn.execute("""
        SELECT
            fa.id,
            fa.project_id,
            p.project_name,
            fa.function,
            fa.requirement
        FROM functional_analysis AS fa
        LEFT JOIN projects AS p
            ON fa.project_id = p.id
        ORDER BY fa.id DESC
    """).fetchall()

    conn.close()

    return render_template(
        "functional_analysis.html",
        projects=projects,
        records=records
    )


# =========================================================
# BOUNDARY DIAGRAM
# =========================================================

@app.route("/boundary-diagram", methods=["GET", "POST"])
def boundary_diagram():

    conn = get_db()

    if request.method == "POST":

        project_id = request.form.get("project_id", "")
        external_element = request.form.get(
            "external_element", ""
        ).strip()

        interaction = request.form.get(
            "interaction", ""
        ).strip()

        direction = request.form.get(
            "direction", ""
        ).strip()

        description = request.form.get(
            "description", ""
        ).strip()

        if project_id and external_element:

            conn.execute("""
                INSERT INTO boundary_diagram
                (
                    project_id,
                    external_element,
                    interaction,
                    direction,
                    description
                )
                VALUES (?, ?, ?, ?, ?)
            """, (
                project_id,
                external_element,
                interaction,
                direction,
                description
            ))

            conn.commit()

    projects = conn.execute("""
        SELECT *
        FROM projects
        ORDER BY project_name
    """).fetchall()

    boundaries = conn.execute("""
        SELECT
            bd.id,
            bd.project_id,
            bd.external_element,
            bd.interaction,
            bd.direction,
            bd.description,
            p.project_name
        FROM boundary_diagram AS bd
        LEFT JOIN projects AS p
            ON bd.project_id = p.id
        ORDER BY bd.id DESC
    """).fetchall()

    conn.close()

    return render_template(
        "boundary_diagram.html",
        projects=projects,
        boundaries=boundaries
    )


# =========================================================
# PRODUCT STRUCTURE
# =========================================================

@app.route("/product-structure", methods=["GET", "POST"])
def product_structure():

    conn = get_db()

    selected_project_id = request.args.get(
        "project_id",
        ""
    )

    if request.method == "POST":

        project_id = request.form.get(
            "project_id",
            ""
        )

        parent_id = request.form.get(
            "parent_id",
            ""
        )

        component_name = request.form.get(
            "component_name",
            ""
        ).strip()

        component_type = request.form.get(
            "component_type",
            ""
        ).strip()

        label = request.form.get(
            "label",
            ""
        ).strip()

        part_number = request.form.get(
            "part_number",
            ""
        ).strip()

        level = request.form.get(
            "level",
            "0"
        ).strip()

        description = request.form.get(
            "description",
            ""
        ).strip()

        if parent_id == "":
            parent_id = None

        if project_id and component_name:

            conn.execute("""
                INSERT INTO product_structure
                (
                    project_id,
                    parent_id,
                    component_name,
                    component_type,
                    label,
                    part_number,
                    level,
                    description
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                project_id,
                parent_id,
                component_name,
                component_type,
                label,
                part_number,
                level,
                description
            ))

            conn.commit()
            conn.close()

            return redirect(
                url_for(
                    "product_structure",
                    project_id=project_id
                )
            )

    projects = conn.execute("""
        SELECT
            id,
            project_name,
            product_name
        FROM projects
        ORDER BY id DESC
    """).fetchall()

    if selected_project_id:

        components = conn.execute("""
            SELECT
                id,
                project_id,
                parent_id,
                component_name,
                component_type,
                label,
                part_number,
                level,
                description
            FROM product_structure
            WHERE project_id = ?
            ORDER BY level, id
        """, (
            selected_project_id,
        )).fetchall()

    else:

        components = []

    conn.close()

    return render_template(
        "product_structure.html",
        projects=projects,
        components=components,
        selected_project_id=selected_project_id
    )


# =========================================================
# KEY CHARACTERISTICS
# =========================================================

@app.route("/key-characteristics", methods=["GET", "POST"])
def key_characteristics():

    conn = get_db()

    selected_project_id = request.args.get(
        "project_id",
        ""
    )

    if request.method == "POST":

        project_id = request.form.get(
            "project_id",
            ""
        )

        component_id = request.form.get(
            "component_id",
            ""
        )

        characteristic = request.form.get(
            "characteristic",
            ""
        ).strip()

        specification = request.form.get(
            "specification",
            ""
        ).strip()

        tolerance = request.form.get(
            "tolerance",
            ""
        ).strip()

        severity = request.form.get(
            "severity",
            "1"
        )

        responsibility = request.form.get(
            "responsibility",
            ""
        ).strip()

        if project_id and component_id and characteristic:

            conn.execute("""
                INSERT INTO key_characteristics
                (
                    project_id,
                    component_id,
                    characteristic,
                    specification,
                    tolerance,
                    severity,
                    responsibility
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                project_id,
                component_id,
                characteristic,
                specification,
                tolerance,
                severity,
                responsibility
            ))

            conn.commit()
            conn.close()

            return redirect(
                url_for(
                    "key_characteristics",
                    project_id=project_id
                )
            )

    projects = conn.execute("""
        SELECT
            id,
            project_name,
            product_name
        FROM projects
        ORDER BY id DESC
    """).fetchall()

    if selected_project_id:

        components = conn.execute("""
            SELECT
                id,
                project_id,
                component_name,
                component_type,
                label,
                part_number,
                level
            FROM product_structure
            WHERE project_id = ?
            ORDER BY level, id
        """, (
            selected_project_id,
        )).fetchall()

    else:

        components = []

    records = conn.execute("""
        SELECT
            kc.id,
            kc.project_id,
            kc.component_id,
            p.project_name,
            ps.component_name,
            kc.characteristic,
            kc.specification,
            kc.tolerance,
            kc.severity,
            kc.responsibility
        FROM key_characteristics AS kc

        LEFT JOIN projects AS p
            ON kc.project_id = p.id

        LEFT JOIN product_structure AS ps
            ON kc.component_id = ps.id

        ORDER BY kc.id DESC
    """).fetchall()

    conn.close()

    return render_template(
        "key_characteristics.html",
        projects=projects,
        components=components,
        records=records,
        selected_project_id=selected_project_id
    )


# =========================================================
# FUNCTIONAL LINKING
# =========================================================

@app.route("/functional-links", methods=["GET", "POST"])
def functional_links():

    conn = get_db()

    selected_project_id = request.args.get(
        "project_id",
        ""
    )

    if request.method == "POST":

        project_id = request.form.get(
            "project_id",
            ""
        )

        function_id = request.form.get(
            "function_id",
            ""
        )

        component_id = request.form.get(
            "component_id",
            ""
        )

        requirement = request.form.get(
            "requirement",
            ""
        ).strip()

        if project_id and function_id and component_id and requirement:

            conn.execute("""
                INSERT INTO functional_links
                (
                    project_id,
                    function_id,
                    component_id,
                    requirement
                )
                VALUES (?, ?, ?, ?)
            """, (
                project_id,
                function_id,
                component_id,
                requirement
            ))

            conn.commit()
            conn.close()

            return redirect(
                url_for(
                    "functional_links",
                    project_id=project_id
                )
            )

    projects = conn.execute("""
        SELECT
            id,
            project_name,
            product_name
        FROM projects
        ORDER BY id DESC
    """).fetchall()

    if selected_project_id:

        functions = conn.execute("""
            SELECT
                id,
                project_id,
                function,
                requirement
            FROM functional_analysis
            WHERE project_id = ?
            ORDER BY id ASC
        """, (
            selected_project_id,
        )).fetchall()

        components = conn.execute("""
            SELECT
                id,
                project_id,
                component_name,
                component_type,
                label,
                part_number,
                level
            FROM product_structure
            WHERE project_id = ?
            ORDER BY level ASC, id ASC
        """, (
            selected_project_id,
        )).fetchall()

    else:

        functions = []
        components = []

    records = conn.execute("""
        SELECT
            fl.id,
            fl.project_id,
            fl.requirement AS linked_requirement,
            p.project_name,
            fa.function,
            fa.requirement AS function_requirement,
            ps.component_name
        FROM functional_links AS fl

        LEFT JOIN projects AS p
            ON fl.project_id = p.id

        LEFT JOIN functional_analysis AS fa
            ON fl.function_id = fa.id

        LEFT JOIN product_structure AS ps
            ON fl.component_id = ps.id

        ORDER BY fl.id DESC
    """).fetchall()

    conn.close()

    return render_template(
        "functional_links.html",
        projects=projects,
        functions=functions,
        components=components,
        records=records,
        selected_project_id=selected_project_id
    )


# =========================================================
# DFMEA
# =========================================================

@app.route("/dfmea", methods=["GET", "POST"])
def dfmea():

    conn = get_db()

    selected_project_id = request.args.get(
        "project_id",
        ""
    )

    if request.method == "POST":

        project_id = request.form.get(
            "project_id",
            ""
        )

        component_id = request.form.get(
            "component_id",
            ""
        )

        function = request.form.get(
            "function",
            ""
        ).strip()

        failure_mode = request.form.get(
            "failure_mode",
            ""
        ).strip()

        failure_effect = request.form.get(
            "failure_effect",
            ""
        ).strip()

        severity = request.form.get(
            "severity",
            "1"
        )

        cause = request.form.get(
            "cause",
            ""
        ).strip()

        occurrence = request.form.get(
            "occurrence",
            "1"
        )

        prevention_control = request.form.get(
            "prevention_control",
            ""
        ).strip()

        detection_control = request.form.get(
            "detection_control",
            ""
        ).strip()

        detection = request.form.get(
            "detection",
            "1"
        )

        recommended_action = request.form.get(
            "recommended_action",
            ""
        ).strip()

        responsibility = request.form.get(
            "responsibility",
            ""
        ).strip()

        target_date = request.form.get(
            "target_date",
            ""
        ).strip()

        action_status = request.form.get(
            "action_status",
            ""
        ).strip()

        try:
            s = int(severity)
            o = int(occurrence)
            d = int(detection)
            rpn = s * o * d
        except ValueError:
            rpn = 0

        if project_id and failure_mode:

            conn.execute("""
                INSERT INTO dfmea
                (
                    project_id,
                    component_id,
                    function,
                    failure_mode,
                    failure_effect,
                    severity,
                    cause,
                    occurrence,
                    prevention_control,
                    detection_control,
                    detection,
                    rpn,
                    recommended_action,
                    responsibility,
                    target_date,
                    action_status
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                project_id,
                component_id,
                function,
                failure_mode,
                failure_effect,
                severity,
                cause,
                occurrence,
                prevention_control,
                detection_control,
                detection,
                rpn,
                recommended_action,
                responsibility,
                target_date,
                action_status
            ))

            conn.commit()

            conn.close()

            return redirect(
                url_for(
                    "dfmea",
                    project_id=project_id
                )
            )

    projects = conn.execute("""
        SELECT
            id,
            project_name,
            product_name
        FROM projects
        ORDER BY id DESC
    """).fetchall()

    if selected_project_id:

        components = conn.execute("""
            SELECT
                id,
                component_name,
                component_type,
                part_number,
                level
            FROM product_structure
            WHERE project_id = ?
            ORDER BY level, id
        """, (
            selected_project_id,
        )).fetchall()

    else:

        components = []

    records = conn.execute("""
        SELECT
            d.*,
            p.project_name,
            ps.component_name
        FROM dfmea AS d

        LEFT JOIN projects AS p
            ON d.project_id = p.id

        LEFT JOIN product_structure AS ps
            ON d.component_id = ps.id

        ORDER BY d.id DESC
    """).fetchall()

    conn.close()

    return render_template(
        "dfmea.html",
        projects=projects,
        components=components,
        records=records,
        selected_project_id=selected_project_id
    )


# =========================================================
# PFMEA
# =========================================================

@app.route("/pfmea", methods=["GET", "POST"])
def pfmea():

    conn = get_db()

    selected_project_id = request.args.get(
        "project_id",
        ""
    )

    if request.method == "POST":

        project_id = request.form.get(
            "project_id",
            ""
        )

        component_id = request.form.get(
            "component_id",
            ""
        )

        process_step = request.form.get(
            "process_step",
            ""
        ).strip()

        process_function = request.form.get(
            "process_function",
            ""
        ).strip()

        failure_mode = request.form.get(
            "failure_mode",
            ""
        ).strip()

        failure_effect = request.form.get(
            "failure_effect",
            ""
        ).strip()

        severity = request.form.get(
            "severity",
            "1"
        )

        cause = request.form.get(
            "cause",
            ""
        ).strip()

        occurrence = request.form.get(
            "occurrence",
            "1"
        )

        prevention_control = request.form.get(
            "prevention_control",
            ""
        ).strip()

        detection_control = request.form.get(
            "detection_control",
            ""
        ).strip()

        detection = request.form.get(
            "detection",
            "1"
        )

        recommended_action = request.form.get(
            "recommended_action",
            ""
        ).strip()

        responsibility = request.form.get(
            "responsibility",
            ""
        ).strip()

        target_date = request.form.get(
            "target_date",
            ""
        ).strip()

        action_status = request.form.get(
            "action_status",
            ""
        ).strip()

        try:
            s = int(severity)
            o = int(occurrence)
            d = int(detection)
            rpn = s * o * d
        except ValueError:
            rpn = 0

        if project_id and failure_mode:

            conn.execute("""
                INSERT INTO pfmea
                (
                    project_id,
                    component_id,
                    process_step,
                    process_function,
                    failure_mode,
                    failure_effect,
                    severity,
                    cause,
                    occurrence,
                    prevention_control,
                    detection_control,
                    detection,
                    rpn,
                    recommended_action,
                    responsibility,
                    target_date,
                    action_status
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                project_id,
                component_id,
                process_step,
                process_function,
                failure_mode,
                failure_effect,
                severity,
                cause,
                occurrence,
                prevention_control,
                detection_control,
                detection,
                rpn,
                recommended_action,
                responsibility,
                target_date,
                action_status
            ))

            conn.commit()

            conn.close()

            return redirect(
                url_for(
                    "pfmea",
                    project_id=project_id
                )
            )

    projects = conn.execute("""
        SELECT
            id,
            project_name,
            product_name
        FROM projects
        ORDER BY id DESC
    """).fetchall()

    if selected_project_id:

        components = conn.execute("""
            SELECT
                id,
                component_name,
                component_type,
                part_number,
                level
            FROM product_structure
            WHERE project_id = ?
            ORDER BY level, id
        """, (
            selected_project_id,
        )).fetchall()

    else:

        components = []

    records = conn.execute("""
        SELECT
            p.*,
            pr.project_name,
            ps.component_name
        FROM pfmea AS p

        LEFT JOIN projects AS pr
            ON p.project_id = pr.id

        LEFT JOIN product_structure AS ps
            ON p.component_id = ps.id

        ORDER BY p.id DESC
    """).fetchall()

    conn.close()

    return render_template(
        "pfmea.html",
        projects=projects,
        components=components,
        records=records,
        selected_project_id=selected_project_id
    )


# =========================================================
# CONTROL PLAN
# =========================================================

@app.route("/control-plan", methods=["GET", "POST"])
def control_plan():

    conn = get_db()

    selected_project_id = request.args.get(
        "project_id",
        ""
    )

    if request.method == "POST":

        project_id = request.form.get(
            "project_id",
            ""
        )

        component_id = request.form.get(
            "component_id",
            ""
        )

        process_step = request.form.get(
            "process_step",
            ""
        ).strip()

        characteristic = request.form.get(
            "characteristic",
            ""
        ).strip()

        specification = request.form.get(
            "specification",
            ""
        ).strip()

        control_method = request.form.get(
            "control_method",
            ""
        ).strip()

        measurement_method = request.form.get(
            "measurement_method",
            ""
        ).strip()

        sample_size = request.form.get(
            "sample_size",
            ""
        ).strip()

        frequency = request.form.get(
            "frequency",
            ""
        ).strip()

        responsibility = request.form.get(
            "responsibility",
            ""
        ).strip()

        reaction_plan = request.form.get(
            "reaction_plan",
            ""
        ).strip()

        if project_id and characteristic:

            conn.execute("""
                INSERT INTO control_plan
                (
                    project_id,
                    component_id,
                    process_step,
                    characteristic,
                    specification,
                    control_method,
                    measurement_method,
                    sample_size,
                    frequency,
                    responsibility,
                    reaction_plan
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                project_id,
                component_id,
                process_step,
                characteristic,
                specification,
                control_method,
                measurement_method,
                sample_size,
                frequency,
                responsibility,
                reaction_plan
            ))

            conn.commit()

            conn.close()

            return redirect(
                url_for(
                    "control_plan",
                    project_id=project_id
                )
            )

    projects = conn.execute("""
        SELECT
            id,
            project_name,
            product_name
        FROM projects
        ORDER BY id DESC
    """).fetchall()

    if selected_project_id:

        components = conn.execute("""
            SELECT
                id,
                component_name,
                component_type,
                part_number,
                level
            FROM product_structure
            WHERE project_id = ?
            ORDER BY level, id
        """, (
            selected_project_id,
        )).fetchall()

    else:

        components = []

    records = conn.execute("""
        SELECT
            cp.*,
            p.project_name,
            ps.component_name
        FROM control_plan AS cp

        LEFT JOIN projects AS p
            ON cp.project_id = p.id

        LEFT JOIN product_structure AS ps
            ON cp.component_id = ps.id

        ORDER BY cp.id DESC
    """).fetchall()

    conn.close()

    return render_template(
        "control_plan.html",
        projects=projects,
        components=components,
        records=records,
        selected_project_id=selected_project_id
    )


# =========================================================
# REPORTS
# =========================================================

@app.route("/reports", methods=["GET"])
def reports():

    conn = get_db()

    selected_project_id = request.args.get(
        "project_id",
        ""
    )

    projects = conn.execute("""
        SELECT
            id,
            project_name,
            product_name
        FROM projects
        ORDER BY id DESC
    """).fetchall()

    project_info = None

    summary = {
        "functional_analysis": 0,
        "boundary_diagram": 0,
        "product_structure": 0,
        "key_characteristics": 0,
        "functional_links": 0,
        "dfmea": 0,
        "pfmea": 0,
        "control_plan": 0
    }

    components = []
    dfmea_records = []
    pfmea_records = []

    if selected_project_id:

        project_info = conn.execute("""
            SELECT *
            FROM projects
            WHERE id = ?
        """, (
            selected_project_id,
        )).fetchone()

        tables = {
            "functional_analysis": "functional_analysis",
            "boundary_diagram": "boundary_diagram",
            "product_structure": "product_structure",
            "key_characteristics": "key_characteristics",
            "functional_links": "functional_links",
            "dfmea": "dfmea",
            "pfmea": "pfmea",
            "control_plan": "control_plan"
        }

        for key, table in tables.items():

            summary[key] = conn.execute(
                f"""
                SELECT COUNT(*)
                FROM {table}
                WHERE project_id = ?
                """,
                (selected_project_id,)
            ).fetchone()[0]

        components = conn.execute("""
            SELECT
                id,
                component_name,
                component_type,
                label,
                part_number,
                level
            FROM product_structure
            WHERE project_id = ?
            ORDER BY level, id
        """, (
            selected_project_id,
        )).fetchall()

        dfmea_records = conn.execute("""
            SELECT
                d.*,
                ps.component_name
            FROM dfmea AS d

            LEFT JOIN product_structure AS ps
                ON d.component_id = ps.id

            WHERE d.project_id = ?

            ORDER BY d.id DESC
        """, (
            selected_project_id,
        )).fetchall()

        pfmea_records = conn.execute("""
            SELECT
                p.*,
                ps.component_name
            FROM pfmea AS p

            LEFT JOIN product_structure AS ps
                ON p.component_id = ps.id

            WHERE p.project_id = ?

            ORDER BY p.id DESC
        """, (
            selected_project_id,
        )).fetchall()

    conn.close()

    return render_template(
        "reports.html",
        projects=projects,
        project_info=project_info,
        summary=summary,
        components=components,
        dfmea_records=dfmea_records,
        pfmea_records=pfmea_records,
        selected_project_id=selected_project_id
    )

# =========================================================
# EXPORT REPORT TO EXCEL
# =========================================================

@app.route("/export-excel")
def export_excel():

    project_id = request.args.get("project_id")

    if not project_id:
        return "Please select a project first."

    conn = get_db()

    project = conn.execute("""
        SELECT *
        FROM projects
        WHERE id = ?
    """, (project_id,)).fetchone()

    if not project:
        conn.close()
        return "Project not found."

    workbook = Workbook()

    # -----------------------------------------------------
    # PROJECT SHEET
    # -----------------------------------------------------

    sheet = workbook.active
    sheet.title = "Project"

    sheet.append(["Project Name", project["project_name"]])
    sheet.append(["Product Name", project["product_name"]])
    sheet.append(["Customer", project["customer"]])
    sheet.append(["Project Number", project["project_number"]])
    sheet.append(["Created Date", project["created_date"]])

    # -----------------------------------------------------
    # PRODUCT STRUCTURE
    # -----------------------------------------------------

    sheet = workbook.create_sheet("Product Structure")

    sheet.append([
        "Level",
        "Component",
        "Type",
        "Label",
        "Part Number",
        "Description"
    ])

    rows = conn.execute("""
        SELECT
            level,
            component_name,
            component_type,
            label,
            part_number,
            description
        FROM product_structure
        WHERE project_id = ?
        ORDER BY level, id
    """, (project_id,)).fetchall()

    for row in rows:
        sheet.append([
            row["level"],
            row["component_name"],
            row["component_type"],
            row["label"],
            row["part_number"],
            row["description"]
        ])

    # -----------------------------------------------------
    # FUNCTIONAL ANALYSIS
    # -----------------------------------------------------

    sheet = workbook.create_sheet("Functional Analysis")

    sheet.append([
        "Function",
        "Requirement"
    ])

    rows = conn.execute("""
        SELECT
            function,
            requirement
        FROM functional_analysis
        WHERE project_id = ?
        ORDER BY id
    """, (project_id,)).fetchall()

    for row in rows:
        sheet.append([
            row["function"],
            row["requirement"]
        ])

    # -----------------------------------------------------
    # KEY CHARACTERISTICS
    # -----------------------------------------------------

    sheet = workbook.create_sheet("Key Characteristics")

    sheet.append([
        "Component",
        "Characteristic",
        "Specification",
        "Tolerance",
        "Severity",
        "Responsibility"
    ])

    rows = conn.execute("""
        SELECT
            ps.component_name,
            kc.characteristic,
            kc.specification,
            kc.tolerance,
            kc.severity,
            kc.responsibility
        FROM key_characteristics AS kc
        LEFT JOIN product_structure AS ps
            ON kc.component_id = ps.id
        WHERE kc.project_id = ?
        ORDER BY kc.id
    """, (project_id,)).fetchall()

    for row in rows:
        sheet.append([
            row["component_name"],
            row["characteristic"],
            row["specification"],
            row["tolerance"],
            row["severity"],
            row["responsibility"]
        ])

    # -----------------------------------------------------
    # FUNCTIONAL LINKS
    # -----------------------------------------------------

    sheet = workbook.create_sheet("Functional Links")

    sheet.append([
        "Function",
        "Function Requirement",
        "Component",
        "Linked Requirement"
    ])

    rows = conn.execute("""
        SELECT
            fa.function,
            fa.requirement,
            ps.component_name,
            fl.requirement
        FROM functional_links AS fl

        LEFT JOIN functional_analysis AS fa
            ON fl.function_id = fa.id

        LEFT JOIN product_structure AS ps
            ON fl.component_id = ps.id

        WHERE fl.project_id = ?

        ORDER BY fl.id
    """, (project_id,)).fetchall()

    for row in rows:
        sheet.append([
            row["function"],
            row["requirement"],
            row["component_name"],
            row["requirement"]
        ])

    # -----------------------------------------------------
    # DFMEA
    # -----------------------------------------------------

    sheet = workbook.create_sheet("DFMEA")

    sheet.append([
        "Component",
        "Function",
        "Failure Mode",
        "Failure Effect",
        "Severity",
        "Potential Cause",
        "Occurrence",
        "Prevention Control",
        "Detection Control",
        "Detection",
        "RPN",
        "Recommended Action",
        "Responsibility",
        "Target Date",
        "Action Status"
    ])

    rows = conn.execute("""
        SELECT
            ps.component_name,
            d.function,
            d.failure_mode,
            d.failure_effect,
            d.severity,
            d.cause,
            d.occurrence,
            d.prevention_control,
            d.detection_control,
            d.detection,
            d.rpn,
            d.recommended_action,
            d.responsibility,
            d.target_date,
            d.action_status
        FROM dfmea AS d

        LEFT JOIN product_structure AS ps
            ON d.component_id = ps.id

        WHERE d.project_id = ?

        ORDER BY d.id
    """, (project_id,)).fetchall()

    for row in rows:
        sheet.append([
            row["component_name"],
            row["function"],
            row["failure_mode"],
            row["failure_effect"],
            row["severity"],
            row["cause"],
            row["occurrence"],
            row["prevention_control"],
            row["detection_control"],
            row["detection"],
            row["rpn"],
            row["recommended_action"],
            row["responsibility"],
            row["target_date"],
            row["action_status"]
        ])

    # -----------------------------------------------------
    # PFMEA
    # -----------------------------------------------------

    sheet = workbook.create_sheet("PFMEA")

    sheet.append([
        "Component",
        "Process Step",
        "Process Function",
        "Failure Mode",
        "Failure Effect",
        "Severity",
        "Potential Cause",
        "Occurrence",
        "Prevention Control",
        "Detection Control",
        "Detection",
        "RPN",
        "Recommended Action",
        "Responsibility",
        "Target Date",
        "Action Status"
    ])

    rows = conn.execute("""
        SELECT
            ps.component_name,
            p.process_step,
            p.process_function,
            p.failure_mode,
            p.failure_effect,
            p.severity,
            p.cause,
            p.occurrence,
            p.prevention_control,
            p.detection_control,
            p.detection,
            p.rpn,
            p.recommended_action,
            p.responsibility,
            p.target_date,
            p.action_status
        FROM pfmea AS p

        LEFT JOIN product_structure AS ps
            ON p.component_id = ps.id

        WHERE p.project_id = ?

        ORDER BY p.id
    """, (project_id,)).fetchall()

    for row in rows:
        sheet.append([
            row["component_name"],
            row["process_step"],
            row["process_function"],
            row["failure_mode"],
            row["failure_effect"],
            row["severity"],
            row["cause"],
            row["occurrence"],
            row["prevention_control"],
            row["detection_control"],
            row["detection"],
            row["rpn"],
            row["recommended_action"],
            row["responsibility"],
            row["target_date"],
            row["action_status"]
        ])

    # -----------------------------------------------------
    # CONTROL PLAN
    # -----------------------------------------------------

    sheet = workbook.create_sheet("Control Plan")

    sheet.append([
        "Component",
        "Process Step",
        "Characteristic",
        "Specification",
        "Control Method",
        "Measurement Method",
        "Sample Size",
        "Frequency",
        "Responsibility",
        "Reaction Plan"
    ])

    rows = conn.execute("""
        SELECT
            ps.component_name,
            cp.process_step,
            cp.characteristic,
            cp.specification,
            cp.control_method,
            cp.measurement_method,
            cp.sample_size,
            cp.frequency,
            cp.responsibility,
            cp.reaction_plan
        FROM control_plan AS cp

        LEFT JOIN product_structure AS ps
            ON cp.component_id = ps.id

        WHERE cp.project_id = ?

        ORDER BY cp.id
    """, (project_id,)).fetchall()

    for row in rows:
        sheet.append([
            row["component_name"],
            row["process_step"],
            row["characteristic"],
            row["specification"],
            row["control_method"],
            row["measurement_method"],
            row["sample_size"],
            row["frequency"],
            row["responsibility"],
            row["reaction_plan"]
        ])

    conn.close()

    # -----------------------------------------------------
    # COLUMN WIDTH
    # -----------------------------------------------------

    for sheet in workbook.worksheets:

        for column in sheet.columns:

            max_length = 0
            column_letter = column[0].column_letter

            for cell in column:

                if cell.value is not None:

                    max_length = max(
                        max_length,
                        len(str(cell.value))
                    )

            sheet.column_dimensions[
                column_letter
            ].width = min(max_length + 2, 40)

    # -----------------------------------------------------
    # SEND FILE
    # -----------------------------------------------------

    output = BytesIO()

    workbook.save(output)

    output.seek(0)

    return send_file(
        output,
        as_attachment=True,
        download_name="Automotive_FMEA_Report.xlsx",
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )


# =========================================================
# START APPLICATION
# =========================================================

if __name__ == "__main__":

    setup_database()

    print("")
    print("==============================================")
    print("   AUTOMOTIVE FMEA MANAGEMENT SYSTEM")
    print("==============================================")
    print("   Server: http://127.0.0.1:5000")
    print("==============================================")
    print("")

    app.run(
        debug=True,
        host="127.0.0.1",
        port=5000
    )