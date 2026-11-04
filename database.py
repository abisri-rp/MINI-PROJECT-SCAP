import os
import sqlite3
import json
import logging
from datetime import datetime
from config import Config

logger = logging.getLogger(__name__)

# Check if oracledb is available
try:
    import oracledb
    ORACLEDB_AVAILABLE = True
except ImportError:
    ORACLEDB_AVAILABLE = False
    logger.warning("python-oracledb is not installed. Oracle DB mode disabled.")

class Database:
    """
    Unified Database abstraction layer supporting Oracle Database (via python-oracledb)
    with seamless SQLite fallback when Oracle XE is offline or for local rapid evaluation.
    Enforces parameterized queries, ACID transactions, and comprehensive CRUD operations.
    """
    
    _instance = None
    
    def __init__(self):
        self.engine_type = "sqlite"
        self.oracle_connected = False
        self._test_and_select_engine()

    def _test_and_select_engine(self):
        requested_engine = Config.DB_ENGINE.lower()
        
        if requested_engine in ("oracle", "auto") and ORACLEDB_AVAILABLE:
            try:
                # Test Oracle connection with short timeout
                conn = oracledb.connect(
                    user=Config.ORACLE_USER,
                    password=Config.ORACLE_PASSWORD,
                    dsn=Config.ORACLE_DSN
                )
                conn.close()
                self.engine_type = "oracle"
                self.oracle_connected = True
                logger.info(f"Connected successfully to Oracle Database at {Config.ORACLE_DSN}")
                return
            except Exception as e:
                logger.warning(
                    f"Oracle Database connection failed ({Config.ORACLE_DSN}): {e}. "
                    "Falling back to local SQLite engine."
                )
                self.oracle_connected = False
                self.engine_type = "sqlite"
        else:
            self.engine_type = "sqlite"

    def get_connection(self):
        if self.engine_type == "oracle" and ORACLEDB_AVAILABLE:
            return oracledb.connect(
                user=Config.ORACLE_USER,
                password=Config.ORACLE_PASSWORD,
                dsn=Config.ORACLE_DSN
            )
        else:
            conn = sqlite3.connect(str(Config.SQLITE_PATH), timeout=20.0)
            conn.row_factory = sqlite3.Row
            conn.execute("PRAGMA foreign_keys = ON")
            return conn

    def execute_query(self, query_sql, params=None, fetchone=False, fetchall=False, commit=False):
        """
        Executes a SQL query using parameterized queries.
        Translates bind parameter style between Oracle (:1, :2) and SQLite (?, ?).
        """
        params = params or ()
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            if self.engine_type == "oracle":
                # Oracle uses :1, :2 or named binds
                cursor.execute(query_sql, params)
            else:
                # In SQLite, convert Oracle-style CLOB / TIMESTAMP / :1, :2 to ?
                # If query contains :1, :2..., replace with ?
                import re
                sqlite_sql = re.sub(r':\d+', '?', query_sql)
                cursor.execute(sqlite_sql, params)

            if commit:
                conn.commit()
                last_id = cursor.lastrowid
                return last_id

            if fetchone:
                row = cursor.fetchone()
                if row is None:
                    return None
                if self.engine_type == "oracle":
                    col_names = [col[0].lower() for col in cursor.description]
                    return dict(zip(col_names, row))
                else:
                    return dict(row)

            if fetchall:
                rows = cursor.fetchall()
                if self.engine_type == "oracle":
                    col_names = [col[0].lower() for col in cursor.description]
                    return [dict(zip(col_names, r)) for r in rows]
                else:
                    return [dict(r) for r in rows]

            return None
        finally:
            cursor.close()
            conn.close()

    def init_db(self):
        """Initializes tables and seeds default data if not already present."""
        if self.engine_type == "sqlite":
            self._init_sqlite()
        else:
            self._init_oracle()

    def _init_sqlite(self):
        """Creates the relational SQLite schema mirroring Oracle DDL."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.executescript("""
        CREATE TABLE IF NOT EXISTS USERS (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            role TEXT DEFAULT 'user' NOT NULL CHECK(role IN ('user', 'admin')),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
        );

        CREATE TABLE IF NOT EXISTS RESUME (
            resume_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            filename TEXT NOT NULL,
            file_path TEXT NOT NULL,
            file_type TEXT NOT NULL CHECK(file_type IN ('pdf', 'docx')),
            version_number INTEGER DEFAULT 1 NOT NULL,
            raw_text TEXT,
            is_active INTEGER DEFAULT 1 NOT NULL,
            uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
            FOREIGN KEY (user_id) REFERENCES USERS(user_id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS RESUME_ANALYSIS (
            analysis_id INTEGER PRIMARY KEY AUTOINCREMENT,
            resume_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            extracted_json TEXT NOT NULL,
            total_score REAL DEFAULT 0 NOT NULL,
            completeness_score REAL DEFAULT 0 NOT NULL,
            skills_score REAL DEFAULT 0 NOT NULL,
            projects_score REAL DEFAULT 0 NOT NULL,
            verbs_score REAL DEFAULT 0 NOT NULL,
            readability_score REAL DEFAULT 0 NOT NULL,
            predicted_category TEXT,
            confidence_score REAL DEFAULT 0,
            feedback_json TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
            FOREIGN KEY (resume_id) REFERENCES RESUME(resume_id) ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES USERS(user_id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS ADMIN_REVIEW (
            review_id INTEGER PRIMARY KEY AUTOINCREMENT,
            analysis_id INTEGER NOT NULL,
            resume_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            admin_id INTEGER,
            review_status TEXT DEFAULT 'Pending Review' NOT NULL CHECK(review_status IN ('Pending Review', 'Approved', 'Improvement Required')),
            admin_comments TEXT,
            verified_category TEXT,
            corrected_data_json TEXT,
            reviewed_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
            FOREIGN KEY (analysis_id) REFERENCES RESUME_ANALYSIS(analysis_id) ON DELETE CASCADE,
            FOREIGN KEY (resume_id) REFERENCES RESUME(resume_id) ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES USERS(user_id) ON DELETE CASCADE,
            FOREIGN KEY (admin_id) REFERENCES USERS(user_id) ON DELETE SET NULL
        );

        CREATE TABLE IF NOT EXISTS SKILL_CATEGORY (
            category_id INTEGER PRIMARY KEY AUTOINCREMENT,
            category_name TEXT NOT NULL UNIQUE,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
        );

        CREATE TABLE IF NOT EXISTS SKILL (
            skill_id INTEGER PRIMARY KEY AUTOINCREMENT,
            category_id INTEGER NOT NULL,
            skill_name TEXT NOT NULL UNIQUE,
            aliases TEXT,
            FOREIGN KEY (category_id) REFERENCES SKILL_CATEGORY(category_id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS USER_SKILL (
            user_skill_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            resume_id INTEGER NOT NULL,
            skill_name TEXT NOT NULL,
            category_name TEXT,
            detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
            FOREIGN KEY (user_id) REFERENCES USERS(user_id) ON DELETE CASCADE,
            FOREIGN KEY (resume_id) REFERENCES RESUME(resume_id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS RESUME_SUGGESTION (
            suggestion_id INTEGER PRIMARY KEY AUTOINCREMENT,
            resume_id INTEGER NOT NULL,
            original_text TEXT NOT NULL,
            suggested_text TEXT NOT NULL,
            action_verb TEXT,
            explanation TEXT,
            status TEXT DEFAULT 'PENDING' NOT NULL CHECK(status IN ('PENDING', 'ACCEPTED', 'REJECTED', 'EDITED')),
            user_final_text TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
            FOREIGN KEY (resume_id) REFERENCES RESUME(resume_id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS QUESTION_BANK (
            question_id INTEGER PRIMARY KEY AUTOINCREMENT,
            category_id INTEGER,
            topic TEXT NOT NULL,
            question_type TEXT DEFAULT 'MCQ' NOT NULL CHECK(question_type IN ('MCQ', 'DESCRIPTIVE', 'APTITUDE')),
            difficulty TEXT DEFAULT 'Intermediate' NOT NULL CHECK(difficulty IN ('Beginner', 'Intermediate', 'Advanced')),
            question_text TEXT NOT NULL,
            option_a TEXT,
            option_b TEXT,
            option_c TEXT,
            option_d TEXT,
            correct_answer TEXT NOT NULL,
            explanation TEXT,
            rubric_keywords TEXT,
            aptitude_section TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
            FOREIGN KEY (category_id) REFERENCES SKILL_CATEGORY(category_id) ON DELETE SET NULL
        );

        CREATE TABLE IF NOT EXISTS MOCK_INTERVIEW (
            interview_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            category_id INTEGER,
            difficulty TEXT DEFAULT 'Intermediate' NOT NULL,
            total_questions INTEGER DEFAULT 5 NOT NULL,
            score_percentage REAL DEFAULT 0 NOT NULL,
            status TEXT DEFAULT 'COMPLETED' NOT NULL,
            completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
            FOREIGN KEY (user_id) REFERENCES USERS(user_id) ON DELETE CASCADE,
            FOREIGN KEY (category_id) REFERENCES SKILL_CATEGORY(category_id) ON DELETE SET NULL
        );

        CREATE TABLE IF NOT EXISTS INTERVIEW_RESPONSE (
            response_id INTEGER PRIMARY KEY AUTOINCREMENT,
            interview_id INTEGER NOT NULL,
            question_id INTEGER NOT NULL,
            user_answer TEXT,
            is_correct INTEGER DEFAULT 0,
            points_earned REAL DEFAULT 0,
            feedback TEXT,
            FOREIGN KEY (interview_id) REFERENCES MOCK_INTERVIEW(interview_id) ON DELETE CASCADE,
            FOREIGN KEY (question_id) REFERENCES QUESTION_BANK(question_id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS APTITUDE_ATTEMPT (
            attempt_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            total_questions INTEGER DEFAULT 15 NOT NULL,
            correct_count INTEGER DEFAULT 0 NOT NULL,
            score_percentage REAL DEFAULT 0 NOT NULL,
            quant_score REAL DEFAULT 0 NOT NULL,
            logical_score REAL DEFAULT 0 NOT NULL,
            verbal_score REAL DEFAULT 0 NOT NULL,
            started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
            completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
            FOREIGN KEY (user_id) REFERENCES USERS(user_id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS APTITUDE_RESPONSE (
            resp_id INTEGER PRIMARY KEY AUTOINCREMENT,
            attempt_id INTEGER NOT NULL,
            question_id INTEGER NOT NULL,
            selected_option TEXT,
            is_correct INTEGER DEFAULT 0 NOT NULL,
            points REAL DEFAULT 0 NOT NULL,
            FOREIGN KEY (attempt_id) REFERENCES APTITUDE_ATTEMPT(attempt_id) ON DELETE CASCADE,
            FOREIGN KEY (question_id) REFERENCES QUESTION_BANK(question_id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS LEARNING_RESOURCE (
            resource_id INTEGER PRIMARY KEY AUTOINCREMENT,
            category_id INTEGER,
            topic TEXT NOT NULL,
            title TEXT NOT NULL,
            resource_url TEXT NOT NULL,
            resource_type TEXT DEFAULT 'Tutorial' NOT NULL,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
            FOREIGN KEY (category_id) REFERENCES SKILL_CATEGORY(category_id) ON DELETE SET NULL
        );
        """)
        conn.commit()

        # Non-destructive migrations for user profile fields and question attributes
        for col, col_type in [
            ("phone", "TEXT"),
            ("degree", "TEXT"),
            ("institution", "TEXT"),
            ("graduation_year", "TEXT"),
            ("skills", "TEXT"),
            ("experience", "TEXT"),
            ("projects", "TEXT"),
            ("bio", "TEXT"),
            ("linkedin_url", "TEXT"),
            ("github_url", "TEXT"),
            ("languages_known", "TEXT"),
            ("area_of_interest", "TEXT")
        ]:
            try:
                conn.execute(f"ALTER TABLE USERS ADD COLUMN {col} {col_type}")
            except Exception:
                pass

        for col, col_type in [
            ("mark_allocation", "INTEGER DEFAULT 5"),
            ("question_no", "TEXT")
        ]:
            try:
                conn.execute(f"ALTER TABLE QUESTION_BANK ADD COLUMN {col} {col_type}")
            except Exception:
                pass

        conn.commit()
        conn.close()
        self._seed_default_data()

    def _init_oracle(self):
        """Runs the schema.sql in Oracle Database if needed."""
        logger.info("Initializing Oracle database tables...")
        # Users can also run schema.sql via SQL*Plus or oracle_setup.py
        self._seed_default_data()

    def _seed_default_data(self):
        """Populates initial administrator, skill categories, questions, and resources."""
        # 1. Admin account
        admin = self.get_user_by_email(Config.ADMIN_EMAIL)
        if not admin:
            from werkzeug.security import generate_password_hash
            hashed = generate_password_hash(Config.ADMIN_PASSWORD)
            self.create_user(Config.ADMIN_NAME, Config.ADMIN_EMAIL, hashed, role="admin")

        # 2. Check if categories already exist
        categories = self.execute_query("SELECT COUNT(*) as cnt FROM SKILL_CATEGORY", fetchone=True)
        if categories and categories.get("cnt", 0) > 0:
            return

        # Seed categories
        cats = [
            (1, "Software and Web Development", "Full-stack software engineering, web application development, frontend, backend architectures, APIs, and modern frameworks."),
            (2, "Data Science and Analytics", "Exploratory data analysis, statistical modeling, business intelligence, data wrangling, SQL analytics, and visualization."),
            (3, "Artificial Intelligence and Machine Learning", "Supervised/unsupervised algorithms, deep neural networks, natural language processing, computer vision, and model deployment."),
            (4, "Database Development", "Relational database management, SQL optimization, PL/SQL, schema normalization, indexing, transaction handling, and NoSQL systems."),
            (5, "Networking and Cybersecurity", "Network architecture, protocols, security auditing, vulnerability assessment, cryptography, firewalls, and ethical hacking."),
            (6, "Cloud Computing and DevOps", "Cloud infrastructure (AWS/GCP/Azure), containerization, CI/CD pipelines, Docker, Kubernetes, microservices, and automation.")
        ]
        for cid, cname, cdesc in cats:
            self.execute_query(
                "INSERT INTO SKILL_CATEGORY (category_id, category_name, description) VALUES (:1, :2, :3)",
                (cid, cname, cdesc), commit=True
            )

        # Seed skills
        skills = [
            # Software Dev
            (1, "Python", "python,py,python3"), (1, "JavaScript", "js,javascript,es6"),
            (1, "TypeScript", "ts,typescript"), (1, "HTML5", "html,html5"),
            (1, "CSS3", "css,css3"), (1, "React", "react,reactjs"),
            (1, "Node.js", "node,nodejs"), (1, "Flask", "flask,flask-restful"),
            (1, "Django", "django,drf"), (1, "Java", "java,core java"),
            (1, "C++", "cpp,c++"), (1, "REST API", "rest,restful,apis"),
            # Data Science
            (2, "Pandas", "pandas"), (2, "NumPy", "numpy"),
            (2, "Matplotlib", "matplotlib,pyplot"), (2, "Seaborn", "seaborn"),
            (2, "Power BI", "powerbi,power bi"), (2, "Tableau", "tableau"),
            (2, "Statistics", "statistical analysis,probability"),
            # AI / ML
            (3, "scikit-learn", "sklearn,scikit-learn"), (3, "TensorFlow", "tensorflow,tf"),
            (3, "PyTorch", "pytorch,torch"), (3, "NLP", "nlp,natural language processing,spacy"),
            (3, "Computer Vision", "cv,opencv,computer vision"), (3, "Deep Learning", "deep learning,ann,cnn,rnn"),
            # Database Development
            (4, "Oracle Database", "oracle,oracle db,oracledb,pl/sql"), (4, "SQL", "sql,queries"),
            (4, "MySQL", "mysql"), (4, "PostgreSQL", "postgres,postgresql"),
            (4, "MongoDB", "mongo,mongodb,nosql"), (4, "Database Tuning", "indexing,optimization"),
            # Cybersecurity
            (5, "Network Protocols", "tcp/ip,dns,http,https"), (5, "Wireshark", "wireshark,packets"),
            (5, "Ethical Hacking", "pentesting,kali linux"), (5, "Cryptography", "tls,ssl,rsa,aes"),
            # Cloud / DevOps
            (6, "Docker", "docker,containerization"), (6, "Kubernetes", "k8s,kubernetes"),
            (6, "AWS", "aws,amazon web services,ec2,s3"), (6, "CI/CD Pipelines", "jenkins,github actions,ci/cd"),
            (6, "Linux System Admin", "linux,bash,shell scripting")
        ]
        for cid, sname, aliases in skills:
            self.execute_query(
                "INSERT INTO SKILL (category_id, skill_name, aliases) VALUES (:1, :2, :3)",
                (cid, sname, aliases), commit=True
            )

        # Seed Questions
        questions = [
            # Technical Questions (Beginner, Intermediate, Advanced across 6 Tracks)
            (1, 'Distributed Systems', 'MCQ', 'Advanced', 'In a distributed microservices architecture, which design pattern prevents cascading service failures by temporarily halting requests to a failing downstream dependency?', 'Saga Pattern', 'Circuit Breaker Pattern', 'Sidecar Pattern', 'Strangler Fig Pattern', 'B', 'The Circuit Breaker pattern wraps network calls and trips open when error thresholds are exceeded, instantly rejecting requests and preventing cascading system failure.', 'circuit breaker,microservices,cascading failure,resilience', None),
            (1, 'Concurrency & Event Loop', 'MCQ', 'Advanced', 'In asynchronous JavaScript / Node.js, how does the Event Loop handle the Microtask queue compared to the Macrotask (Timers/IO) queue?', 'Microtasks are executed only after all timers in the Macrotask queue expire', 'The entire Microtask queue (Promise callbacks, process.nextTick) is fully drained after each Macrotask before the next Macrotask begins', 'Macrotasks have higher execution priority than Microtasks', 'Microtasks and Macrotasks run concurrently on multiple OS worker threads', 'B', 'Microtasks (Promises, process.nextTick) have higher priority than Macrotasks; the microtask queue is completely drained after each macrotask completes.', 'event loop,microtask,macrotask,promises,nextTick', None),
            (1, 'Memory Management', 'MCQ', 'Advanced', 'Which scenario is a primary cause of accidental memory leaks in single-page web applications (SPAs)?', 'Using CSS flexbox instead of CSS grid', 'Uncleaned DOM event listeners referencing detached DOM trees in closures', 'Using async/await instead of native ES6 Promises', 'Storing small configuration JSON in LocalStorage', 'B', 'Retaining event listener callbacks on detached DOM elements retains the elements in memory through closure references, preventing the garbage collector from freeing memory.', 'memory leak,garbage collector,closures,detached DOM', None),
            (1, 'Distributed Systems Architecture', 'DESCRIPTIVE', 'Advanced', 'Explain how the Saga Pattern maintains data consistency in distributed microservices without distributed 2-Phase Commit (2PC), detailing Choreography vs Orchestration.', None, None, None, None, 'The Saga pattern breaks a distributed transaction into a sequence of local transactions. Each transaction updates data in a single service and publishes an event or message. If a local transaction fails, compensating transactions are executed in reverse to undo changes. Choreography coordinates without a central point via peer-to-peer events, whereas Orchestration uses a centralized orchestrator/state machine to command participant services.', 'Sagas avoid locking distributed resources across network boundaries by executing compensating actions if any intermediate step fails.', 'saga,distributed,2pc,consistency,compensation,compensating,choreography,orchestration,events,coordinator', None),
            (1, 'Application Security', 'DESCRIPTIVE', 'Advanced', 'Describe the security implications of Cross-Site Request Forgery (CSRF) and Server-Side Request Forgery (SSRF), and explain their architectural mitigations.', None, None, None, None, 'CSRF tricks an authenticated user browser into executing unwanted actions on a trusted site; mitigated via anti-CSRF tokens, SameSite=Strict/Lax cookie flags, and Origin/Referer verification. SSRF occurs when an attacker induces the backend server to make unauthorized requests to internal resources (e.g. AWS 169.254.169.254 metadata); mitigated via strict egress firewalls, IP allowlisting/denylisting, and input sanitization of target URLs.', 'CSRF targets the user session state on the client, whereas SSRF targets the backend server trust boundary and internal network.', 'csrf,ssrf,samesite,token,anti-csrf,metadata,egress,internal,allowlist,cookies', None),
            (1, 'OOP & Architecture', 'MCQ', 'Beginner', 'Which Object-Oriented Programming pillar binds data and methods into a single protective unit?', 'Inheritance', 'Encapsulation', 'Polymorphism', 'Abstraction', 'B', 'Encapsulation is the bundling of data and methods operating on that data into a single unit.', 'encapsulation,bundling,data hiding', None),
            (1, 'CSS Layout & Box Model', 'MCQ', 'Beginner', 'What are the four components of the CSS Box Model from innermost to outermost?', 'Margin, Border, Padding, Content', 'Content, Padding, Border, Margin', 'Padding, Content, Margin, Border', 'Border, Padding, Content, Margin', 'B', 'The CSS Box Model consists of the element Content in the center, surrounded by Padding, then Border, and outer Margin.', 'box model,content,padding,border,margin', None),
            (1, 'Data Structures & Algorithms', 'MCQ', 'Beginner', 'Which fundamental abstract data type operates strictly on a First-In, First-Out (FIFO) ordering principle?', 'Stack', 'Queue', 'Binary Search Tree', 'Priority Heap', 'B', 'A Queue processes elements in First-In, First-Out (FIFO) order, in contrast to a Stack which is Last-In, First-Out (LIFO).', 'queue,fifo,first in first out,stack,lifo', None),
            (1, 'Web Architecture', 'MCQ', 'Intermediate', 'What is the primary difference between synchronous and asynchronous request execution in web architectures?', 'Asynchronous requests block the main thread', 'Asynchronous execution allows concurrent execution during network I/O without blocking', 'Synchronous requests always utilize WebSockets', 'There is no difference in modern browsers', 'B', 'Asynchronous operations run non-blockingly, keeping client interfaces responsive.', 'asynchronous,non-blocking,concurrency', None),
            (1, 'RESTful APIs', 'DESCRIPTIVE', 'Intermediate', 'Explain how RESTful API design handles idempotency and describe which HTTP methods (GET, POST, PUT, DELETE) are idempotent.', None, None, None, None, 'An operation is idempotent if repeating it produces identical side effects. GET, PUT, and DELETE are idempotent; POST creates a new entity each time and is not idempotent.', 'Idempotent operations yield identical server state regardless of repetitions. GET, PUT, DELETE are idempotent; POST is non-idempotent.', 'idempotent,idempotency,GET,PUT,DELETE,POST,side effect', None),
            (1, 'Relational Database Joins', 'MCQ', 'Intermediate', 'What is the fundamental difference in result sets between an INNER JOIN and a LEFT OUTER JOIN in SQL?', 'An INNER JOIN returns unmatched rows from both tables, while a LEFT JOIN returns only matching rows', 'An INNER JOIN returns only records where there is a match in both tables; a LEFT JOIN returns all rows from the left table along with matching rows from the right table (filling nulls for non-matches)', 'LEFT JOIN requires table partitions, while INNER JOIN does not', 'There is no semantic difference in standard SQL-92', 'B', 'INNER JOIN restricts rows to matching keys across both tables. LEFT OUTER JOIN preserves all left table records and populates NULLs where right table matches are absent.', 'inner join,left join,outer join,sql,nulls,matching', None),
            (1, 'Stateless Authentication & JWT', 'DESCRIPTIVE', 'Intermediate', 'Explain how JSON Web Tokens (JWT) enable stateless authentication in modern web architectures, detailing the roles of the Header, Payload, and Signature.', None, None, None, None, 'A JSON Web Token (JWT) enables stateless authentication because user identity and claims are encoded directly within the token, eliminating server-side session lookup in memory or databases. A JWT has three dot-separated Base64Url parts: 1) Header: specifies the cryptographic algorithm (e.g. HS256/RS256) and token type. 2) Payload: contains registered, public, and private claims (e.g. user_id, roles, expiration exp). 3) Signature: generated by hashing header and payload with a secret or private key; the server verifies the signature on subsequent requests to confirm the token has not been tampered with.', 'JWTs store authenticated claims client-side. The header defines the algorithm, the payload holds claims, and the cryptographic signature guarantees integrity without server session state.', 'jwt,json web token,stateless,authentication,header,payload,signature,base64,claims,secret,verify,tamper', None),
            (2, 'Data Modeling', 'DESCRIPTIVE', 'Advanced', 'Explain the bias-variance tradeoff and how regularization (L1 Lasso vs L2 Ridge) mitigates model overfitting.', None, None, None, None, 'Bias represents underfitting due to oversimplified assumptions; variance represents overfitting on noise. L1 adds absolute weight penalties forcing coefficients to zero (feature selection); L2 penalizes squared weights to shrink coefficients.', 'Bias error originates from erroneous assumptions; variance originates from sensitivity to training noise. Regularization adds penalties to prevent extreme coefficient values.', 'bias,variance,tradeoff,overfitting,underfitting,L1,L2,lasso,ridge,regularization', None),
            (2, 'Dimensionality Reduction', 'MCQ', 'Advanced', 'In Principal Component Analysis (PCA), what mathematical property defines the relationship between the computed Principal Components?', 'They are highly collinear with maximum mutual information', 'They are orthogonal (uncorrelated) linear combinations of the original features that maximize variance', 'They minimize the entropy of discrete classification labels', 'They are non-linear kernel transformations with unit determinant', 'B', 'PCA calculates eigenvectors of the covariance matrix; each principal component is orthogonal (dot product = 0) and captures successive maximal variance.', 'pca,orthogonal,uncorrelated,variance,eigenvectors', None),
            (2, 'Advanced Analytics & Imbalanced Data', 'DESCRIPTIVE', 'Advanced', 'Explain how SMOTE (Synthetic Minority Over-sampling Technique) generates synthetic samples compared to simple random oversampling, and discuss why evaluating with ROC-AUC can be overly optimistic under severe class imbalance.', None, None, None, None, 'Simple oversampling duplicates existing minority records causing overfitting. SMOTE synthesizes new examples by computing vector differences between k-nearest neighbors in the minority feature space and generating interpolated points along the connecting line. ROC-AUC can be misleadingly high under extreme imbalance because the vast number of True Negatives suppresses the False Positive Rate (FPR = FP / (FP + TN)). Precision-Recall AUC (PR-AUC) focuses exclusively on the positive minority class without distortion from large TN counts.', 'PR-AUC evaluates precision and recall directly without being skewed by large true negative quantities.', 'smote,synthetic,interpolation,knn,k-nearest,oversampling,roc-auc,pr-auc,precision,recall,imbalance,false positive', None),
            (2, 'Feature Engineering & Ensembles', 'MCQ', 'Advanced', 'In gradient boosted decision trees (such as XGBoost or LightGBM), how is the split criterion fundamentally derived at each node?', 'By maximizing Gini impurity on random feature subsets', 'By calculating exact first-order gradients and second-order Hessian approximations of the loss function', 'By averaging the linear correlation coefficients across all training samples', 'By pruning trees strictly according to depth without objective function optimization', 'B', 'XGBoost and modern GBDT algorithms approximate the arbitrary objective loss using a second-order Taylor expansion (gradients and Hessians) to compute optimal split scores.', 'gradient,hessian,taylor expansion,loss function,xgboost,gbdt,split score', None),
            (2, 'Causal Inference & Experimentation', 'DESCRIPTIVE', 'Advanced', 'Explain how Sample Ratio Mismatch (SRM) invalidates A/B test results and discuss methods for handling confounding variables in observational data (e.g., Propensity Score Matching).', None, None, None, None, 'Sample Ratio Mismatch (SRM) indicates that the observed sample allocation ratio deviates significantly from the designed assignment (e.g. 50/50), signaling systemic bias such as bot filtering, browser crashes, or redirection drops. In observational studies where randomized assignment is impossible, confounding variables bias treatment effects; Propensity Score Matching (PSM) balances covariates by estimating the probability of receiving treatment conditional on observable confounders, mimicking randomized trials.', 'SRM detects allocation bias caused by tracking or redirection errors. Propensity score matching creates matched treatment and control groups to control for confounding variables.', 'srm,sample ratio mismatch,a/b testing,confounding,propensity score,matching,psm,covariates,bias,randomized', None),
            (2, 'Pandas Data Wrangling', 'MCQ', 'Beginner', 'In pandas, which method is used to remove records containing missing or null values from a DataFrame?', 'df.replace_null()', 'df.dropna()', 'df.isna_drop()', 'df.clean()', 'B', 'The dropna() function drops rows or columns containing missing (NaN) values.', 'pandas,dropna,missing values', None),
            (2, 'NumPy Array Computing', 'MCQ', 'Beginner', 'Which Python library provides the foundational ndarray data structure for high-performance vectorized numerical operations?', 'Matplotlib', 'NumPy', 'Requests', 'Flask', 'B', 'NumPy is the core numerical computing package in Python providing multidimensional arrays and optimized C-level vectorized operations.', 'numpy,ndarray,vectorized,numerical', None),
            (2, 'Descriptive Statistics', 'MCQ', 'Beginner', 'What is the median of the following ordered numerical sample: [3, 7, 8, 12, 14, 19, 21]?', '8', '12', '14', '12.4', 'B', 'For a sample of 7 sorted values, the median is the 4th element: 12.', 'median,statistics,central tendency', None),
            (2, 'Supervised Learning Paradigms', 'MCQ', 'Intermediate', 'What is the fundamental difference between Classification and Regression in supervised machine learning?', 'Classification predicts discrete categorical class labels; Regression predicts continuous numerical target values', 'Regression only works on unlabeled data, while Classification requires target labels', 'Classification requires linear models; Regression requires decision trees', 'Regression always minimizes cross-entropy loss', 'A', 'Supervised learning splits into classification (discrete targets like spam vs not-spam) and regression (continuous values like house prices or revenue).', 'classification,regression,discrete,continuous,supervised learning', None),
            (2, 'Feature Engineering & Scaling', 'DESCRIPTIVE', 'Intermediate', 'Contrast Min-Max Normalization with Z-score Standardization and explain why feature scaling is critical for distance-based algorithms such as K-Nearest Neighbors (KNN) and Gradient Descent optimization.', None, None, None, None, 'Min-Max Normalization rescales features into a bounded range [0, 1] using (X - X_min) / (X_max - X_min), but is sensitive to extreme outliers. Z-score Standardization transforms features to have zero mean and unit variance using (X - mean) / std, which handles outliers better. Feature scaling is essential for distance-based algorithms (like KNN and SVM) because features with larger numerical magnitudes would otherwise dominate Euclidean distance calculations. For Gradient Descent, scaling ensures smooth, spherical loss contours, preventing oscillating updates and accelerating parameter convergence.', 'Normalization scales to [0, 1]; standardization scales to zero mean and unit variance. Unscaled features distort Euclidean distances in KNN and cause slow oscillating gradient descent convergence.', 'normalization,standardization,min-max,z-score,feature scaling,knn,distance,gradient descent,outliers,convergence', None),
            (3, 'Transformer Architectures', 'MCQ', 'Advanced', 'In the Transformer multi-head attention mechanism, why is the dot product of Query (Q) and Key (K) scaled by 1/sqrt(d_k)?', 'To reduce computational time complexity from O(n^2) to O(n)', 'To prevent dot products from growing excessively large for large dimensions, which would push softmax into regions with tiny gradients', 'To ensure matrices Q and K remain symmetric positive definite', 'To enforce L2 regularization directly on projection weights', 'B', 'For large projection dimensions d_k, dot products grow large in magnitude, driving softmax outputs into saturation where gradients vanish. Dividing by sqrt(d_k) stabilizes backpropagation gradients.', 'transformer,attention,query,key,softmax,gradients,scaled dot product', None),
            (3, 'LLM Fine-Tuning & Adaptation', 'DESCRIPTIVE', 'Advanced', 'Explain Parameter-Efficient Fine-Tuning (PEFT) using Low-Rank Adaptation (LoRA), detailing rank decomposition matrices and how it reduces GPU memory requirements during LLM adaptation.', None, None, None, None, 'Traditional fine-tuning updates all billions of model parameters W. LoRA freezes pre-trained weights W0 and decomposes the weight update delta-W into two low-rank matrices A and B: delta-W = B * A, where B is (d x r) and A is (r x k) with rank r << min(d, k). This reduces trainable parameters by 99%+, dramatically diminishing gradient and optimizer state memory on GPUs while retaining comparable downstream task accuracy.', 'LoRA adapts foundational models by freezing base weights and training minimal low-rank adapter matrices.', 'lora,peft,rank,decomposition,adapter,frozen,weights,gpu,memory,matrix,d_model', None),
            (3, 'Deep Learning Optimization', 'MCQ', 'Advanced', 'Why does the Adam optimizer combine Adaptive Gradient Algorithm (AdaGrad) and Root Mean Square Propagation (RMSprop)?', 'To replace backpropagation with genetic algorithms', 'To track both the exponentially decaying average of past gradients (first moment) and past squared gradients (second moment), stabilizing updates across sparse features and varying curvatures', 'To guarantee convergence to global minima in non-convex loss surfaces without hyperparameter tuning', 'To eliminate the need for batch normalization in convolutional networks', 'B', 'Adam tracks both first moments (momentum) and second moments (uncentered variance of gradients) with bias corrections, adapting learning rates per parameter effectively.', 'adam,optimizer,adagrad,rmsprop,first moment,second moment,momentum,exponential decay', None),
            (3, 'Generative AI & Diffusion Models', 'MCQ', 'Advanced', 'In Denoising Diffusion Probabilistic Models (DDPM), what is the primary role of the neural network during the reverse diffusion process?', 'To directly reconstruct high-resolution images in a single forward pass without sampling', 'To predict the Gaussian noise epsilon added at timestep t, thereby iteratively subtracting estimated noise to recover the original data distribution', 'To discriminate between synthetic and real images via adversarial minimax loss', 'To compress token embeddings into a lower-dimensional latent space', 'B', 'DDPM gradually adds Gaussian noise in the forward process and trains a U-Net to predict the added noise at each step t, allowing iterative reverse denoising.', 'diffusion,ddpm,reverse process,gaussian noise,denoising,u-net,latent', None),
            (3, 'RAG Architecture & Embeddings', 'DESCRIPTIVE', 'Advanced', 'Detail the architecture of an enterprise Retrieval-Augmented Generation (RAG) system, explaining chunking strategies, dense vector vs hybrid search, re-ranking models, and methods to mitigate hallucinations.', None, None, None, None, 'Enterprise RAG ingests unstructured documentation via semantic chunking with overlapping windows. Documents are converted into dense embeddings via transformer models and indexed in a vector database. To overcome vocabulary mismatch, Hybrid Search combines dense semantic vectors with BM25 sparse keyword queries (Reciprocal Rank Fusion). A Cross-Encoder re-ranker then refines candidate chunks by scoring query-document pairs simultaneously. The top chunks are injected into the LLM context prompt with strict instructions and guardrails to cite sources and refuse unsupported queries, preventing hallucinations.', 'RAG combines vector retrieval with language generation. Semantic chunking, hybrid search (dense + BM25), cross-encoder re-ranking, and citation-based grounding minimize hallucinations.', 'rag,retrieval,chunking,dense,vector,sparse,bm25,hybrid search,re-ranker,cross-encoder,hallucination,embeddings,context', None),
            (3, 'Unsupervised Learning', 'MCQ', 'Beginner', 'Which machine learning paradigm learns hidden patterns and cluster groupings from data that lacks human-annotated target labels?', 'Supervised Learning', 'Unsupervised Learning', 'Reinforcement Learning', 'Active Learning', 'B', 'Unsupervised learning discovers intrinsic groupings and representations in unlabeled data (e.g., K-Means clustering, PCA).', 'unsupervised learning,clustering,unlabeled data', None),
            (3, 'Activation Functions', 'MCQ', 'Beginner', 'Which non-linear activation function defined as f(x) = max(0, x) is widely used in deep neural network hidden layers to mitigate vanishing gradients for positive inputs?', 'Sigmoid', 'ReLU (Rectified Linear Unit)', 'Tanh', 'Softmax', 'B', 'ReLU f(x) = max(0, x) has a constant gradient of 1 for all positive inputs, allowing deep networks to train much faster without gradient saturation.', 'relu,activation function,vanishing gradient,non-linear', None),
            (3, 'ML Evaluation', 'MCQ', 'Intermediate', 'Which evaluation metric is most critical when evaluating a machine learning model on an imbalanced classification problem such as fraud detection?', 'Overall Accuracy', 'F1-Score / PR-AUC', 'Mean Squared Error', 'Adjusted R-squared', 'B', 'Accuracy is deceiving under severe imbalance; F1-score balances precision and recall on the minority class.', 'imbalanced,precision,recall,F1-score', None),
            (3, 'NLP & Features', 'DESCRIPTIVE', 'Intermediate', 'Explain how TF-IDF (Term Frequency - Inverse Document Frequency) converts text into numerical vectors and why IDF penalizes common words.', None, None, None, None, 'TF measures word frequency within a document. IDF diminishes weights of words frequent across the entire corpus, penalizing non-informative stopwords and accentuating distinctive terms.', 'TF-IDF weighs term importance by multiplying local occurrence (TF) with corpus-wide rarity (IDF), suppressing common stopwords.', 'TF-IDF,term frequency,inverse document frequency,stopwords,corpus,weight', None),
            (3, 'Computer Vision Regularization', 'MCQ', 'Intermediate', 'What is the primary motivation for applying Data Augmentation (e.g. random cropping, horizontal flipping, affine rotations) during Convolutional Neural Network (CNN) training?', 'To accelerate GPU backpropagation calculations', 'To artificially synthesize training variability, improving generalizability and preventing overfitting on limited image sets', 'To convert colored RGB images into binary masks', 'To eliminate the need for pooling layers', 'B', 'Data augmentation artificially expands training data diversity with invariant transformations, preventing CNN models from overfitting on training samples.', 'data augmentation,cnn,overfitting,generalization,computer vision', None),
            (3, 'Recurrent Networks & Memory Gating', 'DESCRIPTIVE', 'Intermediate', 'Explain why standard Vanilla Recurrent Neural Networks (RNNs) suffer from the vanishing gradient problem over long sequences, and describe how LSTM networks resolve this with Forget, Input, and Output gates.', None, None, None, None, 'In Vanilla RNNs, backpropagation through time (BPTT) requires repeated matrix multiplications of weight matrices across sequential timesteps. If eigenvalues are less than 1, gradients decay exponentially to zero, preventing the network from learning long-term temporal dependencies. LSTMs (Long Short-Term Memory) resolve this by introducing an internal Cell State and three regulating gates: 1) Forget Gate: decides what portion of past cell state to discard via a sigmoid layer. 2) Input Gate: decides what new candidate information to store in the cell state. 3) Output Gate: computes the next hidden state based on filtered cell state and tanh activation. The linear additive highway of the cell state allows error gradients to flow across hundreds of timesteps without exponential decay.', 'Vanilla RNNs suffer from exponential gradient decay during backpropagation through time. LSTMs use an additive cell state controlled by forget, input, and output gates to preserve long-range dependencies.', 'lstm,rnn,vanishing gradient,bptt,cell state,forget gate,input gate,output gate,temporal,long-term dependencies', None),
            (4, 'Oracle Database Tuning', 'DESCRIPTIVE', 'Advanced', 'Discuss how B-Tree indexes improve SELECT query performance in Oracle Database and state a scenario where an index might be ignored by the cost-based optimizer (CBO).', None, None, None, None, 'B-Tree indexes provide balanced tree lookups to fetch RowIDs rapidly. The CBO ignores indexes when wrapping columns in un-indexed functions (e.g. UPPER(name)) or when a full table scan is cheaper due to low selectivity.', 'B-Tree indexes structure sorted keys with pointers to rowids. CBO skips index when column is wrapped in an un-indexed function or when table is very small.', 'B-Tree,index,RowID,full table scan,CBO,optimizer,selectivity', None),
            (4, 'Concurrency & Isolation', 'MCQ', 'Advanced', 'Under ANSI SQL isolation levels, which phenomenon can occur in Repeatable Read that is strictly prevented under Serializable isolation?', 'Dirty Reads', 'Non-Repeatable Reads', 'Phantom Reads', 'Lost Updates', 'C', 'Repeatable Read locks accessed rows preventing modifications, but does not prevent concurrent transactions from inserting new rows matching the WHERE criteria, resulting in Phantom Reads. Serializable prevents phantoms via predicate or range locking.', 'repeatable read,serializable,phantom reads,isolation level,locking', None),
            (4, 'Query Optimization & Cost Modeling', 'DESCRIPTIVE', 'Advanced', 'Explain how the Oracle Cost-Based Optimizer (CBO) determines whether to use a B-Tree Index Unique Scan, Index Range Scan, or Full Table Scan (FTS), and explain the concept of Clustering Factor.', None, None, None, None, 'The CBO calculates I/O and CPU cost using dictionary statistics (data volume, column cardinality, selectivity). An Index Unique Scan is chosen for unique/primary key equality. An Index Range Scan is used for range or non-unique filters with high selectivity. If selectivity is low or the Clustering Factor is high (indicating table rows are scattered across disparate data blocks rather than ordered sequentially with index keys), the CBO determines a Full Table Scan with multi-block read I/O is faster than repeated single-block random index lookups.', 'High clustering factor signifies index pointers require random disk block reads, prompting the optimizer to favor full table scans.', 'cbo,cost,optimizer,b-tree,unique,range,full table scan,fts,clustering factor,selectivity,statistics', None),
            (4, 'Distributed Databases & Consensus', 'MCQ', 'Advanced', 'Under the Raft consensus algorithm used in modern distributed data stores (e.g., etcd, CockroachDB), what guarantees that a newly elected leader has all committed log entries?', 'A leader can only be elected if its log is at least as up-to-date as any majority quorum member', 'The leader queries all followers and pulls missing log entries after election', 'The state machine rolls back uncommitted transactions across all nodes upon election', 'Heartbeat intervals are synchronized via GPS atomic clocks', 'A', 'Raft ensures the Leader Completeness property by rejecting RequestVote RPCs if the candidate log is less up-to-date than the voter log, guaranteeing leaders always possess all committed entries.', 'raft,consensus,quorum,leader election,log replication,commit,distributed', None),
            (4, 'Transaction Durability & ARIES Recovery', 'DESCRIPTIVE', 'Advanced', 'Explain the ARIES (Algorithms for Recovery and Isolation Exploiting Semantics) database recovery protocol, detailing the Analysis, Redo (Repeating History), and Undo phases following a system crash.', None, None, None, None, 'ARIES guarantees atomicity and durability using Write-Ahead Logging (WAL) with physiological logging and Compensation Log Records (CLRs). Post-crash recovery executes three phases: 1) Analysis Phase: scans log forward from the last checkpoint to identify active uncommitted transactions (loser transactions) and dirty pages in buffer pool. 2) Redo Phase: repeats history by scanning forward from the smallest recovery LSN, reapplying changes for all committed and uncommitted transactions to restore the exact pre-crash database state. 3) Undo Phase: scans backward undoing actions of all loser transactions, writing CLRs to ensure that recovery itself is crash-tolerant and never repeats undone actions.', 'ARIES uses write-ahead logging with three recovery phases: Analysis identifies active transactions, Redo repeats history to restore state, and Undo rolls back incomplete transactions using CLRs.', 'aries,recovery,wal,write-ahead logging,lsn,analysis,redo,undo,clr,checkpoint,dirty page,atomicity,durability', None),
            (4, 'SQL Data Manipulation', 'MCQ', 'Beginner', 'Which SQL DML statement is used to insert one or more new record rows into an existing relational table?', 'UPDATE', 'INSERT INTO', 'ALTER TABLE', 'SELECT INTO', 'B', 'INSERT INTO specifies the target table, columns, and values to add new rows to a database.', 'insert into,sql,dml,records', None),
            (4, 'Relational Key Constraints', 'MCQ', 'Beginner', 'What two primary constraints are automatically enforced on a relational table column designated as a PRIMARY KEY?', 'CHECK and DEFAULT', 'UNIQUE and NOT NULL', 'FOREIGN KEY and CASCADE', 'AUTOINCREMENT and INDEX only', 'B', 'A Primary Key uniquely identifies each row in a table, requiring every value to be strictly UNIQUE and NOT NULL.', 'primary key,unique,not null,entity integrity', None),
            (4, 'Database Normalization', 'MCQ', 'Intermediate', 'What is the fundamental objective of database normalization up to Third Normal Form (3NF)?', 'Increase data duplication for faster analytics', 'Eliminate redundant data and prevent insert, update, and deletion anomalies', 'Enforce foreign keys without table indexes', 'Convert relational tables into document JSON', 'B', '3NF removes transitive dependencies, ensuring each non-key field depends strictly on the primary key.', '3NF,normalization,redundancy,anomalies,transitive dependency', None),
            (4, 'Transaction ACID Properties', 'MCQ', 'Intermediate', 'In relational database transactions, what does the ACID acronym stand for?', 'Availability, Consistency, Isolation, Durability', 'Atomicity, Consistency, Isolation, Durability', 'Atomicity, Concurrency, Indexing, Data-integrity', 'Access, Security, Isolation, Durability', 'B', 'ACID stands for Atomicity (all or nothing), Consistency (preserves schema constraints), Isolation (concurrent execution independence), and Durability (committed data persists across crashes).', 'acid,atomicity,consistency,isolation,durability,transactions', None),
            (4, 'Database Index Architectures', 'DESCRIPTIVE', 'Intermediate', 'Compare Clustered Indexes with Non-Clustered Indexes in relational databases, explaining how each affects physical data row organization on disk and query performance.', None, None, None, None, 'A Clustered Index dictates the physical on-disk storage order of actual table rows; because rows can only be physically sorted one way on disk, a table can have only one clustered index (typically on the Primary Key). Lookups on the clustered key find the entire data page directly. A Non-Clustered Index is a separate B-Tree data structure containing sorted index keys and pointers (RowIDs or clustered index keys) back to the actual table data rows. A table can possess multiple non-clustered indexes. While non-clustered indexes speed up secondary search filters, retrieving non-indexed columns requires a secondary key lookup or bookmark lookup to fetch the full row.', 'Clustered indexes define physical data row order on disk (one per table). Non-clustered indexes are separate auxiliary B-Trees pointing to row locations (multiple allowed per table).', 'clustered index,non-clustered index,b-tree,physical storage,disk,rowid,primary key,lookup', None),
            (5, 'Modern Cryptography & Protocols', 'MCQ', 'Advanced', 'Why does modern TLS 1.3 mandate Ephemeral Diffie-Hellman (ECDHE) and eliminate static RSA key exchange?', 'RSA certificates cannot be verified on mobile devices', 'ECDHE guarantees Perfect Forward Secrecy (PFS), ensuring past recorded sessions cannot be decrypted even if the server private key is compromised in the future', 'Diffie-Hellman eliminates the need for Certificate Authorities (CAs)', 'TLS 1.3 strictly prohibits AES symmetric encryption', 'B', 'In static RSA exchange, if the server private key is compromised years later, all previously recorded ciphertext sessions can be decrypted. Ephemeral ECDHE generates fresh temporary keys for every session, providing Perfect Forward Secrecy (PFS).', 'tls,tls 1.3,ecdhe,forward secrecy,pfs,rsa,diffie-hellman', None),
            (5, 'Zero Trust Architecture', 'DESCRIPTIVE', 'Advanced', 'Contrast traditional perimeter-based security (castle-and-moat) with Zero Trust Architecture (ZTA), explaining the principle of never trust, always verify and micro-segmentation.', None, None, None, None, 'Perimeter security assumes anyone inside the corporate intranet firewall is trustworthy, leaving internal networks vulnerable to lateral movement if the perimeter is breached. Zero Trust operates under the assumption of breach: never trust, always verify. Every access request must be authenticated, authorized, and encrypted based on continuous identity verification, device health telemetry, least-privilege role permissions, and network micro-segmentation to restrict blast radiuses.', 'Zero Trust enforces continuous dynamic validation rather than implicit location-based trust.', 'zero trust,perimeter,castle,verify,least privilege,micro-segmentation,identity,iam,mfa,telemetry', None),
            (5, 'Web Security & XSS Mitigation', 'MCQ', 'Advanced', 'Which Content Security Policy (CSP) directive strategy provides the most resilient defense against Cross-Site Scripting (XSS) in modern web applications without breaking inline script bundles?', 'unsafe-inline with wildcard script-src *', "Nonce-based CSP (script-src 'nonce-{random}') combined with 'strict-dynamic' to trust scripts loaded by authorized root scripts", 'Disabling HTTPS and enforcing same-origin headers strictly on CSS stylesheets', 'Relying solely on HTML iframe sandbox attributes', 'B', 'Nonce-based CSP with strict-dynamic ensures that only dynamically generated cryptographic one-time tokens execute scripts and propagate trust to child dependencies, preventing injected XSS payloads.', 'csp,content security policy,nonce,strict-dynamic,xss,inline scripts', None),
            (5, 'Network Protocol Hardening', 'MCQ', 'Advanced', 'How do SYN Cookies protect a server against TCP SYN Flood Denial-of-Service attacks without consuming server state memory?', 'By dropping all incoming TCP packets arriving from external subnets', 'By encoding connection parameters (MSS, timestamp, secret cryptographic hash) into the initial 32-bit TCP Sequence Number (ISN) sent in the SYN-ACK, deferring TCB allocation until the client completes the ACK handshake', 'By executing a CAPTCHA challenge before opening the transport layer socket', 'By re-routing TCP traffic to UDP datagram sockets', 'B', 'SYN Cookies encode connection state in the initial sequence number, eliminating half-open connection tables (TCB) until client ACK verification is confirmed.', 'syn cookies,tcp,syn flood,dos,isn,sequence number,handshake,tcb', None),
            (5, 'Threat Modeling & Forensics', 'DESCRIPTIVE', 'Advanced', 'Detail the STRIDE threat modeling framework and explain how digital forensics investigators analyze memory dumps (RAM) using Volatility to detect Advanced Persistent Threats (APTs) employing DLL injection.', None, None, None, None, 'STRIDE models security threats into Spoofing (identity), Tampering (data integrity), Repudiation (deniability), Information Disclosure (privacy), Denial of Service (availability), and Elevation of Privilege (authorization). In live incident response, sophisticated APT malware operates filelessly in memory. Investigators capture physical RAM dumps and use Volatility to inspect active process trees (pstree), identify unlinked or hidden processes (psxview), scan for injected virtual memory regions with execute-write permissions (malfind/vadinfo), and detect injected Dynamic Link Libraries (DLLs) through suspicious handles, hooked API import tables, or hollowed process memory.', 'STRIDE categorizes system threats. Memory forensics with Volatility inspects process memory, VAD permissions, and hollowed processes to detect fileless DLL injection attacks.', 'stride,threat model,forensics,volatility,ram,memory,apt,dll injection,process hollowing,vad,malfind', None),
            (5, 'Network Port Protocols', 'MCQ', 'Beginner', 'Which standard transport-layer port is officially designated for secure, encrypted web communication via HTTPS (TLS/SSL)?', 'Port 80', 'Port 443', 'Port 22', 'Port 8080', 'B', 'Port 443 is standard for HTTPS encrypted traffic; Port 80 is used for unencrypted HTTP; Port 22 is for SSH.', 'port 443,https,tls,ssl,port 80,network ports', None),
            (5, 'Network Firewalls', 'MCQ', 'Beginner', 'What is the primary security function of an enterprise network firewall?', 'To compile source code into executable binary packages', 'To inspect, monitor, and filter incoming and outgoing network traffic based on predefined security rules and IP/port policies', 'To accelerate Wi-Fi wireless broadcast signals', 'To assign dynamic IP addresses via DHCP', 'B', 'Firewalls establish a defensive perimeter boundary between trusted internal networks and untrusted external networks by filtering traffic packets against security policies.', 'firewall,network security,filtering,packets,rules,perimeter', None),
            (5, 'Symmetric vs Asymmetric Encryption', 'MCQ', 'Intermediate', 'What is the fundamental architectural difference between Symmetric Encryption (e.g. AES) and Asymmetric Encryption (e.g. RSA)?', 'Symmetric encryption only works on plain text strings shorter than 128 characters', 'Symmetric uses a single shared secret key for both encryption and decryption; Asymmetric uses a mathematically linked public-private key pair', 'Asymmetric encryption does not require mathematical keys', 'Symmetric encryption cannot be executed on Linux systems', 'B', 'Symmetric cryptography shares one private secret key (fast, high throughput). Asymmetric cryptography uses a public key for encryption and a distinct private key for decryption (ideal for key exchanges and digital signatures).', 'symmetric,asymmetric,aes,rsa,encryption,decryption,public key,private key', None),
            (5, 'Web Application Security & SQLi', 'DESCRIPTIVE', 'Intermediate', 'Explain how SQL Injection (SQLi) vulnerabilities arise in web applications and why parameterized queries (prepared statements) fundamentally neutralize this attack vector.', None, None, None, None, "SQL Injection occurs when untrusted user input is directly concatenated into SQL query strings without sanitization. An attacker injects SQL control characters (such as ' OR '1'='1) to alter query logic, bypass authentication, or exfiltrate database contents. Parameterized queries (prepared statements) completely eliminate SQLi because the database compiles the SQL query structure and command template first with placeholders before binding user inputs. The database engine treats bound parameters strictly as literal literal data values, never executing user data as executable SQL commands, regardless of what characters are supplied.", 'SQLi occurs from dynamic string concatenation. Prepared statements separate query structure from parameters, ensuring input is treated strictly as data and cannot modify SQL execution logic.', 'sql injection,sqli,parameterized query,prepared statement,sanitization,concatenation,input,payload,syntax', None),
            (6, 'Kubernetes Internals', 'MCQ', 'Advanced', 'In Kubernetes, what component is responsible for monitoring Pod specifications and reconciling the actual container state on an individual worker node?', 'kube-controller-manager', 'kubelet', 'etcd', 'kube-scheduler', 'B', 'The kubelet is the primary node agent that registers the node with the apiserver, watches PodSpecs, and interacts with the container runtime (CRI) to ensure the specified containers are running and healthy.', 'kubernetes,kubelet,worker node,podspec,cri,runtime', None),
            (6, 'Deployment Strategies & Reliability', 'DESCRIPTIVE', 'Advanced', 'Compare Blue-Green Deployments with Canary Deployments, detailing traffic routing mechanisms, rollback speeds, and how distributed database schema migrations (expand-contract pattern) must be handled.', None, None, None, None, 'Blue-Green runs two identical production environments; traffic is cut over 100% via a load balancer/DNS once green passes smoke tests, allowing instantaneous rollback by switching the router back to blue. Canary routes a small percentage of traffic (e.g. 5%) to new instances while monitoring error rates, gradually scaling traffic to 100%. For database migrations, schema changes must use the Expand-Contract (Parallel Run) pattern: first expand the schema backward-compatibly (adding columns/tables without removing old ones), deploy code that writes to both or reads from new, then contract (drop obsolete columns) only after old versions are decommissioned.', 'Decoupling schema migrations via expand-contract prevents breaking previous versions during phased rollouts.', 'blue-green,canary,traffic,rollback,expand-contract,schema,backward,compatible,database,router', None),
            (6, 'Service Mesh & Cloud Networking', 'MCQ', 'Advanced', 'In a Kubernetes Service Mesh (e.g., Istio, Linkerd), how is mutual TLS (mTLS) and traffic management typically implemented between microservices?', 'By configuring hardware firewall appliances outside the Kubernetes cluster', 'By injecting an Envoy sidecar proxy into each application Pod to intercept inbound and outbound pod network traffic transparently', 'By recompiling application source code with custom cryptographic libraries', 'By running all microservices within a single shared container image', 'B', 'A service mesh injects sidecar proxies (like Envoy) using iptables redirection to handle mTLS encryption, traffic routing, rate limiting, and observability without application code modifications.', 'service mesh,istio,envoy,sidecar,mtls,kubernetes,traffic management', None),
            (6, 'Chaos Engineering & Resilience', 'MCQ', 'Advanced', 'What is the primary objective of Chaos Engineering practices (e.g. Chaos Monkey, LitmusChaos) in cloud architectures?', 'To intentionally cause catastrophic downtime during peak customer business hours', 'To proactively identify systemic vulnerabilities and validate automated recovery mechanisms by injecting controlled failures into production environments before unpredictable outages occur', 'To bypass integration testing and deploy code directly without code reviews', 'To stress test hardware CPU clock speeds beyond manufacturer limits', 'B', 'Chaos Engineering builds confidence in system resilience by testing hypotheses about system behavior under turbulent conditions and verifying self-healing mechanisms.', 'chaos engineering,chaos monkey,resilience,fault injection,availability,self-healing', None),
            (6, 'SRE & Observability Engineering', 'DESCRIPTIVE', 'Advanced', 'Compare the Three Pillars of Observability (Metrics, Distributed Tracing, Logs) and explain how Site Reliability Engineering (SRE) teams establish Service Level Objectives (SLOs) and Error Budgets to balance feature velocity with system reliability.', None, None, None, None, 'The Three Pillars of Observability provide comprehensive system visibility: Metrics (aggregated numerical time-series for trend detection and alerting), Distributed Tracing (request lifecycle propagation across microservices with spans and latency breakdowns for bottleneck diagnosis), and Logs (context-rich event timestamps for root-cause analysis). SRE operationalizes reliability by defining Service Level Indicators (SLIs - quantifiable metrics like 99th percentile latency), establishing Service Level Objectives (SLOs - target reliability goals such as 99.9% success rate), and creating Error Budgets (100% - SLO). The Error Budget serves as an objective governance tool: when the error budget is healthy, developers can ship features aggressively; when the budget is depleted by incidents, feature releases freeze and engineering priorities shift to reliability and stability.', 'Observability utilizes metrics, traces, and logs. SRE uses SLIs, SLOs, and Error Budgets to objectively balance new feature deployment velocity with system availability and stability.', 'sre,observability,metrics,tracing,logs,distributed tracing,sli,slo,error budget,reliability,latency,governance', None),
            (6, 'Cloud Computing Service Models', 'MCQ', 'Beginner', 'Which cloud service model provides virtualized compute instances, raw storage volumes, and network routing where the customer is responsible for managing the guest OS, runtime, and applications?', 'SaaS (Software as a Service)', 'IaaS (Infrastructure as a Service)', 'PaaS (Platform as a Service)', 'FaaS (Function as a Service)', 'B', 'IaaS provides fundamental compute, storage, and networking resources (e.g. AWS EC2, GCP Compute Engine). PaaS manages runtimes; SaaS delivers full end-user software.', 'iaas,paas,saas,cloud models,infrastructure,virtual machine', None),
            (6, 'Git Version Control', 'MCQ', 'Beginner', 'In Git version control, which command moves modified files from the working directory to the staging area in preparation for a commit?', 'git push', 'git add', 'git checkout', 'git stash', 'B', 'git add stages working tree modifications, indexing changes to be included in the next commit snapshot.', 'git,git add,staging,version control,commit', None),
            (6, 'Containers vs VMs', 'MCQ', 'Intermediate', 'What is the core architectural difference between Docker containers and traditional Virtual Machines (VMs)?', 'VMs share the host OS kernel, while containers package a dedicated guest OS kernel', 'Containers share the host operating system kernel and isolate user spaces, resulting in lightweight execution', 'Containers require dedicated hardware hypervisors (Type 1)', 'Virtual machines cannot run on Linux servers', 'B', 'Containers isolate processes using host kernel namespaces/cgroups, whereas VMs virtualize physical hardware with a hypervisor and full guest OS.', 'containers,docker,host kernel,virtual machine,hypervisor', None),
            (6, 'Infrastructure as Code (IaC)', 'MCQ', 'Intermediate', 'What is the primary advantage of utilizing Infrastructure as Code (IaC) tools like Terraform or CloudFormation over manual cloud console provisioning?', 'It eliminates the need for cloud billing accounts', 'It codifies cloud resources into declarative, version-controlled definitions that enable automated, repeatable, and drift-free environment deployments', 'It forces all virtual machines to run Windows Server OS', 'It prevents developers from using command-line terminals', 'B', 'IaC provides declarative state management, versioning, automated provisioning, and consistent replication across development, staging, and production environments.', 'iac,infrastructure as code,terraform,declarative,automation,reproducibility', None),
            (6, 'CI/CD Pipelines & Automation', 'DESCRIPTIVE', 'Intermediate', 'Explain the difference between Continuous Integration (CI), Continuous Delivery (CD), and Continuous Deployment, outlining the typical automated pipeline stages from code commit to production release.', None, None, None, None, 'Continuous Integration (CI) is the practice where developers regularly merge code into a shared repository, triggering automated builds, linters, static analysis, and unit test suites to catch regressions early. Continuous Delivery extends CI by automatically packaging artifacts and staging deployment to test environments, ensuring code is always in a releasable state, but requiring manual human approval for production deployment. Continuous Deployment automates the entire journey end-to-end: every change that passes all automated tests deploys automatically to production without human intervention. A standard pipeline includes: 1) Source/Trigger (git push), 2) Build/Compile (dependencies and container image building), 3) Test (unit, integration, and security scans), 4) Staging Verification (smoke and end-to-end tests), and 5) Production Release (canary or blue-green rollout with automated health checks).', 'CI automates build and test on code merge. Continuous Delivery ensures code is always releasable to production with manual gate. Continuous Deployment automatically ships every passing commit to production.', 'ci,cd,continuous integration,continuous delivery,continuous deployment,pipeline,build,test,staging,production,automation,regression', None),

            # Aptitude Questions (Quantitative, Logical, Verbal)
            (None, 'Number Series', 'APTITUDE', 'Beginner', 'Find the missing number in the sequence: 4, 9, 19, 39, 79, ?', '119', '139', '159', '169', 'C', 'Rule: (term * 2) + 1. (79 * 2) + 1 = 159.', None, 'Logical'),
            (None, 'Coding-Decoding', 'APTITUDE', 'Intermediate', 'If the word PYTHON is coded as QZWIPM, how would FLASK be coded following the same character shifting (+1, -1, +1, -1...)?', 'GKBTL', 'GMBTL', 'GKZTL', 'GMZTL', 'A', 'Applying alternating character shift yields GKBTL.', None, 'Logical'),
            (None, 'Syllogisms', 'APTITUDE', 'Intermediate', 'Statements: All developers write code. Some developers are architects. Conclusions: I. Some code writers are architects. II. All architects are developers.', 'Only Conclusion I follows', 'Only Conclusion II follows', 'Both follow', 'Neither follows', 'A', 'Since all developers write code and some are architects, those architects are code writers. Only Conclusion I follows logically.', None, 'Logical'),
            (None, 'Direction Sense', 'APTITUDE', 'Beginner', 'Starting from office, Priya walks 10m North, turns Right and walks 15m, turns Right again and walks 10m. How far is she from the starting point?', '15m East', '15m West', '10m South', '25m North', 'A', 'The north and south paths cancel out, placing her 15m directly East of the origin.', None, 'Logical'),
            (None, 'Blood Relations', 'APTITUDE', 'Intermediate', "Pointing to a photograph, Rohit says, 'She is the daughter of the only son of my grandfather.' How is the woman in the photograph related to Rohit?", 'Sister', 'Aunt', 'Mother', 'Niece', 'A', "Rohit's grandfather's only son is Rohit's father. The daughter of Rohit's father is Rohit's sister.", None, 'Logical'),
            (None, 'Clock Angles', 'APTITUDE', 'Intermediate', 'What is the acute angle between the hour hand and the minute hand of an analog clock at 3:30?', '60 degrees', '75 degrees', '80 degrees', '90 degrees', 'B', 'Angle = |30*H - 5.5*M| = |30*3 - 5.5*30| = |90 - 165| = 75 degrees.', None, 'Logical'),
            (None, 'Seating Arrangements', 'APTITUDE', 'Intermediate', 'Six engineers (A, B, C, D, E, F) sit in a row facing North. C sits between A and E. D is to the immediate right of E. B is at the extreme left. Who sits between B and A?', 'F', 'C', 'D', 'E', 'A', 'The seating arrangement from left to right is: B, F, A, C, E, D. Therefore, F sits between B and A.', None, 'Logical'),
            (None, 'Critical Assumptions', 'APTITUDE', 'Intermediate', "Statement: 'To improve sprint delivery velocity, the DevOps team should implement automated CI/CD pipelines.' Assumption I: Current manual deployments cause delivery bottlenecks. Assumption II: Automated pipelines reduce deployment errors.", 'Only Assumption I is implicit', 'Only Assumption II is implicit', 'Both Assumptions I and II are implicit', 'Neither is implicit', 'C', 'Recommending automated CI/CD assumes that manual deployments currently hinder velocity and that automation remediates errors to improve delivery speed.', None, 'Logical'),
            (None, 'System Analogies', 'APTITUDE', 'Beginner', 'Compiler : Machine Code :: Interpreter : ?', 'Source Code', 'Bytecode / Direct Execution', 'Assembler', 'Linker', 'B', 'A compiler translates entire high-level code into machine code, while an interpreter directly executes instructions or translates into intermediate bytecode.', None, 'Logical'),
            (None, 'Letter-Number Coding', 'APTITUDE', 'Beginner', 'If CLOUD is coded as 3-12-15-21-4 and DEV is coded as 4-5-22, how is the word OPS coded using standard alphabet positions?', '14-15-18', '15-16-19', '15-17-19', '16-17-20', 'B', 'Using 1-based alphabet positions: O = 15, P = 16, S = 19. Hence, 15-16-19.', None, 'Logical'),
            (None, 'Arithmetic & Rates', 'APTITUDE', 'Intermediate', 'A train running at 54 km/hr crosses a platform of length 250 meters in 30 seconds. What is the length of the train in meters?', '150 meters', '200 meters', '250 meters', '300 meters', 'B', 'Speed in m/s = 54 * (5/18) = 15 m/s. Total distance in 30s = 15 * 30 = 450m. Train length = 450 - 250 = 200m.', None, 'Quantitative'),
            (None, 'Percentages & Profit', 'APTITUDE', 'Intermediate', 'An article is sold for $840 at a gain of 20%. What was its initial cost price?', '$680', '$700', '$720', '$750', 'B', 'Cost Price = Selling Price / 1.20 = 840 / 1.20 = $700.', None, 'Quantitative'),
            (None, 'Time & Work', 'APTITUDE', 'Intermediate', 'Worker A can complete a project in 12 days and Worker B can complete it in 24 days. Working together, how many days will it take?', '6 days', '8 days', '9 days', '10 days', 'B', 'Combined daily rate = 1/12 + 1/24 = 3/24 = 1/8. Together they take 8 days.', None, 'Quantitative'),
            (None, 'Ratios & Proportions', 'APTITUDE', 'Beginner', 'The ratio of boys to girls in a computer science class is 5:3. If there are 40 students in total, how many girls are in the class?', '12', '15', '20', '25', 'B', 'Each ratio part = 40 / (5+3) = 5. Girls = 3 * 5 = 15.', None, 'Quantitative'),
            (None, 'Probability', 'APTITUDE', 'Intermediate', 'Two standard six-sided dice are rolled simultaneously. What is the probability that the sum of numbers equals 7?', '1/12', '1/6', '5/36', '7/36', 'B', 'There are 6 favorable outcomes out of 36 total possibilities. 6/36 = 1/6.', None, 'Quantitative'),
            (None, 'Compound Interest', 'APTITUDE', 'Intermediate', 'A sum of money invested at 10% compound interest compounded annually becomes ,420 in 2 years. What was the principal amount invested?', ',800', ',000', ',100', ',200', 'B', 'Amount = P * (1 + r/100)^t => 2420 = P * (1.10)^2 => P = 2420 / 1.21 = ,000.', None, 'Quantitative'),
            (None, 'Pipes & Cisterns', 'APTITUDE', 'Intermediate', 'Pipe A can fill a water tank in 4 hours, and Pipe B can fill it in 6 hours. If both pipes operate simultaneously, how long will it take to fill the tank completely?', '2 hours', '2 hours 24 minutes', '2 hours 45 minutes', '3 hours', 'B', 'Combined rate = 1/4 + 1/6 = 5/12 tank/hr. Total time = 12/5 hrs = 2.4 hrs = 2 hours 24 minutes.', None, 'Quantitative'),
            (None, 'Boats & Streams', 'APTITUDE', 'Intermediate', 'A motorboat travels upstream against the river current at 12 km/h and downstream with the current at 20 km/h. What is the speed of the river stream?', '3 km/h', '4 km/h', '5 km/h', '6 km/h', 'B', 'Speed of stream = (Downstream speed - Upstream speed) / 2 = (20 - 12) / 2 = 4 km/h.', None, 'Quantitative'),
            (None, 'Averages & Teams', 'APTITUDE', 'Beginner', 'The average age of 5 software engineers in a squad is 28 years. When the Tech Lead joins the squad, the average age increases to 30 years. What is the age of the Tech Lead?', '36 years', '40 years', '42 years', '45 years', 'B', 'Total age of 6 members = 6 * 30 = 180. Total age of 5 engineers = 5 * 28 = 140. Tech lead age = 180 - 140 = 40 years.', None, 'Quantitative'),
            (None, 'Permutations', 'APTITUDE', 'Intermediate', "In how many distinct ways can the letters of the word 'REACT' be arranged?", '60', '120', '240', '720', 'B', 'The word REACT has 5 distinct letters. Number of permutations = 5! = 5 * 4 * 3 * 2 * 1 = 120.', None, 'Quantitative'),
            (None, 'Percentage Changes', 'APTITUDE', 'Intermediate', 'A tech company increased its developer headcount by 25% in Q1, and subsequently reduced it by 20% in Q2. What was the net percentage change in headcount?', '+5% increase', '0% (No net change)', '-5% decrease', '+2.5% increase', 'B', 'Net multiplier = (1 + 0.25) * (1 - 0.20) = 1.25 * 0.80 = 1.00. Hence, net change is 0%.', None, 'Quantitative'),
            (None, 'Sentence Correction', 'APTITUDE', 'Intermediate', 'Choose the grammatically correct sentence:', 'Neither the database administrator nor the developers was present at the incident review.', 'Neither the database administrator nor the developers were present at the incident review.', 'Neither the database administrator or the developers were present at the incident review.', 'Neither the database administrator nor the developers has been present at the incident review.', 'B', "In neither...nor constructions, the verb agrees with the closer subject ('developers' plural).", None, 'Verbal'),
            (None, 'Vocabulary & Synonyms', 'APTITUDE', 'Intermediate', 'Select the closest synonym for the word PRAGMATIC in a professional engineering context:', 'Theoretical', 'Idealistic', 'Practical and outcome-oriented', 'Speculative', 'C', 'Pragmatic means practical, sensible, and focused on real-world outcomes.', None, 'Verbal'),
            (None, 'Antonyms', 'APTITUDE', 'Beginner', 'Choose the word that is most opposite in meaning to OBSOLETE:', 'Redundant', 'Contemporary', 'Ancient', 'Archaic', 'B', 'Obsolete means outdated; contemporary means current or modern.', None, 'Verbal'),
            (None, 'Idioms in Workplace', 'APTITUDE', 'Intermediate', "In professional team communication, what does the idiom 'Bite the bullet' mean?", 'Cancel a release abruptly', 'Face an inevitable, difficult situation with courage', 'Blame others for an outage', 'Celebrate a production milestone', 'B', 'To bite the bullet means to accept or confront a grim, difficult, or painful situation bravely.', None, 'Verbal'),
            (None, 'Reading Inference', 'APTITUDE', 'Intermediate', "Passage: 'Microservices allow teams to deploy independent services. However, without centralized distributed tracing and strict interface versioning, systemic complexity quickly exceeds the cognitive capacity of squads.' What can be logically inferred?", 'Microservices eliminate the need for engineering squads', 'Autonomous microservices require observability and interface discipline to manage architectural complexity', 'Monoliths are always superior to microservices', 'Database schema changes never affect microservices', 'B', 'The passage directly emphasizes that independent microservices need distributed tracing and interface versioning to keep architectural complexity manageable.', None, 'Verbal'),
            (None, 'Spotting Grammatical Errors', 'APTITUDE', 'Intermediate', 'Identify the sentence segment containing a grammatical error: (A) Each of the software candidates / (B) have completed their / (C) technical assessment / (D) within the allocated timeframe.', 'Segment A', 'Segment B', 'Segment C', 'Segment D', 'B', "'Each' is an indefinite singular pronoun and requires the singular verb 'has completed', not 'have completed'.", None, 'Verbal'),
            (None, 'Sentence Completion', 'APTITUDE', 'Beginner', 'The comprehensive security audit uncovered several critical vulnerabilities that demanded _______ remediation to prevent sensitive data leakage.', 'negligent', 'prompt and decisive', 'sluggish', 'redundant', 'B', "'Prompt and decisive' appropriately fits the urgent context of mitigating critical security vulnerabilities.", None, 'Verbal'),
            (None, 'Synonyms in Engineering', 'APTITUDE', 'Beginner', 'Choose the closest synonym for the word RESILIENT in the context of cloud systems architecture:', 'Fragile', 'Robust and fault-tolerant', 'Volatile', 'Rigid', 'B', 'A resilient cloud architecture is robust, fault-tolerant, and capable of recovering quickly from disruptions.', None, 'Verbal'),
            (None, 'Sentence Sequencing', 'APTITUDE', 'Intermediate', 'Rearrange the phrases into a coherent logical sequence: (P) It triggers automated test suites. (Q) The developer pushes code to git. (R) Build artifacts deploy to staging. (S) The CI pipeline starts execution.', 'Q-S-P-R', 'S-Q-R-P', 'Q-P-S-R', 'P-Q-S-R', 'A', 'Logical workflow: Developer pushes code (Q) -> CI pipeline starts (S) -> Automated tests run (P) -> Artifacts deploy to staging (R).', None, 'Verbal'),
        ]
        for q in questions:
            self.execute_query(
                """INSERT INTO QUESTION_BANK 
                (category_id, topic, question_type, difficulty, question_text, 
                 option_a, option_b, option_c, option_d, correct_answer, 
                 explanation, rubric_keywords, aptitude_section) 
                VALUES (:1, :2, :3, :4, :5, :6, :7, :8, :9, :10, :11, :12, :13)""",
                q, commit=True
            )

        # Seed Learning Resources
        resources = [
            (1, "RESTful APIs", "Architecting RESTful Web APIs: Best Practices", "https://restfulapi.net/", "Guide", "Comprehensive principles for designing clean, idempotent, scalable HTTP APIs."),
            (1, "OOP & Architecture", "Clean Architecture and SOLID Design Principles", "https://refactoring.guru/design-patterns", "Interactive Guide", "Master object-oriented patterns, encapsulation, and maintainable software design."),
            (2, "Pandas Data Wrangling", "Pandas Complete Data Wrangling Bootcamp", "https://pandas.pydata.org/docs/", "Official Docs", "Essential methods for filtering, aggregating, and handling missing values."),
            (3, "ML Evaluation", "Model Evaluation & Imbalanced Class Metrics in scikit-learn", "https://scikit-learn.org/stable/modules/model_evaluation.html", "Tutorial", "Learn why accuracy is misleading in imbalanced problems and how to use Precision-Recall curves."),
            (4, "Oracle Database Tuning", "Oracle Database SQL Tuning and B-Tree Indexing Guide", "https://docs.oracle.com/en/database/oracle/oracle-database/", "Documentation", "Deep-dive into cost-based query optimization, execution plans, and index architectures."),
            (6, "Containers vs VMs", "Docker & Containerization Architectural Foundations", "https://docs.docker.com/get-started/", "Practical Lab", "Understand namespaces, cgroups, layered storage, and container orchestration."),
            (None, "Quantitative", "Quantitative Aptitude for Placements & Engineering", "https://www.indiabix.com/aptitude/questions-and-answers/", "Practice Bank", "Step-by-step arithmetic, ratios, speed, time, and algebra problem-solving strategies."),
            (None, "Logical", "Logical Reasoning Mastery: Series, Syllogisms, and Deduction", "https://www.indiabix.com/logical-reasoning/questions-and-answers/", "Practice Bank", "Structured techniques to solve coding patterns, direction puzzles, and logical relations."),
            (None, "Verbal", "Grammar, Subject-Verb Concord, and Professional Vocabulary", "https://www.indiabix.com/verbal-ability/questions-and-answers/", "Practice Bank", "Refine sentence mechanics, corporate communication vocabulary, and reading comprehension.")
        ]
        for r in resources:
            self.execute_query(
                "INSERT INTO LEARNING_RESOURCE (category_id, topic, title, resource_url, resource_type, description) VALUES (:1, :2, :3, :4, :5, :6)",
                r, commit=True
            )

    # ================= User Operations =================
    def create_user(self, full_name, email, password_hash, role="user"):
        return self.execute_query(
            "INSERT INTO USERS (full_name, email, password_hash, role) VALUES (:1, :2, :3, :4)",
            (full_name, email.lower().strip(), password_hash, role),
            commit=True
        )

    def get_user_by_email(self, email):
        return self.execute_query(
            "SELECT * FROM USERS WHERE LOWER(email) = LOWER(:1)",
            (email.strip(),), fetchone=True
        )

    def get_user_by_id(self, user_id):
        return self.execute_query(
            "SELECT * FROM USERS WHERE user_id = :1",
            (user_id,), fetchone=True
        )

    def list_all_users(self):
        return self.execute_query(
            """SELECT u.user_id, u.full_name, u.email, u.role, u.created_at,
                      u.phone, u.degree, u.institution, u.graduation_year, u.skills,
                      r.resume_id, r.filename, r.uploaded_at,
                      ra.total_score, ra.predicted_category,
                      ar.review_status
               FROM USERS u
               LEFT JOIN RESUME r ON u.user_id = r.user_id AND r.is_active = 1
               LEFT JOIN RESUME_ANALYSIS ra ON r.resume_id = ra.resume_id
               LEFT JOIN ADMIN_REVIEW ar ON ra.analysis_id = ar.analysis_id
               ORDER BY u.created_at DESC""",
            fetchall=True
        )

    def update_user_password(self, email, password_hash):
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return self.execute_query(
            "UPDATE USERS SET password_hash = :1, updated_at = :2 WHERE LOWER(email) = LOWER(:3)",
            (password_hash, now, email.strip()),
            commit=True
        )

    def update_user_profile(self, user_id, profile_dict):
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return self.execute_query(
            """UPDATE USERS SET 
               full_name = :1, phone = :2, degree = :3, institution = :4,
               graduation_year = :5, skills = :6, experience = :7,
               projects = :8, bio = :9, linkedin_url = :10, github_url = :11,
               languages_known = :12, area_of_interest = :13,
               updated_at = :14
               WHERE user_id = :15""",
            (
                profile_dict.get('full_name', ''),
                profile_dict.get('phone', ''),
                profile_dict.get('degree', ''),
                profile_dict.get('institution', ''),
                profile_dict.get('graduation_year', ''),
                profile_dict.get('skills', ''),
                profile_dict.get('experience', ''),
                profile_dict.get('projects', ''),
                profile_dict.get('bio', ''),
                profile_dict.get('linkedin_url', ''),
                profile_dict.get('github_url', ''),
                profile_dict.get('languages_known', ''),
                profile_dict.get('area_of_interest', ''),
                now,
                user_id
            ),
            commit=True
        )

    def delete_user(self, user_id):
        """
        Permanently deletes a user and cascades all associated records:
        - Uploaded resumes on disk and user upload directory
        - APTITUDE_RESPONSE and APTITUDE_ATTEMPT
        - INTERVIEW_RESPONSE and MOCK_INTERVIEW
        - RESUME_SUGGESTION, USER_SKILL, ADMIN_REVIEW, RESUME_ANALYSIS, RESUME
        - Unlinks admin reviews where this user was the admin reviewer (admin_id set to NULL)
        - USERS record
        """
        import shutil
        from pathlib import Path

        # 1. Physical file cleanup
        try:
            resumes = self.get_all_resumes_for_user(user_id)
            if resumes:
                for r in resumes:
                    fp = r.get('file_path')
                    if fp and os.path.exists(str(fp)):
                        try:
                            os.remove(str(fp))
                        except Exception as e:
                            logger.warning(f"Could not remove resume file {fp}: {e}")

            user_upload_dir = Path(Config.UPLOAD_FOLDER) / f"user_{user_id}"
            if user_upload_dir.exists() and user_upload_dir.is_dir():
                shutil.rmtree(str(user_upload_dir), ignore_errors=True)
        except Exception as e:
            logger.warning(f"Error during physical file cleanup for user {user_id}: {e}")

        # 2. Database cascading deletion
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            def _run(sql, params):
                if self.engine_type == "oracle":
                    cursor.execute(sql, params)
                else:
                    import re
                    sqlite_sql = re.sub(r':\d+', '?', sql)
                    cursor.execute(sqlite_sql, params)

            # Unlink any admin reviews conducted by this user
            _run("UPDATE ADMIN_REVIEW SET admin_id = NULL WHERE admin_id = :1", (user_id,))

            # Delete aptitude test responses and attempts
            _run("""DELETE FROM APTITUDE_RESPONSE WHERE attempt_id IN 
                    (SELECT attempt_id FROM APTITUDE_ATTEMPT WHERE user_id = :1)""", (user_id,))
            _run("DELETE FROM APTITUDE_ATTEMPT WHERE user_id = :1", (user_id,))

            # Delete mock interview responses and interviews
            _run("""DELETE FROM INTERVIEW_RESPONSE WHERE interview_id IN 
                    (SELECT interview_id FROM MOCK_INTERVIEW WHERE user_id = :1)""", (user_id,))
            _run("DELETE FROM MOCK_INTERVIEW WHERE user_id = :1", (user_id,))

            # Delete resume suggestions
            _run("""DELETE FROM RESUME_SUGGESTION WHERE resume_id IN 
                    (SELECT resume_id FROM RESUME WHERE user_id = :1)""", (user_id,))

            # Delete user skills
            _run("DELETE FROM USER_SKILL WHERE user_id = :1", (user_id,))

            # Delete admin reviews of this user's resumes
            _run("DELETE FROM ADMIN_REVIEW WHERE user_id = :1", (user_id,))

            # Delete resume analysis
            _run("DELETE FROM RESUME_ANALYSIS WHERE user_id = :1", (user_id,))

            # Delete resumes
            _run("DELETE FROM RESUME WHERE user_id = :1", (user_id,))

            # Delete the user record
            _run("DELETE FROM USERS WHERE user_id = :1", (user_id,))

            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            logger.error(f"Failed to delete user {user_id}: {e}")
            return False
        finally:
            cursor.close()
            conn.close()

    # ================= Resume Operations =================
    def save_resume(self, user_id, filename, file_path, file_type, raw_text=""):
        # Deactivate older resumes
        self.execute_query(
            "UPDATE RESUME SET is_active = 0 WHERE user_id = :1",
            (user_id,), commit=True
        )
        # Determine next version number
        latest = self.execute_query(
            "SELECT MAX(version_number) as max_v FROM RESUME WHERE user_id = :1",
            (user_id,), fetchone=True
        )
        next_v = (latest.get("max_v") or 0) + 1 if latest else 1

        resume_id = self.execute_query(
            """INSERT INTO RESUME (user_id, filename, file_path, file_type, version_number, raw_text, is_active)
               VALUES (:1, :2, :3, :4, :5, :6, 1)""",
            (user_id, filename, str(file_path), file_type, next_v, raw_text),
            commit=True
        )
        return resume_id, next_v

    def get_resume_by_id(self, resume_id):
        return self.execute_query(
            "SELECT * FROM RESUME WHERE resume_id = :1",
            (resume_id,), fetchone=True
        )

    def get_latest_resume_for_user(self, user_id):
        return self.execute_query(
            "SELECT * FROM RESUME WHERE user_id = :1 AND is_active = 1 ORDER BY version_number DESC",
            (user_id,), fetchone=True
        )

    def get_all_resumes_for_user(self, user_id):
        return self.execute_query(
            "SELECT * FROM RESUME WHERE user_id = :1 ORDER BY version_number DESC",
            (user_id,), fetchall=True
        )

    # ================= Analysis Operations =================
    def save_resume_analysis(self, resume_id, user_id, extracted_dict, scores_dict, category, confidence, feedback_dict):
        analysis_id = self.execute_query(
            """INSERT INTO RESUME_ANALYSIS 
               (resume_id, user_id, extracted_json, total_score, completeness_score, 
                skills_score, projects_score, verbs_score, readability_score, 
                predicted_category, confidence_score, feedback_json)
               VALUES (:1, :2, :3, :4, :5, :6, :7, :8, :9, :10, :11, :12)""",
            (resume_id, user_id, json.dumps(extracted_dict),
             scores_dict.get("total", 0), scores_dict.get("completeness", 0),
             scores_dict.get("skills", 0), scores_dict.get("projects", 0),
             scores_dict.get("action_verbs", 0), scores_dict.get("readability", 0),
             category, confidence, json.dumps(feedback_dict)),
            commit=True
        )
        # Create initial pending admin review
        self.execute_query(
            """INSERT INTO ADMIN_REVIEW (analysis_id, resume_id, user_id, review_status, verified_category)
               VALUES (:1, :2, :3, 'Pending Review', :4)""",
            (analysis_id, resume_id, user_id, category),
            commit=True
        )
        return analysis_id

    def get_analysis_by_resume_id(self, resume_id):
        return self.execute_query(
            "SELECT * FROM RESUME_ANALYSIS WHERE resume_id = :1 ORDER BY created_at DESC",
            (resume_id,), fetchone=True
        )

    def get_latest_analysis_for_user(self, user_id):
        return self.execute_query(
            """SELECT ra.*, r.filename, r.version_number, ar.review_status, ar.admin_comments, ar.reviewed_at
               FROM RESUME_ANALYSIS ra
               JOIN RESUME r ON ra.resume_id = r.resume_id
               LEFT JOIN ADMIN_REVIEW ar ON ra.analysis_id = ar.analysis_id
               WHERE ra.user_id = :1 AND r.is_active = 1
               ORDER BY ra.created_at DESC""",
            (user_id,), fetchone=True
        )

    def update_analysis_extracted_data(self, analysis_id, extracted_dict):
        self.execute_query(
            "UPDATE RESUME_ANALYSIS SET extracted_json = :1 WHERE analysis_id = :2",
            (json.dumps(extracted_dict), analysis_id), commit=True
        )

    # ================= Admin Review Operations =================
    def get_admin_kpis(self):
        total_users = self.execute_query("SELECT COUNT(*) as c FROM USERS WHERE role = 'user'", fetchone=True).get("c", 0)
        total_resumes = self.execute_query("SELECT COUNT(*) as c FROM RESUME", fetchone=True).get("c", 0)
        pending_reviews = self.execute_query("SELECT COUNT(*) as c FROM ADMIN_REVIEW WHERE review_status = 'Pending Review'", fetchone=True).get("c", 0)
        approved_resumes = self.execute_query("SELECT COUNT(*) as c FROM ADMIN_REVIEW WHERE review_status = 'Approved'", fetchone=True).get("c", 0)
        improvement_req = self.execute_query("SELECT COUNT(*) as c FROM ADMIN_REVIEW WHERE review_status = 'Improvement Required'", fetchone=True).get("c", 0)
        total_interviews = self.execute_query("SELECT COUNT(*) as c FROM MOCK_INTERVIEW", fetchone=True).get("c", 0)
        total_aptitude = self.execute_query("SELECT COUNT(*) as c FROM APTITUDE_ATTEMPT", fetchone=True).get("c", 0)

        # Aggregated performance statistics (safe, non-confidential)
        avg_resume = self.execute_query("SELECT ROUND(AVG(total_score), 1) as avg_s FROM RESUME_ANALYSIS", fetchone=True)
        avg_resume_score = avg_resume.get("avg_s") if avg_resume and avg_resume.get("avg_s") is not None else 0

        avg_interview = self.execute_query("SELECT ROUND(AVG(score_percentage), 1) as avg_s FROM MOCK_INTERVIEW", fetchone=True)
        avg_interview_score = avg_interview.get("avg_s") if avg_interview and avg_interview.get("avg_s") is not None else 0

        avg_aptitude = self.execute_query("SELECT ROUND(AVG(score_percentage), 1) as avg_s FROM APTITUDE_ATTEMPT", fetchone=True)
        avg_aptitude_score = avg_aptitude.get("avg_s") if avg_aptitude and avg_aptitude.get("avg_s") is not None else 0

        category_distribution = self.execute_query(
            "SELECT predicted_category, COUNT(*) as count FROM RESUME_ANALYSIS GROUP BY predicted_category", fetchall=True
        )
        return {
            "total_users": total_users,
            "total_resumes": total_resumes,
            "pending_reviews": pending_reviews,
            "approved_resumes": approved_resumes,
            "improvement_req": improvement_req,
            "total_interviews": total_interviews,
            "total_aptitude": total_aptitude,
            "avg_resume_score": avg_resume_score,
            "avg_interview_score": avg_interview_score,
            "avg_aptitude_score": avg_aptitude_score,
            "category_distribution": category_distribution or []
        }

    def list_all_reviews(self):
        return self.execute_query(
            """SELECT ar.*, u.full_name as candidate_name, u.email as candidate_email,
                      r.filename, r.version_number, r.uploaded_at,
                      ra.total_score, ra.predicted_category, ra.extracted_json
               FROM ADMIN_REVIEW ar
               JOIN USERS u ON ar.user_id = u.user_id
               JOIN RESUME r ON ar.resume_id = r.resume_id
               JOIN RESUME_ANALYSIS ra ON ar.analysis_id = ra.analysis_id
               ORDER BY ar.created_at DESC""",
            fetchall=True
        )

    def get_review_by_id(self, review_id):
        return self.execute_query(
            """SELECT ar.*, u.full_name as candidate_name, u.email as candidate_email,
                      r.filename, r.version_number, r.file_path, r.uploaded_at,
                      ra.total_score, ra.completeness_score, ra.skills_score, ra.projects_score,
                      ra.verbs_score, ra.readability_score, ra.predicted_category,
                      ra.confidence_score, ra.extracted_json, ra.feedback_json
               FROM ADMIN_REVIEW ar
               JOIN USERS u ON ar.user_id = u.user_id
               JOIN RESUME r ON ar.resume_id = r.resume_id
               JOIN RESUME_ANALYSIS ra ON ar.analysis_id = ra.analysis_id
               WHERE ar.review_id = :1""",
            (review_id,), fetchone=True
        )

    def submit_admin_review(self, review_id, admin_id, status, comments, verified_cat, corrected_json=None):
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.execute_query(
            """UPDATE ADMIN_REVIEW 
               SET admin_id = :1, review_status = :2, admin_comments = :3, 
                   verified_category = :4, corrected_data_json = :5, reviewed_at = :6
               WHERE review_id = :7""",
            (admin_id, status, comments, verified_cat, corrected_json, now, review_id),
            commit=True
        )

    # ================= Skills Operations =================
    def get_skill_categories(self):
        return self.execute_query("SELECT * FROM SKILL_CATEGORY ORDER BY category_id ASC", fetchall=True)

    def get_all_skills(self):
        return self.execute_query(
            """SELECT s.*, c.category_name 
               FROM SKILL s 
               JOIN SKILL_CATEGORY c ON s.category_id = c.category_id""",
            fetchall=True
        )

    def save_user_skills(self, user_id, resume_id, skills_list):
        self.execute_query("DELETE FROM USER_SKILL WHERE resume_id = :1", (resume_id,), commit=True)
        for s in skills_list:
            name = s.get("name") if isinstance(s, dict) else s
            cat = s.get("category", "General") if isinstance(s, dict) else "General"
            self.execute_query(
                "INSERT INTO USER_SKILL (user_id, resume_id, skill_name, category_name) VALUES (:1, :2, :3, :4)",
                (user_id, resume_id, name, cat), commit=True
            )

    def get_user_skills(self, user_id):
        return self.execute_query(
            """SELECT DISTINCT skill_name, category_name 
               FROM USER_SKILL WHERE user_id = :1 
               ORDER BY category_name, skill_name""",
            (user_id,), fetchall=True
        )

    # ================= Suggestions Operations =================
    def save_suggestion(self, resume_id, original, suggested, verb, explanation):
        return self.execute_query(
            """INSERT INTO RESUME_SUGGESTION 
               (resume_id, original_text, suggested_text, action_verb, explanation, status)
               VALUES (:1, :2, :3, :4, :5, 'PENDING')""",
            (resume_id, original, suggested, verb, explanation),
            commit=True
        )

    def get_suggestions_for_resume(self, resume_id):
        return self.execute_query(
            "SELECT * FROM RESUME_SUGGESTION WHERE resume_id = :1 ORDER BY suggestion_id ASC",
            (resume_id,), fetchall=True
        )

    def update_suggestion_status(self, suggestion_id, status, user_final=None):
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.execute_query(
            """UPDATE RESUME_SUGGESTION 
               SET status = :1, user_final_text = :2, updated_at = :3 
               WHERE suggestion_id = :4""",
            (status, user_final, now, suggestion_id),
            commit=True
        )

    # ================= Question & Assessment Operations =================
    def get_technical_questions(self, category_name=None, difficulty=None, limit=10):
        params = []
        sql = """SELECT q.*, c.category_name 
                 FROM QUESTION_BANK q 
                 LEFT JOIN SKILL_CATEGORY c ON q.category_id = c.category_id 
                 WHERE q.question_type IN ('MCQ', 'DESCRIPTIVE')"""
        
        if category_name:
            sql += " AND (c.category_name = :1 OR c.category_name IS NULL)"
            params.append(category_name)
        if difficulty and difficulty != "All":
            param_idx = len(params) + 1
            sql += f" AND q.difficulty = :{param_idx}"
            params.append(difficulty)
            
        lim = int(limit) if limit else 10
        sql += f" ORDER BY RANDOM() LIMIT {lim}" if self.engine_type == "sqlite" else f" ORDER BY dbms_random.value FETCH FIRST {lim} ROWS ONLY"
        return self.execute_query(sql, tuple(params), fetchall=True)

    def get_aptitude_questions(self, limit=15):
        lim = int(limit) if limit else 15
        sql = "SELECT * FROM QUESTION_BANK WHERE question_type = 'APTITUDE'"
        sql += f" ORDER BY RANDOM() LIMIT {lim}" if self.engine_type == "sqlite" else f" ORDER BY dbms_random.value FETCH FIRST {lim} ROWS ONLY"
        return self.execute_query(sql, fetchall=True)

    def get_question_by_id(self, question_id):
        return self.execute_query(
            "SELECT * FROM QUESTION_BANK WHERE question_id = :1",
            (question_id,), fetchone=True
        )

    def create_mock_interview(self, user_id, category_id, difficulty, total_q, score_pct):
        return self.execute_query(
            """INSERT INTO MOCK_INTERVIEW 
               (user_id, category_id, difficulty, total_questions, score_percentage, status)
               VALUES (:1, :2, :3, :4, :5, 'COMPLETED')""",
            (user_id, category_id, difficulty, total_q, score_pct),
            commit=True
        )

    def save_interview_response(self, interview_id, question_id, user_ans, is_correct, points, feedback):
        self.execute_query(
            """INSERT INTO INTERVIEW_RESPONSE 
               (interview_id, question_id, user_answer, is_correct, points_earned, feedback)
               VALUES (:1, :2, :3, :4, :5, :6)""",
            (interview_id, question_id, user_ans, is_correct, points, feedback),
            commit=True
        )

    def get_user_interviews(self, user_id):
        return self.execute_query(
            """SELECT m.*, c.category_name 
               FROM MOCK_INTERVIEW m 
               LEFT JOIN SKILL_CATEGORY c ON m.category_id = c.category_id 
               WHERE m.user_id = :1 
               ORDER BY m.completed_at DESC""",
            (user_id,), fetchall=True
        )

    def create_aptitude_attempt(self, user_id, total, correct, score_pct, quant, logical, verbal):
        return self.execute_query(
            """INSERT INTO APTITUDE_ATTEMPT 
               (user_id, total_questions, correct_count, score_percentage, quant_score, logical_score, verbal_score)
               VALUES (:1, :2, :3, :4, :5, :6, :7)""",
            (user_id, total, correct, score_pct, quant, logical, verbal),
            commit=True
        )

    def save_aptitude_response(self, attempt_id, question_id, option, is_correct, points):
        self.execute_query(
            """INSERT INTO APTITUDE_RESPONSE (attempt_id, question_id, selected_option, is_correct, points)
               VALUES (:1, :2, :3, :4, :5)""",
            (attempt_id, question_id, option, is_correct, points),
            commit=True
        )

    def get_user_aptitude_attempts(self, user_id):
        return self.execute_query(
            "SELECT * FROM APTITUDE_ATTEMPT WHERE user_id = :1 ORDER BY completed_at DESC",
            (user_id,), fetchall=True
        )

    def get_learning_resources(self, category_name=None, weak_topics=None):
        sql = """SELECT r.*, c.category_name 
                 FROM LEARNING_RESOURCE r 
                 LEFT JOIN SKILL_CATEGORY c ON r.category_id = c.category_id"""
        return self.execute_query(sql, fetchall=True)

    # ================= Progress & Closed Loop Tracking =================
    def get_user_progress_timeline(self, user_id):
        # 1. Resume quality score progression across versions
        resumes = self.execute_query(
            """SELECT r.resume_id, r.version_number, r.uploaded_at,
                      ra.total_score, ra.completeness_score, ra.skills_score,
                      ra.projects_score, ra.verbs_score, ra.readability_score,
                      ra.predicted_category, ar.review_status
               FROM RESUME r
               LEFT JOIN RESUME_ANALYSIS ra ON r.resume_id = ra.resume_id
               LEFT JOIN ADMIN_REVIEW ar ON ra.analysis_id = ar.analysis_id
               WHERE r.user_id = :1
               ORDER BY r.version_number ASC""",
            (user_id,), fetchall=True
        )
        # 2. Mock interview scores
        interviews = self.get_user_interviews(user_id)
        # 3. Aptitude test scores
        aptitudes = self.get_user_aptitude_attempts(user_id)
        # 4. User skills
        skills = self.get_user_skills(user_id)

        return {
            "resumes": resumes or [],
            "interviews": interviews or [],
            "aptitudes": aptitudes or [],
            "skills": skills or []
        }

    # ================= Admin Question Bank Operations =================
    def add_question(self, q_data):
        return self.execute_query(
            """INSERT INTO QUESTION_BANK 
               (category_id, topic, question_type, difficulty, question_text, 
                option_a, option_b, option_c, option_d, correct_answer, 
                explanation, rubric_keywords, aptitude_section, mark_allocation, question_no)
               VALUES (:1, :2, :3, :4, :5, :6, :7, :8, :9, :10, :11, :12, :13, :14, :15)""",
            (
                q_data.get('category_id'),
                q_data.get('topic', 'General'),
                q_data.get('question_type', 'DESCRIPTIVE'),
                q_data.get('difficulty', 'Intermediate'),
                q_data.get('question_text', ''),
                q_data.get('option_a'),
                q_data.get('option_b'),
                q_data.get('option_c'),
                q_data.get('option_d'),
                q_data.get('correct_answer', ''),
                q_data.get('explanation', ''),
                q_data.get('rubric_keywords', ''),
                q_data.get('aptitude_section'),
                int(q_data.get('mark_allocation', 5)),
                q_data.get('question_no')
            ),
            commit=True
        )

    def list_all_questions(self, limit=200):
        lim = int(limit) if limit else 200
        sql = f"""SELECT q.*, c.category_name 
                 FROM QUESTION_BANK q
                 LEFT JOIN SKILL_CATEGORY c ON q.category_id = c.category_id
                 ORDER BY q.question_id DESC LIMIT {lim}""" if self.engine_type == "sqlite" else f"""SELECT q.*, c.category_name 
                 FROM QUESTION_BANK q
                 LEFT JOIN SKILL_CATEGORY c ON q.category_id = c.category_id
                 ORDER BY q.question_id DESC FETCH FIRST {lim} ROWS ONLY"""
        return self.execute_query(sql, fetchall=True)

    def delete_question(self, question_id):
        return self.execute_query(
            "DELETE FROM QUESTION_BANK WHERE question_id = :1",
            (question_id,), commit=True
        )

    # ================= Field of Study / Candidate Skills Grouping =================
    def get_users_by_field_of_study(self):
        """
        Groups registered candidate users by their field of study and learned skills
        (e.g., C -> [Users], Java -> [Users], Python -> [Users]).
        Gathers skills from USER_SKILL, USERS.skills, and RESUME_ANALYSIS.
        """
        users = self.list_all_users()
        # Common key programming languages and fields of study
        skill_groups = {}
        category_groups = {}

        for u in users:
            if u.get('role') == 'admin':
                continue

            user_id = u['user_id']
            user_skills = set()

            # 1. Check USER_SKILL table
            detected = self.get_user_skills(user_id)
            for d in detected:
                if d.get('skill_name'):
                    user_skills.add(d['skill_name'].strip())

            # 2. Check USERS.skills profile field
            if u.get('skills'):
                for sk in str(u['skills']).split(','):
                    cleaned = sk.strip()
                    if cleaned:
                        user_skills.add(cleaned)

            # 3. Check RESUME_ANALYSIS
            latest = self.get_latest_analysis_for_user(user_id)
            if latest and latest.get('extracted_json'):
                try:
                    ext = json.loads(latest['extracted_json'])
                    for s in ext.get('technical_skills', []):
                        user_skills.add(str(s).strip())
                except Exception:
                    pass

            user_summary = {
                "user_id": u['user_id'],
                "full_name": u['full_name'],
                "email": u['email'],
                "degree": u.get('degree') or 'Engineering / Computer Science',
                "institution": u.get('institution') or 'University Student',
                "filename": u.get('filename'),
                "resume_id": u.get('resume_id'),
                "total_score": u.get('total_score'),
                "review_status": u.get('review_status') or 'Pending Review',
                "predicted_category": u.get('predicted_category') or 'Software Development',
                "skills_list": sorted(list(user_skills))
            }

            # Group by predicted category
            cat = user_summary['predicted_category']
            if cat not in category_groups:
                category_groups[cat] = []
            category_groups[cat].append(user_summary)

            # Group by individual learned skill (case-insensitive key mapping)
            for sk in user_skills:
                # Canonical name formatting
                sk_lower = sk.lower()
                if sk_lower in ('c', 'c lang', 'c language'):
                    canonical = "C"
                elif sk_lower in ('java', 'core java', 'j2ee'):
                    canonical = "Java"
                elif sk_lower in ('python', 'python3'):
                    canonical = "Python"
                elif sk_lower in ('c++', 'cpp'):
                    canonical = "C++"
                elif sk_lower in ('c#', 'csharp', '.net'):
                    canonical = "C#"
                elif sk_lower in ('sql', 'pl/sql', 'mysql', 'oracle', 'postgresql'):
                    canonical = "SQL / Database"
                elif sk_lower in ('javascript', 'js', 'typescript', 'ts'):
                    canonical = "JavaScript / Web"
                elif sk_lower in ('html', 'css', 'html5', 'css3'):
                    canonical = "HTML / CSS"
                elif sk_lower in ('react', 'reactjs', 'react.js'):
                    canonical = "React"
                elif sk_lower in ('node', 'nodejs', 'node.js', 'express'):
                    canonical = "Node.js"
                elif sk_lower in ('machine learning', 'ml', 'scikit-learn', 'deep learning'):
                    canonical = "Machine Learning"
                elif sk_lower in ('cloud', 'aws', 'azure', 'gcp', 'devops', 'docker'):
                    canonical = "Cloud & DevOps"
                else:
                    canonical = sk.title()

                if canonical not in skill_groups:
                    skill_groups[canonical] = []
                if user_summary not in skill_groups[canonical]:
                    skill_groups[canonical].append(user_summary)

        # Prioritize key skills like C, Java, Python, SQL at the top
        priority_keys = ["C", "Java", "Python", "C++", "SQL / Database", "JavaScript / Web", "React", "Node.js", "Machine Learning", "Cloud & DevOps"]
        sorted_skill_groups = {}
        for k in priority_keys:
            if k in skill_groups:
                sorted_skill_groups[k] = skill_groups[k]
        for k in sorted(skill_groups.keys()):
            if k not in sorted_skill_groups:
                sorted_skill_groups[k] = skill_groups[k]

        return {
            "skills": sorted_skill_groups,
            "categories": category_groups,
            "total_candidates": len([u for u in users if u.get('role') != 'admin'])
        }

db = Database()

