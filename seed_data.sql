-- ============================================================================
-- STRATEGIC CAREER ADVANCEMENT PLATFORM (SCAP)
-- Oracle Database 19c / 21c / 23ai Initial Seed Data
-- ============================================================================

-- 1. Insert Default Administrator (Password: Admin@SCAP2026)
INSERT INTO USERS (full_name, email, password_hash, role)
VALUES (
    'Platform Administrator',
    'admin@scap.edu',
    'scrypt:32768:8:1$UM9wQKjlCXmtcUTe$b81994219f16d567360bb6d722b3b50ad0d679dec5cf72d87fdc7cc09e316a3eaf6c22590be5cefd7a228ec3f9ff9cef925f6ea206c826e81a01bd25bc06f865',
    'admin'
);

-- 2. Insert Skill Categories
INSERT INTO SKILL_CATEGORY (category_id, category_name, description) VALUES 
(1, 'Software and Web Development', 'Full-stack software engineering, web application development, frontend, backend architectures, APIs, and modern frameworks.');

INSERT INTO SKILL_CATEGORY (category_id, category_name, description) VALUES 
(2, 'Data Science and Analytics', 'Exploratory data analysis, statistical modeling, business intelligence, data wrangling, SQL analytics, and visualization.');

INSERT INTO SKILL_CATEGORY (category_id, category_name, description) VALUES 
(3, 'Artificial Intelligence and Machine Learning', 'Supervised/unsupervised algorithms, deep neural networks, natural language processing, computer vision, and model deployment.');

INSERT INTO SKILL_CATEGORY (category_id, category_name, description) VALUES 
(4, 'Database Development', 'Relational database management, SQL optimization, PL/SQL, schema normalization, indexing, transaction handling, and NoSQL systems.');

INSERT INTO SKILL_CATEGORY (category_id, category_name, description) VALUES 
(5, 'Networking and Cybersecurity', 'Network architecture, protocols, security auditing, vulnerability assessment, cryptography, firewalls, and ethical hacking.');

INSERT INTO SKILL_CATEGORY (category_id, category_name, description) VALUES 
(6, 'Cloud Computing and DevOps', 'Cloud infrastructure (AWS/GCP/Azure), containerization, CI/CD pipelines, Docker, Kubernetes, microservices, and automation.');

-- 3. Insert Skills with Aliases
-- Category 1: Software & Web Dev
INSERT INTO SKILL (category_id, skill_name, aliases) VALUES (1, 'Python', 'python,py,python3');
INSERT INTO SKILL (category_id, skill_name, aliases) VALUES (1, 'JavaScript', 'js,javascript,es6,ecmascript');
INSERT INTO SKILL (category_id, skill_name, aliases) VALUES (1, 'TypeScript', 'ts,typescript');
INSERT INTO SKILL (category_id, skill_name, aliases) VALUES (1, 'HTML5', 'html,html5');
INSERT INTO SKILL (category_id, skill_name, aliases) VALUES (1, 'CSS3', 'css,css3,sass,scss');
INSERT INTO SKILL (category_id, skill_name, aliases) VALUES (1, 'React', 'react,reactjs,react.js');
INSERT INTO SKILL (category_id, skill_name, aliases) VALUES (1, 'Node.js', 'node,nodejs,node.js');
INSERT INTO SKILL (category_id, skill_name, aliases) VALUES (1, 'Flask', 'flask,flask-restful');
INSERT INTO SKILL (category_id, skill_name, aliases) VALUES (1, 'Django', 'django,drf');
INSERT INTO SKILL (category_id, skill_name, aliases) VALUES (1, 'Java', 'java,core java,j2ee');
INSERT INTO SKILL (category_id, skill_name, aliases) VALUES (1, 'C++', 'cpp,c++,c plus plus');
INSERT INTO SKILL (category_id, skill_name, aliases) VALUES (1, 'REST API', 'rest,restful,rest apis,web apis');

-- Category 2: Data Science
INSERT INTO SKILL (category_id, skill_name, aliases) VALUES (2, 'Pandas', 'pandas');
INSERT INTO SKILL (category_id, skill_name, aliases) VALUES (2, 'NumPy', 'numpy');
INSERT INTO SKILL (category_id, skill_name, aliases) VALUES (2, 'Matplotlib', 'matplotlib,pyplot');
INSERT INTO SKILL (category_id, skill_name, aliases) VALUES (2, 'Seaborn', 'seaborn');
INSERT INTO SKILL (category_id, skill_name, aliases) VALUES (2, 'Power BI', 'powerbi,power bi');
INSERT INTO SKILL (category_id, skill_name, aliases) VALUES (2, 'Tableau', 'tableau');
INSERT INTO SKILL (category_id, skill_name, aliases) VALUES (2, 'Statistics', 'statistical analysis,probability,inferential statistics');
INSERT INTO SKILL (category_id, skill_name, aliases) VALUES (2, 'Data Wrangling', 'data cleaning,data transformation,etl');

-- Category 3: AI / ML
INSERT INTO SKILL (category_id, skill_name, aliases) VALUES (3, 'scikit-learn', 'sklearn,scikit-learn,scikit learn');
INSERT INTO SKILL (category_id, skill_name, aliases) VALUES (3, 'TensorFlow', 'tensorflow,tf,tf2');
INSERT INTO SKILL (category_id, skill_name, aliases) VALUES (3, 'PyTorch', 'pytorch,torch');
INSERT INTO SKILL (category_id, skill_name, aliases) VALUES (3, 'NLP', 'nlp,natural language processing,spacy,nltk,transformers');
INSERT INTO SKILL (category_id, skill_name, aliases) VALUES (3, 'Computer Vision', 'cv,opencv,computer vision,image processing');
INSERT INTO SKILL (category_id, skill_name, aliases) VALUES (3, 'Deep Learning', 'dl,deep learning,ann,cnn,rnn,lstm');

-- Category 4: Database Development
INSERT INTO SKILL (category_id, skill_name, aliases) VALUES (4, 'Oracle Database', 'oracle,oracle db,oracledb,pl/sql,plsql');
INSERT INTO SKILL (category_id, skill_name, aliases) VALUES (4, 'SQL', 'sql,structured query language');
INSERT INTO SKILL (category_id, skill_name, aliases) VALUES (4, 'MySQL', 'mysql');
INSERT INTO SKILL (category_id, skill_name, aliases) VALUES (4, 'PostgreSQL', 'postgres,postgresql');
INSERT INTO SKILL (category_id, skill_name, aliases) VALUES (4, 'MongoDB', 'mongo,mongodb,nosql');
INSERT INTO SKILL (category_id, skill_name, aliases) VALUES (4, 'Redis', 'redis,in-memory cache');
INSERT INTO SKILL (category_id, skill_name, aliases) VALUES (4, 'Database Tuning', 'query optimization,indexing,execution plans,normalization');

-- Category 5: Networking & Cybersecurity
INSERT INTO SKILL (category_id, skill_name, aliases) VALUES (5, 'Network Protocols', 'tcp/ip,dns,dhcp,http,https,routing,switching');
INSERT INTO SKILL (category_id, skill_name, aliases) VALUES (5, 'Wireshark', 'wireshark,packet inspection');
INSERT INTO SKILL (category_id, skill_name, aliases) VALUES (5, 'Ethical Hacking', 'penetration testing,pentesting,metasploit,kali linux');
INSERT INTO SKILL (category_id, skill_name, aliases) VALUES (5, 'Cryptography', 'tls,ssl,rsa,aes,encryption,hashing');
INSERT INTO SKILL (category_id, skill_name, aliases) VALUES (5, 'Firewalls & IDS', 'firewall,ids,ips,snort,suricata,siem');

-- Category 6: Cloud Computing & DevOps
INSERT INTO SKILL (category_id, skill_name, aliases) VALUES (6, 'Docker', 'docker,containerization,docker-compose');
INSERT INTO SKILL (category_id, skill_name, aliases) VALUES (6, 'Kubernetes', 'k8s,kubernetes,helm');
INSERT INTO SKILL (category_id, skill_name, aliases) VALUES (6, 'AWS', 'aws,amazon web services,ec2,s3,lambda');
INSERT INTO SKILL (category_id, skill_name, aliases) VALUES (6, 'CI/CD Pipelines', 'jenkins,github actions,gitlab ci,ci/cd');
INSERT INTO SKILL (category_id, skill_name, aliases) VALUES (6, 'Terraform', 'terraform,iac,infrastructure as code');
INSERT INTO SKILL (category_id, skill_name, aliases) VALUES (6, 'Linux System Admin', 'linux,bash,shell scripting,ubuntu,centos,redhat');

-- 4. Insert Curated Question Bank (Technical Mock Interview Questions)

-- Software and Web Development
INSERT INTO QUESTION_BANK (category_id, topic, question_type, difficulty, question_text, option_a, option_b, option_c, option_d, correct_answer, explanation, rubric_keywords) VALUES
(1, 'Distributed Systems', 'MCQ', 'Advanced',
 'In a distributed microservices architecture, which design pattern prevents cascading service failures by temporarily halting requests to a failing downstream dependency?',
 'Saga Pattern', 'Circuit Breaker Pattern', 'Sidecar Pattern', 'Strangler Fig Pattern',
 'B',
 'The Circuit Breaker pattern wraps network calls and trips open when error thresholds are exceeded, instantly rejecting requests and preventing cascading system failure.',
 'circuit breaker,microservices,cascading failure,resilience');

INSERT INTO QUESTION_BANK (category_id, topic, question_type, difficulty, question_text, option_a, option_b, option_c, option_d, correct_answer, explanation, rubric_keywords) VALUES
(1, 'Concurrency & Event Loop', 'MCQ', 'Advanced',
 'In asynchronous JavaScript / Node.js, how does the Event Loop handle the Microtask queue compared to the Macrotask (Timers/IO) queue?',
 'Microtasks are executed only after all timers in the Macrotask queue expire', 'The entire Microtask queue (Promise callbacks, process.nextTick) is fully drained after each Macrotask before the next Macrotask begins', 'Macrotasks have higher execution priority than Microtasks', 'Microtasks and Macrotasks run concurrently on multiple OS worker threads',
 'B',
 'Microtasks (Promises, process.nextTick) have higher priority than Macrotasks; the microtask queue is completely drained after each macrotask completes.',
 'event loop,microtask,macrotask,promises,nextTick');

INSERT INTO QUESTION_BANK (category_id, topic, question_type, difficulty, question_text, option_a, option_b, option_c, option_d, correct_answer, explanation, rubric_keywords) VALUES
(1, 'Memory Management', 'MCQ', 'Advanced',
 'Which scenario is a primary cause of accidental memory leaks in single-page web applications (SPAs)?',
 'Using CSS flexbox instead of CSS grid', 'Uncleaned DOM event listeners referencing detached DOM trees in closures', 'Using async/await instead of native ES6 Promises', 'Storing small configuration JSON in LocalStorage',
 'B',
 'Retaining event listener callbacks on detached DOM elements retains the elements in memory through closure references, preventing the garbage collector from freeing memory.',
 'memory leak,garbage collector,closures,detached DOM');

INSERT INTO QUESTION_BANK (category_id, topic, question_type, difficulty, question_text, option_a, option_b, option_c, option_d, correct_answer, explanation, rubric_keywords) VALUES
(1, 'Distributed Systems Architecture', 'DESCRIPTIVE', 'Advanced',
 'Explain how the Saga Pattern maintains data consistency in distributed microservices without distributed 2-Phase Commit (2PC), detailing Choreography vs Orchestration.',
 NULL, NULL, NULL, NULL,
 'The Saga pattern breaks a distributed transaction into a sequence of local transactions. Each transaction updates data in a single service and publishes an event or message. If a local transaction fails, compensating transactions are executed in reverse to undo changes. Choreography coordinates without a central point via peer-to-peer events, whereas Orchestration uses a centralized orchestrator/state machine to command participant services.',
 'Sagas avoid locking distributed resources across network boundaries by executing compensating actions if any intermediate step fails.',
 'saga,distributed,2pc,consistency,compensation,compensating,choreography,orchestration,events,coordinator');

INSERT INTO QUESTION_BANK (category_id, topic, question_type, difficulty, question_text, option_a, option_b, option_c, option_d, correct_answer, explanation, rubric_keywords) VALUES
(1, 'Application Security', 'DESCRIPTIVE', 'Advanced',
 'Describe the security implications of Cross-Site Request Forgery (CSRF) and Server-Side Request Forgery (SSRF), and explain their architectural mitigations.',
 NULL, NULL, NULL, NULL,
 'CSRF tricks an authenticated user browser into executing unwanted actions on a trusted site; mitigated via anti-CSRF tokens, SameSite=Strict/Lax cookie flags, and Origin/Referer verification. SSRF occurs when an attacker induces the backend server to make unauthorized requests to internal resources (e.g. AWS 169.254.169.254 metadata); mitigated via strict egress firewalls, IP allowlisting/denylisting, and input sanitization of target URLs.',
 'CSRF targets the user session state on the client, whereas SSRF targets the backend server trust boundary and internal network.',
 'csrf,ssrf,samesite,token,anti-csrf,metadata,egress,internal,allowlist,cookies');

INSERT INTO QUESTION_BANK (category_id, topic, question_type, difficulty, question_text, option_a, option_b, option_c, option_d, correct_answer, explanation, rubric_keywords) VALUES
(1, 'OOP & Architecture', 'MCQ', 'Beginner',
 'Which Object-Oriented Programming pillar binds data and methods into a single protective unit?',
 'Inheritance', 'Encapsulation', 'Polymorphism', 'Abstraction',
 'B',
 'Encapsulation is the bundling of data and methods operating on that data into a single unit.',
 'encapsulation,bundling,data hiding');

INSERT INTO QUESTION_BANK (category_id, topic, question_type, difficulty, question_text, option_a, option_b, option_c, option_d, correct_answer, explanation, rubric_keywords) VALUES
(1, 'CSS Layout & Box Model', 'MCQ', 'Beginner',
 'What are the four components of the CSS Box Model from innermost to outermost?',
 'Margin, Border, Padding, Content', 'Content, Padding, Border, Margin', 'Padding, Content, Margin, Border', 'Border, Padding, Content, Margin',
 'B',
 'The CSS Box Model consists of the element Content in the center, surrounded by Padding, then Border, and outer Margin.',
 'box model,content,padding,border,margin');

INSERT INTO QUESTION_BANK (category_id, topic, question_type, difficulty, question_text, option_a, option_b, option_c, option_d, correct_answer, explanation, rubric_keywords) VALUES
(1, 'Data Structures & Algorithms', 'MCQ', 'Beginner',
 'Which fundamental abstract data type operates strictly on a First-In, First-Out (FIFO) ordering principle?',
 'Stack', 'Queue', 'Binary Search Tree', 'Priority Heap',
 'B',
 'A Queue processes elements in First-In, First-Out (FIFO) order, in contrast to a Stack which is Last-In, First-Out (LIFO).',
 'queue,fifo,first in first out,stack,lifo');

INSERT INTO QUESTION_BANK (category_id, topic, question_type, difficulty, question_text, option_a, option_b, option_c, option_d, correct_answer, explanation, rubric_keywords) VALUES
(1, 'Web Architecture', 'MCQ', 'Intermediate',
 'What is the primary difference between synchronous and asynchronous request execution in web architectures?',
 'Asynchronous requests block the main thread', 'Asynchronous execution allows concurrent execution during network I/O without blocking', 'Synchronous requests always utilize WebSockets', 'There is no difference in modern browsers',
 'B',
 'Asynchronous operations run non-blockingly, keeping client interfaces responsive.',
 'asynchronous,non-blocking,concurrency');

INSERT INTO QUESTION_BANK (category_id, topic, question_type, difficulty, question_text, option_a, option_b, option_c, option_d, correct_answer, explanation, rubric_keywords) VALUES
(1, 'RESTful APIs', 'DESCRIPTIVE', 'Intermediate',
 'Explain how RESTful API design handles idempotency and describe which HTTP methods (GET, POST, PUT, DELETE) are idempotent.',
 NULL, NULL, NULL, NULL,
 'An operation is idempotent if repeating it produces identical side effects. GET, PUT, and DELETE are idempotent; POST creates a new entity each time and is not idempotent.',
 'Idempotent operations yield identical server state regardless of repetitions. GET, PUT, DELETE are idempotent; POST is non-idempotent.',
 'idempotent,idempotency,GET,PUT,DELETE,POST,side effect');

INSERT INTO QUESTION_BANK (category_id, topic, question_type, difficulty, question_text, option_a, option_b, option_c, option_d, correct_answer, explanation, rubric_keywords) VALUES
(1, 'Relational Database Joins', 'MCQ', 'Intermediate',
 'What is the fundamental difference in result sets between an INNER JOIN and a LEFT OUTER JOIN in SQL?',
 'An INNER JOIN returns unmatched rows from both tables, while a LEFT JOIN returns only matching rows', 'An INNER JOIN returns only records where there is a match in both tables; a LEFT JOIN returns all rows from the left table along with matching rows from the right table (filling nulls for non-matches)', 'LEFT JOIN requires table partitions, while INNER JOIN does not', 'There is no semantic difference in standard SQL-92',
 'B',
 'INNER JOIN restricts rows to matching keys across both tables. LEFT OUTER JOIN preserves all left table records and populates NULLs where right table matches are absent.',
 'inner join,left join,outer join,sql,nulls,matching');

INSERT INTO QUESTION_BANK (category_id, topic, question_type, difficulty, question_text, option_a, option_b, option_c, option_d, correct_answer, explanation, rubric_keywords) VALUES
(1, 'Stateless Authentication & JWT', 'DESCRIPTIVE', 'Intermediate',
 'Explain how JSON Web Tokens (JWT) enable stateless authentication in modern web architectures, detailing the roles of the Header, Payload, and Signature.',
 NULL, NULL, NULL, NULL,
 'A JSON Web Token (JWT) enables stateless authentication because user identity and claims are encoded directly within the token, eliminating server-side session lookup in memory or databases. A JWT has three dot-separated Base64Url parts: 1) Header: specifies the cryptographic algorithm (e.g. HS256/RS256) and token type. 2) Payload: contains registered, public, and private claims (e.g. user_id, roles, expiration exp). 3) Signature: generated by hashing header and payload with a secret or private key; the server verifies the signature on subsequent requests to confirm the token has not been tampered with.',
 'JWTs store authenticated claims client-side. The header defines the algorithm, the payload holds claims, and the cryptographic signature guarantees integrity without server session state.',
 'jwt,json web token,stateless,authentication,header,payload,signature,base64,claims,secret,verify,tamper');


-- Data Science and Analytics
INSERT INTO QUESTION_BANK (category_id, topic, question_type, difficulty, question_text, option_a, option_b, option_c, option_d, correct_answer, explanation, rubric_keywords) VALUES
(2, 'Data Modeling', 'DESCRIPTIVE', 'Advanced',
 'Explain the bias-variance tradeoff and how regularization (L1 Lasso vs L2 Ridge) mitigates model overfitting.',
 NULL, NULL, NULL, NULL,
 'Bias represents underfitting due to oversimplified assumptions; variance represents overfitting on noise. L1 adds absolute weight penalties forcing coefficients to zero (feature selection); L2 penalizes squared weights to shrink coefficients.',
 'Bias error originates from erroneous assumptions; variance originates from sensitivity to training noise. Regularization adds penalties to prevent extreme coefficient values.',
 'bias,variance,tradeoff,overfitting,underfitting,L1,L2,lasso,ridge,regularization');

INSERT INTO QUESTION_BANK (category_id, topic, question_type, difficulty, question_text, option_a, option_b, option_c, option_d, correct_answer, explanation, rubric_keywords) VALUES
(2, 'Dimensionality Reduction', 'MCQ', 'Advanced',
 'In Principal Component Analysis (PCA), what mathematical property defines the relationship between the computed Principal Components?',
 'They are highly collinear with maximum mutual information', 'They are orthogonal (uncorrelated) linear combinations of the original features that maximize variance', 'They minimize the entropy of discrete classification labels', 'They are non-linear kernel transformations with unit determinant',
 'B',
 'PCA calculates eigenvectors of the covariance matrix; each principal component is orthogonal (dot product = 0) and captures successive maximal variance.',
 'pca,orthogonal,uncorrelated,variance,eigenvectors');

INSERT INTO QUESTION_BANK (category_id, topic, question_type, difficulty, question_text, option_a, option_b, option_c, option_d, correct_answer, explanation, rubric_keywords) VALUES
(2, 'Advanced Analytics & Imbalanced Data', 'DESCRIPTIVE', 'Advanced',
 'Explain how SMOTE (Synthetic Minority Over-sampling Technique) generates synthetic samples compared to simple random oversampling, and discuss why evaluating with ROC-AUC can be overly optimistic under severe class imbalance.',
 NULL, NULL, NULL, NULL,
 'Simple oversampling duplicates existing minority records causing overfitting. SMOTE synthesizes new examples by computing vector differences between k-nearest neighbors in the minority feature space and generating interpolated points along the connecting line. ROC-AUC can be misleadingly high under extreme imbalance because the vast number of True Negatives suppresses the False Positive Rate (FPR = FP / (FP + TN)). Precision-Recall AUC (PR-AUC) focuses exclusively on the positive minority class without distortion from large TN counts.',
 'PR-AUC evaluates precision and recall directly without being skewed by large true negative quantities.',
 'smote,synthetic,interpolation,knn,k-nearest,oversampling,roc-auc,pr-auc,precision,recall,imbalance,false positive');

INSERT INTO QUESTION_BANK (category_id, topic, question_type, difficulty, question_text, option_a, option_b, option_c, option_d, correct_answer, explanation, rubric_keywords) VALUES
(2, 'Feature Engineering & Ensembles', 'MCQ', 'Advanced',
 'In gradient boosted decision trees (such as XGBoost or LightGBM), how is the split criterion fundamentally derived at each node?',
 'By maximizing Gini impurity on random feature subsets', 'By calculating exact first-order gradients and second-order Hessian approximations of the loss function', 'By averaging the linear correlation coefficients across all training samples', 'By pruning trees strictly according to depth without objective function optimization',
 'B',
 'XGBoost and modern GBDT algorithms approximate the arbitrary objective loss using a second-order Taylor expansion (gradients and Hessians) to compute optimal split scores.',
 'gradient,hessian,taylor expansion,loss function,xgboost,gbdt,split score');

INSERT INTO QUESTION_BANK (category_id, topic, question_type, difficulty, question_text, option_a, option_b, option_c, option_d, correct_answer, explanation, rubric_keywords) VALUES
(2, 'Causal Inference & Experimentation', 'DESCRIPTIVE', 'Advanced',
 'Explain how Sample Ratio Mismatch (SRM) invalidates A/B test results and discuss methods for handling confounding variables in observational data (e.g., Propensity Score Matching).',
 NULL, NULL, NULL, NULL,
 'Sample Ratio Mismatch (SRM) indicates that the observed sample allocation ratio deviates significantly from the designed assignment (e.g. 50/50), signaling systemic bias such as bot filtering, browser crashes, or redirection drops. In observational studies where randomized assignment is impossible, confounding variables bias treatment effects; Propensity Score Matching (PSM) balances covariates by estimating the probability of receiving treatment conditional on observable confounders, mimicking randomized trials.',
 'SRM detects allocation bias caused by tracking or redirection errors. Propensity score matching creates matched treatment and control groups to control for confounding variables.',
 'srm,sample ratio mismatch,a/b testing,confounding,propensity score,matching,psm,covariates,bias,randomized');

INSERT INTO QUESTION_BANK (category_id, topic, question_type, difficulty, question_text, option_a, option_b, option_c, option_d, correct_answer, explanation, rubric_keywords) VALUES
(2, 'Pandas Data Wrangling', 'MCQ', 'Beginner',
 'In pandas, which method is used to remove records containing missing or null values from a DataFrame?',
 'df.replace_null()', 'df.dropna()', 'df.isna_drop()', 'df.clean()',
 'B',
 'The dropna() function drops rows or columns containing missing (NaN) values.',
 'pandas,dropna,missing values');

INSERT INTO QUESTION_BANK (category_id, topic, question_type, difficulty, question_text, option_a, option_b, option_c, option_d, correct_answer, explanation, rubric_keywords) VALUES
(2, 'NumPy Array Computing', 'MCQ', 'Beginner',
 'Which Python library provides the foundational ndarray data structure for high-performance vectorized numerical operations?',
 'Matplotlib', 'NumPy', 'Requests', 'Flask',
 'B',
 'NumPy is the core numerical computing package in Python providing multidimensional arrays and optimized C-level vectorized operations.',
 'numpy,ndarray,vectorized,numerical');

INSERT INTO QUESTION_BANK (category_id, topic, question_type, difficulty, question_text, option_a, option_b, option_c, option_d, correct_answer, explanation, rubric_keywords) VALUES
(2, 'Descriptive Statistics', 'MCQ', 'Beginner',
 'What is the median of the following ordered numerical sample: [3, 7, 8, 12, 14, 19, 21]?',
 '8', '12', '14', '12.4',
 'B',
 'For a sample of 7 sorted values, the median is the 4th element: 12.',
 'median,statistics,central tendency');

INSERT INTO QUESTION_BANK (category_id, topic, question_type, difficulty, question_text, option_a, option_b, option_c, option_d, correct_answer, explanation, rubric_keywords) VALUES
(2, 'Supervised Learning Paradigms', 'MCQ', 'Intermediate',
 'What is the fundamental difference between Classification and Regression in supervised machine learning?',
 'Classification predicts discrete categorical class labels; Regression predicts continuous numerical target values', 'Regression only works on unlabeled data, while Classification requires target labels', 'Classification requires linear models; Regression requires decision trees', 'Regression always minimizes cross-entropy loss',
 'A',
 'Supervised learning splits into classification (discrete targets like spam vs not-spam) and regression (continuous values like house prices or revenue).',
 'classification,regression,discrete,continuous,supervised learning');

INSERT INTO QUESTION_BANK (category_id, topic, question_type, difficulty, question_text, option_a, option_b, option_c, option_d, correct_answer, explanation, rubric_keywords) VALUES
(2, 'Feature Engineering & Scaling', 'DESCRIPTIVE', 'Intermediate',
 'Contrast Min-Max Normalization with Z-score Standardization and explain why feature scaling is critical for distance-based algorithms such as K-Nearest Neighbors (KNN) and Gradient Descent optimization.',
 NULL, NULL, NULL, NULL,
 'Min-Max Normalization rescales features into a bounded range [0, 1] using (X - X_min) / (X_max - X_min), but is sensitive to extreme outliers. Z-score Standardization transforms features to have zero mean and unit variance using (X - mean) / std, which handles outliers better. Feature scaling is essential for distance-based algorithms (like KNN and SVM) because features with larger numerical magnitudes would otherwise dominate Euclidean distance calculations. For Gradient Descent, scaling ensures smooth, spherical loss contours, preventing oscillating updates and accelerating parameter convergence.',
 'Normalization scales to [0, 1]; standardization scales to zero mean and unit variance. Unscaled features distort Euclidean distances in KNN and cause slow oscillating gradient descent convergence.',
 'normalization,standardization,min-max,z-score,feature scaling,knn,distance,gradient descent,outliers,convergence');


-- Artificial Intelligence and Machine Learning
INSERT INTO QUESTION_BANK (category_id, topic, question_type, difficulty, question_text, option_a, option_b, option_c, option_d, correct_answer, explanation, rubric_keywords) VALUES
(3, 'Transformer Architectures', 'MCQ', 'Advanced',
 'In the Transformer multi-head attention mechanism, why is the dot product of Query (Q) and Key (K) scaled by 1/sqrt(d_k)?',
 'To reduce computational time complexity from O(n^2) to O(n)', 'To prevent dot products from growing excessively large for large dimensions, which would push softmax into regions with tiny gradients', 'To ensure matrices Q and K remain symmetric positive definite', 'To enforce L2 regularization directly on projection weights',
 'B',
 'For large projection dimensions d_k, dot products grow large in magnitude, driving softmax outputs into saturation where gradients vanish. Dividing by sqrt(d_k) stabilizes backpropagation gradients.',
 'transformer,attention,query,key,softmax,gradients,scaled dot product');

INSERT INTO QUESTION_BANK (category_id, topic, question_type, difficulty, question_text, option_a, option_b, option_c, option_d, correct_answer, explanation, rubric_keywords) VALUES
(3, 'LLM Fine-Tuning & Adaptation', 'DESCRIPTIVE', 'Advanced',
 'Explain Parameter-Efficient Fine-Tuning (PEFT) using Low-Rank Adaptation (LoRA), detailing rank decomposition matrices and how it reduces GPU memory requirements during LLM adaptation.',
 NULL, NULL, NULL, NULL,
 'Traditional fine-tuning updates all billions of model parameters W. LoRA freezes pre-trained weights W0 and decomposes the weight update delta-W into two low-rank matrices A and B: delta-W = B * A, where B is (d x r) and A is (r x k) with rank r << min(d, k). This reduces trainable parameters by 99%+, dramatically diminishing gradient and optimizer state memory on GPUs while retaining comparable downstream task accuracy.',
 'LoRA adapts foundational models by freezing base weights and training minimal low-rank adapter matrices.',
 'lora,peft,rank,decomposition,adapter,frozen,weights,gpu,memory,matrix,d_model');

INSERT INTO QUESTION_BANK (category_id, topic, question_type, difficulty, question_text, option_a, option_b, option_c, option_d, correct_answer, explanation, rubric_keywords) VALUES
(3, 'Deep Learning Optimization', 'MCQ', 'Advanced',
 'Why does the Adam optimizer combine Adaptive Gradient Algorithm (AdaGrad) and Root Mean Square Propagation (RMSprop)?',
 'To replace backpropagation with genetic algorithms', 'To track both the exponentially decaying average of past gradients (first moment) and past squared gradients (second moment), stabilizing updates across sparse features and varying curvatures', 'To guarantee convergence to global minima in non-convex loss surfaces without hyperparameter tuning', 'To eliminate the need for batch normalization in convolutional networks',
 'B',
 'Adam tracks both first moments (momentum) and second moments (uncentered variance of gradients) with bias corrections, adapting learning rates per parameter effectively.',
 'adam,optimizer,adagrad,rmsprop,first moment,second moment,momentum,exponential decay');

INSERT INTO QUESTION_BANK (category_id, topic, question_type, difficulty, question_text, option_a, option_b, option_c, option_d, correct_answer, explanation, rubric_keywords) VALUES
(3, 'Generative AI & Diffusion Models', 'MCQ', 'Advanced',
 'In Denoising Diffusion Probabilistic Models (DDPM), what is the primary role of the neural network during the reverse diffusion process?',
 'To directly reconstruct high-resolution images in a single forward pass without sampling', 'To predict the Gaussian noise epsilon added at timestep t, thereby iteratively subtracting estimated noise to recover the original data distribution', 'To discriminate between synthetic and real images via adversarial minimax loss', 'To compress token embeddings into a lower-dimensional latent space',
 'B',
 'DDPM gradually adds Gaussian noise in the forward process and trains a U-Net to predict the added noise at each step t, allowing iterative reverse denoising.',
 'diffusion,ddpm,reverse process,gaussian noise,denoising,u-net,latent');

INSERT INTO QUESTION_BANK (category_id, topic, question_type, difficulty, question_text, option_a, option_b, option_c, option_d, correct_answer, explanation, rubric_keywords) VALUES
(3, 'RAG Architecture & Embeddings', 'DESCRIPTIVE', 'Advanced',
 'Detail the architecture of an enterprise Retrieval-Augmented Generation (RAG) system, explaining chunking strategies, dense vector vs hybrid search, re-ranking models, and methods to mitigate hallucinations.',
 NULL, NULL, NULL, NULL,
 'Enterprise RAG ingests unstructured documentation via semantic chunking with overlapping windows. Documents are converted into dense embeddings via transformer models and indexed in a vector database. To overcome vocabulary mismatch, Hybrid Search combines dense semantic vectors with BM25 sparse keyword queries (Reciprocal Rank Fusion). A Cross-Encoder re-ranker then refines candidate chunks by scoring query-document pairs simultaneously. The top chunks are injected into the LLM context prompt with strict instructions and guardrails to cite sources and refuse unsupported queries, preventing hallucinations.',
 'RAG combines vector retrieval with language generation. Semantic chunking, hybrid search (dense + BM25), cross-encoder re-ranking, and citation-based grounding minimize hallucinations.',
 'rag,retrieval,chunking,dense,vector,sparse,bm25,hybrid search,re-ranker,cross-encoder,hallucination,embeddings,context');

INSERT INTO QUESTION_BANK (category_id, topic, question_type, difficulty, question_text, option_a, option_b, option_c, option_d, correct_answer, explanation, rubric_keywords) VALUES
(3, 'Unsupervised Learning', 'MCQ', 'Beginner',
 'Which machine learning paradigm learns hidden patterns and cluster groupings from data that lacks human-annotated target labels?',
 'Supervised Learning', 'Unsupervised Learning', 'Reinforcement Learning', 'Active Learning',
 'B',
 'Unsupervised learning discovers intrinsic groupings and representations in unlabeled data (e.g., K-Means clustering, PCA).',
 'unsupervised learning,clustering,unlabeled data');

INSERT INTO QUESTION_BANK (category_id, topic, question_type, difficulty, question_text, option_a, option_b, option_c, option_d, correct_answer, explanation, rubric_keywords) VALUES
(3, 'Activation Functions', 'MCQ', 'Beginner',
 'Which non-linear activation function defined as f(x) = max(0, x) is widely used in deep neural network hidden layers to mitigate vanishing gradients for positive inputs?',
 'Sigmoid', 'ReLU (Rectified Linear Unit)', 'Tanh', 'Softmax',
 'B',
 'ReLU f(x) = max(0, x) has a constant gradient of 1 for all positive inputs, allowing deep networks to train much faster without gradient saturation.',
 'relu,activation function,vanishing gradient,non-linear');

INSERT INTO QUESTION_BANK (category_id, topic, question_type, difficulty, question_text, option_a, option_b, option_c, option_d, correct_answer, explanation, rubric_keywords) VALUES
(3, 'ML Evaluation', 'MCQ', 'Intermediate',
 'Which evaluation metric is most critical when evaluating a machine learning model on an imbalanced classification problem such as fraud detection?',
 'Overall Accuracy', 'F1-Score / PR-AUC', 'Mean Squared Error', 'Adjusted R-squared',
 'B',
 'Accuracy is deceiving under severe imbalance; F1-score balances precision and recall on the minority class.',
 'imbalanced,precision,recall,F1-score');

INSERT INTO QUESTION_BANK (category_id, topic, question_type, difficulty, question_text, option_a, option_b, option_c, option_d, correct_answer, explanation, rubric_keywords) VALUES
(3, 'NLP & Features', 'DESCRIPTIVE', 'Intermediate',
 'Explain how TF-IDF (Term Frequency - Inverse Document Frequency) converts text into numerical vectors and why IDF penalizes common words.',
 NULL, NULL, NULL, NULL,
 'TF measures word frequency within a document. IDF diminishes weights of words frequent across the entire corpus, penalizing non-informative stopwords and accentuating distinctive terms.',
 'TF-IDF weighs term importance by multiplying local occurrence (TF) with corpus-wide rarity (IDF), suppressing common stopwords.',
 'TF-IDF,term frequency,inverse document frequency,stopwords,corpus,weight');

INSERT INTO QUESTION_BANK (category_id, topic, question_type, difficulty, question_text, option_a, option_b, option_c, option_d, correct_answer, explanation, rubric_keywords) VALUES
(3, 'Computer Vision Regularization', 'MCQ', 'Intermediate',
 'What is the primary motivation for applying Data Augmentation (e.g. random cropping, horizontal flipping, affine rotations) during Convolutional Neural Network (CNN) training?',
 'To accelerate GPU backpropagation calculations', 'To artificially synthesize training variability, improving generalizability and preventing overfitting on limited image sets', 'To convert colored RGB images into binary masks', 'To eliminate the need for pooling layers',
 'B',
 'Data augmentation artificially expands training data diversity with invariant transformations, preventing CNN models from overfitting on training samples.',
 'data augmentation,cnn,overfitting,generalization,computer vision');

INSERT INTO QUESTION_BANK (category_id, topic, question_type, difficulty, question_text, option_a, option_b, option_c, option_d, correct_answer, explanation, rubric_keywords) VALUES
(3, 'Recurrent Networks & Memory Gating', 'DESCRIPTIVE', 'Intermediate',
 'Explain why standard Vanilla Recurrent Neural Networks (RNNs) suffer from the vanishing gradient problem over long sequences, and describe how LSTM networks resolve this with Forget, Input, and Output gates.',
 NULL, NULL, NULL, NULL,
 'In Vanilla RNNs, backpropagation through time (BPTT) requires repeated matrix multiplications of weight matrices across sequential timesteps. If eigenvalues are less than 1, gradients decay exponentially to zero, preventing the network from learning long-term temporal dependencies. LSTMs (Long Short-Term Memory) resolve this by introducing an internal Cell State and three regulating gates: 1) Forget Gate: decides what portion of past cell state to discard via a sigmoid layer. 2) Input Gate: decides what new candidate information to store in the cell state. 3) Output Gate: computes the next hidden state based on filtered cell state and tanh activation. The linear additive highway of the cell state allows error gradients to flow across hundreds of timesteps without exponential decay.',
 'Vanilla RNNs suffer from exponential gradient decay during backpropagation through time. LSTMs use an additive cell state controlled by forget, input, and output gates to preserve long-range dependencies.',
 'lstm,rnn,vanishing gradient,bptt,cell state,forget gate,input gate,output gate,temporal,long-term dependencies');


-- Database Development
INSERT INTO QUESTION_BANK (category_id, topic, question_type, difficulty, question_text, option_a, option_b, option_c, option_d, correct_answer, explanation, rubric_keywords) VALUES
(4, 'Oracle Database Tuning', 'DESCRIPTIVE', 'Advanced',
 'Discuss how B-Tree indexes improve SELECT query performance in Oracle Database and state a scenario where an index might be ignored by the cost-based optimizer (CBO).',
 NULL, NULL, NULL, NULL,
 'B-Tree indexes provide balanced tree lookups to fetch RowIDs rapidly. The CBO ignores indexes when wrapping columns in un-indexed functions (e.g. UPPER(name)) or when a full table scan is cheaper due to low selectivity.',
 'B-Tree indexes structure sorted keys with pointers to rowids. CBO skips index when column is wrapped in an un-indexed function or when table is very small.',
 'B-Tree,index,RowID,full table scan,CBO,optimizer,selectivity');

INSERT INTO QUESTION_BANK (category_id, topic, question_type, difficulty, question_text, option_a, option_b, option_c, option_d, correct_answer, explanation, rubric_keywords) VALUES
(4, 'Concurrency & Isolation', 'MCQ', 'Advanced',
 'Under ANSI SQL isolation levels, which phenomenon can occur in Repeatable Read that is strictly prevented under Serializable isolation?',
 'Dirty Reads', 'Non-Repeatable Reads', 'Phantom Reads', 'Lost Updates',
 'C',
 'Repeatable Read locks accessed rows preventing modifications, but does not prevent concurrent transactions from inserting new rows matching the WHERE criteria, resulting in Phantom Reads. Serializable prevents phantoms via predicate or range locking.',
 'repeatable read,serializable,phantom reads,isolation level,locking');

INSERT INTO QUESTION_BANK (category_id, topic, question_type, difficulty, question_text, option_a, option_b, option_c, option_d, correct_answer, explanation, rubric_keywords) VALUES
(4, 'Query Optimization & Cost Modeling', 'DESCRIPTIVE', 'Advanced',
 'Explain how the Oracle Cost-Based Optimizer (CBO) determines whether to use a B-Tree Index Unique Scan, Index Range Scan, or Full Table Scan (FTS), and explain the concept of Clustering Factor.',
 NULL, NULL, NULL, NULL,
 'The CBO calculates I/O and CPU cost using dictionary statistics (data volume, column cardinality, selectivity). An Index Unique Scan is chosen for unique/primary key equality. An Index Range Scan is used for range or non-unique filters with high selectivity. If selectivity is low or the Clustering Factor is high (indicating table rows are scattered across disparate data blocks rather than ordered sequentially with index keys), the CBO determines a Full Table Scan with multi-block read I/O is faster than repeated single-block random index lookups.',
 'High clustering factor signifies index pointers require random disk block reads, prompting the optimizer to favor full table scans.',
 'cbo,cost,optimizer,b-tree,unique,range,full table scan,fts,clustering factor,selectivity,statistics');

INSERT INTO QUESTION_BANK (category_id, topic, question_type, difficulty, question_text, option_a, option_b, option_c, option_d, correct_answer, explanation, rubric_keywords) VALUES
(4, 'Distributed Databases & Consensus', 'MCQ', 'Advanced',
 'Under the Raft consensus algorithm used in modern distributed data stores (e.g., etcd, CockroachDB), what guarantees that a newly elected leader has all committed log entries?',
 'A leader can only be elected if its log is at least as up-to-date as any majority quorum member', 'The leader queries all followers and pulls missing log entries after election', 'The state machine rolls back uncommitted transactions across all nodes upon election', 'Heartbeat intervals are synchronized via GPS atomic clocks',
 'A',
 'Raft ensures the Leader Completeness property by rejecting RequestVote RPCs if the candidate log is less up-to-date than the voter log, guaranteeing leaders always possess all committed entries.',
 'raft,consensus,quorum,leader election,log replication,commit,distributed');

INSERT INTO QUESTION_BANK (category_id, topic, question_type, difficulty, question_text, option_a, option_b, option_c, option_d, correct_answer, explanation, rubric_keywords) VALUES
(4, 'Transaction Durability & ARIES Recovery', 'DESCRIPTIVE', 'Advanced',
 'Explain the ARIES (Algorithms for Recovery and Isolation Exploiting Semantics) database recovery protocol, detailing the Analysis, Redo (Repeating History), and Undo phases following a system crash.',
 NULL, NULL, NULL, NULL,
 'ARIES guarantees atomicity and durability using Write-Ahead Logging (WAL) with physiological logging and Compensation Log Records (CLRs). Post-crash recovery executes three phases: 1) Analysis Phase: scans log forward from the last checkpoint to identify active uncommitted transactions (loser transactions) and dirty pages in buffer pool. 2) Redo Phase: repeats history by scanning forward from the smallest recovery LSN, reapplying changes for all committed and uncommitted transactions to restore the exact pre-crash database state. 3) Undo Phase: scans backward undoing actions of all loser transactions, writing CLRs to ensure that recovery itself is crash-tolerant and never repeats undone actions.',
 'ARIES uses write-ahead logging with three recovery phases: Analysis identifies active transactions, Redo repeats history to restore state, and Undo rolls back incomplete transactions using CLRs.',
 'aries,recovery,wal,write-ahead logging,lsn,analysis,redo,undo,clr,checkpoint,dirty page,atomicity,durability');

INSERT INTO QUESTION_BANK (category_id, topic, question_type, difficulty, question_text, option_a, option_b, option_c, option_d, correct_answer, explanation, rubric_keywords) VALUES
(4, 'SQL Data Manipulation', 'MCQ', 'Beginner',
 'Which SQL DML statement is used to insert one or more new record rows into an existing relational table?',
 'UPDATE', 'INSERT INTO', 'ALTER TABLE', 'SELECT INTO',
 'B',
 'INSERT INTO specifies the target table, columns, and values to add new rows to a database.',
 'insert into,sql,dml,records');

INSERT INTO QUESTION_BANK (category_id, topic, question_type, difficulty, question_text, option_a, option_b, option_c, option_d, correct_answer, explanation, rubric_keywords) VALUES
(4, 'Relational Key Constraints', 'MCQ', 'Beginner',
 'What two primary constraints are automatically enforced on a relational table column designated as a PRIMARY KEY?',
 'CHECK and DEFAULT', 'UNIQUE and NOT NULL', 'FOREIGN KEY and CASCADE', 'AUTOINCREMENT and INDEX only',
 'B',
 'A Primary Key uniquely identifies each row in a table, requiring every value to be strictly UNIQUE and NOT NULL.',
 'primary key,unique,not null,entity integrity');

INSERT INTO QUESTION_BANK (category_id, topic, question_type, difficulty, question_text, option_a, option_b, option_c, option_d, correct_answer, explanation, rubric_keywords) VALUES
(4, 'Database Normalization', 'MCQ', 'Intermediate',
 'What is the fundamental objective of database normalization up to Third Normal Form (3NF)?',
 'Increase data duplication for faster analytics', 'Eliminate redundant data and prevent insert, update, and deletion anomalies', 'Enforce foreign keys without table indexes', 'Convert relational tables into document JSON',
 'B',
 '3NF removes transitive dependencies, ensuring each non-key field depends strictly on the primary key.',
 '3NF,normalization,redundancy,anomalies,transitive dependency');

INSERT INTO QUESTION_BANK (category_id, topic, question_type, difficulty, question_text, option_a, option_b, option_c, option_d, correct_answer, explanation, rubric_keywords) VALUES
(4, 'Transaction ACID Properties', 'MCQ', 'Intermediate',
 'In relational database transactions, what does the ACID acronym stand for?',
 'Availability, Consistency, Isolation, Durability', 'Atomicity, Consistency, Isolation, Durability', 'Atomicity, Concurrency, Indexing, Data-integrity', 'Access, Security, Isolation, Durability',
 'B',
 'ACID stands for Atomicity (all or nothing), Consistency (preserves schema constraints), Isolation (concurrent execution independence), and Durability (committed data persists across crashes).',
 'acid,atomicity,consistency,isolation,durability,transactions');

INSERT INTO QUESTION_BANK (category_id, topic, question_type, difficulty, question_text, option_a, option_b, option_c, option_d, correct_answer, explanation, rubric_keywords) VALUES
(4, 'Database Index Architectures', 'DESCRIPTIVE', 'Intermediate',
 'Compare Clustered Indexes with Non-Clustered Indexes in relational databases, explaining how each affects physical data row organization on disk and query performance.',
 NULL, NULL, NULL, NULL,
 'A Clustered Index dictates the physical on-disk storage order of actual table rows; because rows can only be physically sorted one way on disk, a table can have only one clustered index (typically on the Primary Key). Lookups on the clustered key find the entire data page directly. A Non-Clustered Index is a separate B-Tree data structure containing sorted index keys and pointers (RowIDs or clustered index keys) back to the actual table data rows. A table can possess multiple non-clustered indexes. While non-clustered indexes speed up secondary search filters, retrieving non-indexed columns requires a secondary key lookup or bookmark lookup to fetch the full row.',
 'Clustered indexes define physical data row order on disk (one per table). Non-clustered indexes are separate auxiliary B-Trees pointing to row locations (multiple allowed per table).',
 'clustered index,non-clustered index,b-tree,physical storage,disk,rowid,primary key,lookup');


-- Networking and Cybersecurity
INSERT INTO QUESTION_BANK (category_id, topic, question_type, difficulty, question_text, option_a, option_b, option_c, option_d, correct_answer, explanation, rubric_keywords) VALUES
(5, 'Modern Cryptography & Protocols', 'MCQ', 'Advanced',
 'Why does modern TLS 1.3 mandate Ephemeral Diffie-Hellman (ECDHE) and eliminate static RSA key exchange?',
 'RSA certificates cannot be verified on mobile devices', 'ECDHE guarantees Perfect Forward Secrecy (PFS), ensuring past recorded sessions cannot be decrypted even if the server private key is compromised in the future', 'Diffie-Hellman eliminates the need for Certificate Authorities (CAs)', 'TLS 1.3 strictly prohibits AES symmetric encryption',
 'B',
 'In static RSA exchange, if the server private key is compromised years later, all previously recorded ciphertext sessions can be decrypted. Ephemeral ECDHE generates fresh temporary keys for every session, providing Perfect Forward Secrecy (PFS).',
 'tls,tls 1.3,ecdhe,forward secrecy,pfs,rsa,diffie-hellman');

INSERT INTO QUESTION_BANK (category_id, topic, question_type, difficulty, question_text, option_a, option_b, option_c, option_d, correct_answer, explanation, rubric_keywords) VALUES
(5, 'Zero Trust Architecture', 'DESCRIPTIVE', 'Advanced',
 'Contrast traditional perimeter-based security (castle-and-moat) with Zero Trust Architecture (ZTA), explaining the principle of never trust, always verify and micro-segmentation.',
 NULL, NULL, NULL, NULL,
 'Perimeter security assumes anyone inside the corporate intranet firewall is trustworthy, leaving internal networks vulnerable to lateral movement if the perimeter is breached. Zero Trust operates under the assumption of breach: never trust, always verify. Every access request must be authenticated, authorized, and encrypted based on continuous identity verification, device health telemetry, least-privilege role permissions, and network micro-segmentation to restrict blast radiuses.',
 'Zero Trust enforces continuous dynamic validation rather than implicit location-based trust.',
 'zero trust,perimeter,castle,verify,least privilege,micro-segmentation,identity,iam,mfa,telemetry');

INSERT INTO QUESTION_BANK (category_id, topic, question_type, difficulty, question_text, option_a, option_b, option_c, option_d, correct_answer, explanation, rubric_keywords) VALUES
(5, 'Web Security & XSS Mitigation', 'MCQ', 'Advanced',
 'Which Content Security Policy (CSP) directive strategy provides the most resilient defense against Cross-Site Scripting (XSS) in modern web applications without breaking inline script bundles?',
 'unsafe-inline with wildcard script-src *', 'Nonce-based CSP (script-src ''nonce-{random}'') combined with ''strict-dynamic'' to trust scripts loaded by authorized root scripts', 'Disabling HTTPS and enforcing same-origin headers strictly on CSS stylesheets', 'Relying solely on HTML iframe sandbox attributes',
 'B',
 'Nonce-based CSP with strict-dynamic ensures that only dynamically generated cryptographic one-time tokens execute scripts and propagate trust to child dependencies, preventing injected XSS payloads.',
 'csp,content security policy,nonce,strict-dynamic,xss,inline scripts');

INSERT INTO QUESTION_BANK (category_id, topic, question_type, difficulty, question_text, option_a, option_b, option_c, option_d, correct_answer, explanation, rubric_keywords) VALUES
(5, 'Network Protocol Hardening', 'MCQ', 'Advanced',
 'How do SYN Cookies protect a server against TCP SYN Flood Denial-of-Service attacks without consuming server state memory?',
 'By dropping all incoming TCP packets arriving from external subnets', 'By encoding connection parameters (MSS, timestamp, secret cryptographic hash) into the initial 32-bit TCP Sequence Number (ISN) sent in the SYN-ACK, deferring TCB allocation until the client completes the ACK handshake', 'By executing a CAPTCHA challenge before opening the transport layer socket', 'By re-routing TCP traffic to UDP datagram sockets',
 'B',
 'SYN Cookies encode connection state in the initial sequence number, eliminating half-open connection tables (TCB) until client ACK verification is confirmed.',
 'syn cookies,tcp,syn flood,dos,isn,sequence number,handshake,tcb');

INSERT INTO QUESTION_BANK (category_id, topic, question_type, difficulty, question_text, option_a, option_b, option_c, option_d, correct_answer, explanation, rubric_keywords) VALUES
(5, 'Threat Modeling & Forensics', 'DESCRIPTIVE', 'Advanced',
 'Detail the STRIDE threat modeling framework and explain how digital forensics investigators analyze memory dumps (RAM) using Volatility to detect Advanced Persistent Threats (APTs) employing DLL injection.',
 NULL, NULL, NULL, NULL,
 'STRIDE models security threats into Spoofing (identity), Tampering (data integrity), Repudiation (deniability), Information Disclosure (privacy), Denial of Service (availability), and Elevation of Privilege (authorization). In live incident response, sophisticated APT malware operates filelessly in memory. Investigators capture physical RAM dumps and use Volatility to inspect active process trees (pstree), identify unlinked or hidden processes (psxview), scan for injected virtual memory regions with execute-write permissions (malfind/vadinfo), and detect injected Dynamic Link Libraries (DLLs) through suspicious handles, hooked API import tables, or hollowed process memory.',
 'STRIDE categorizes system threats. Memory forensics with Volatility inspects process memory, VAD permissions, and hollowed processes to detect fileless DLL injection attacks.',
 'stride,threat model,forensics,volatility,ram,memory,apt,dll injection,process hollowing,vad,malfind');

INSERT INTO QUESTION_BANK (category_id, topic, question_type, difficulty, question_text, option_a, option_b, option_c, option_d, correct_answer, explanation, rubric_keywords) VALUES
(5, 'Network Port Protocols', 'MCQ', 'Beginner',
 'Which standard transport-layer port is officially designated for secure, encrypted web communication via HTTPS (TLS/SSL)?',
 'Port 80', 'Port 443', 'Port 22', 'Port 8080',
 'B',
 'Port 443 is standard for HTTPS encrypted traffic; Port 80 is used for unencrypted HTTP; Port 22 is for SSH.',
 'port 443,https,tls,ssl,port 80,network ports');

INSERT INTO QUESTION_BANK (category_id, topic, question_type, difficulty, question_text, option_a, option_b, option_c, option_d, correct_answer, explanation, rubric_keywords) VALUES
(5, 'Network Firewalls', 'MCQ', 'Beginner',
 'What is the primary security function of an enterprise network firewall?',
 'To compile source code into executable binary packages', 'To inspect, monitor, and filter incoming and outgoing network traffic based on predefined security rules and IP/port policies', 'To accelerate Wi-Fi wireless broadcast signals', 'To assign dynamic IP addresses via DHCP',
 'B',
 'Firewalls establish a defensive perimeter boundary between trusted internal networks and untrusted external networks by filtering traffic packets against security policies.',
 'firewall,network security,filtering,packets,rules,perimeter');

INSERT INTO QUESTION_BANK (category_id, topic, question_type, difficulty, question_text, option_a, option_b, option_c, option_d, correct_answer, explanation, rubric_keywords) VALUES
(5, 'Symmetric vs Asymmetric Encryption', 'MCQ', 'Intermediate',
 'What is the fundamental architectural difference between Symmetric Encryption (e.g. AES) and Asymmetric Encryption (e.g. RSA)?',
 'Symmetric encryption only works on plain text strings shorter than 128 characters', 'Symmetric uses a single shared secret key for both encryption and decryption; Asymmetric uses a mathematically linked public-private key pair', 'Asymmetric encryption does not require mathematical keys', 'Symmetric encryption cannot be executed on Linux systems',
 'B',
 'Symmetric cryptography shares one private secret key (fast, high throughput). Asymmetric cryptography uses a public key for encryption and a distinct private key for decryption (ideal for key exchanges and digital signatures).',
 'symmetric,asymmetric,aes,rsa,encryption,decryption,public key,private key');

INSERT INTO QUESTION_BANK (category_id, topic, question_type, difficulty, question_text, option_a, option_b, option_c, option_d, correct_answer, explanation, rubric_keywords) VALUES
(5, 'Web Application Security & SQLi', 'DESCRIPTIVE', 'Intermediate',
 'Explain how SQL Injection (SQLi) vulnerabilities arise in web applications and why parameterized queries (prepared statements) fundamentally neutralize this attack vector.',
 NULL, NULL, NULL, NULL,
 'SQL Injection occurs when untrusted user input is directly concatenated into SQL query strings without sanitization. An attacker injects SQL control characters (such as '' OR ''1''=''1) to alter query logic, bypass authentication, or exfiltrate database contents. Parameterized queries (prepared statements) completely eliminate SQLi because the database compiles the SQL query structure and command template first with placeholders before binding user inputs. The database engine treats bound parameters strictly as literal literal data values, never executing user data as executable SQL commands, regardless of what characters are supplied.',
 'SQLi occurs from dynamic string concatenation. Prepared statements separate query structure from parameters, ensuring input is treated strictly as data and cannot modify SQL execution logic.',
 'sql injection,sqli,parameterized query,prepared statement,sanitization,concatenation,input,payload,syntax');


-- Cloud Computing and DevOps
INSERT INTO QUESTION_BANK (category_id, topic, question_type, difficulty, question_text, option_a, option_b, option_c, option_d, correct_answer, explanation, rubric_keywords) VALUES
(6, 'Kubernetes Internals', 'MCQ', 'Advanced',
 'In Kubernetes, what component is responsible for monitoring Pod specifications and reconciling the actual container state on an individual worker node?',
 'kube-controller-manager', 'kubelet', 'etcd', 'kube-scheduler',
 'B',
 'The kubelet is the primary node agent that registers the node with the apiserver, watches PodSpecs, and interacts with the container runtime (CRI) to ensure the specified containers are running and healthy.',
 'kubernetes,kubelet,worker node,podspec,cri,runtime');

INSERT INTO QUESTION_BANK (category_id, topic, question_type, difficulty, question_text, option_a, option_b, option_c, option_d, correct_answer, explanation, rubric_keywords) VALUES
(6, 'Deployment Strategies & Reliability', 'DESCRIPTIVE', 'Advanced',
 'Compare Blue-Green Deployments with Canary Deployments, detailing traffic routing mechanisms, rollback speeds, and how distributed database schema migrations (expand-contract pattern) must be handled.',
 NULL, NULL, NULL, NULL,
 'Blue-Green runs two identical production environments; traffic is cut over 100% via a load balancer/DNS once green passes smoke tests, allowing instantaneous rollback by switching the router back to blue. Canary routes a small percentage of traffic (e.g. 5%) to new instances while monitoring error rates, gradually scaling traffic to 100%. For database migrations, schema changes must use the Expand-Contract (Parallel Run) pattern: first expand the schema backward-compatibly (adding columns/tables without removing old ones), deploy code that writes to both or reads from new, then contract (drop obsolete columns) only after old versions are decommissioned.',
 'Decoupling schema migrations via expand-contract prevents breaking previous versions during phased rollouts.',
 'blue-green,canary,traffic,rollback,expand-contract,schema,backward,compatible,database,router');

INSERT INTO QUESTION_BANK (category_id, topic, question_type, difficulty, question_text, option_a, option_b, option_c, option_d, correct_answer, explanation, rubric_keywords) VALUES
(6, 'Service Mesh & Cloud Networking', 'MCQ', 'Advanced',
 'In a Kubernetes Service Mesh (e.g., Istio, Linkerd), how is mutual TLS (mTLS) and traffic management typically implemented between microservices?',
 'By configuring hardware firewall appliances outside the Kubernetes cluster', 'By injecting an Envoy sidecar proxy into each application Pod to intercept inbound and outbound pod network traffic transparently', 'By recompiling application source code with custom cryptographic libraries', 'By running all microservices within a single shared container image',
 'B',
 'A service mesh injects sidecar proxies (like Envoy) using iptables redirection to handle mTLS encryption, traffic routing, rate limiting, and observability without application code modifications.',
 'service mesh,istio,envoy,sidecar,mtls,kubernetes,traffic management');

INSERT INTO QUESTION_BANK (category_id, topic, question_type, difficulty, question_text, option_a, option_b, option_c, option_d, correct_answer, explanation, rubric_keywords) VALUES
(6, 'Chaos Engineering & Resilience', 'MCQ', 'Advanced',
 'What is the primary objective of Chaos Engineering practices (e.g. Chaos Monkey, LitmusChaos) in cloud architectures?',
 'To intentionally cause catastrophic downtime during peak customer business hours', 'To proactively identify systemic vulnerabilities and validate automated recovery mechanisms by injecting controlled failures into production environments before unpredictable outages occur', 'To bypass integration testing and deploy code directly without code reviews', 'To stress test hardware CPU clock speeds beyond manufacturer limits',
 'B',
 'Chaos Engineering builds confidence in system resilience by testing hypotheses about system behavior under turbulent conditions and verifying self-healing mechanisms.',
 'chaos engineering,chaos monkey,resilience,fault injection,availability,self-healing');

INSERT INTO QUESTION_BANK (category_id, topic, question_type, difficulty, question_text, option_a, option_b, option_c, option_d, correct_answer, explanation, rubric_keywords) VALUES
(6, 'SRE & Observability Engineering', 'DESCRIPTIVE', 'Advanced',
 'Compare the Three Pillars of Observability (Metrics, Distributed Tracing, Logs) and explain how Site Reliability Engineering (SRE) teams establish Service Level Objectives (SLOs) and Error Budgets to balance feature velocity with system reliability.',
 NULL, NULL, NULL, NULL,
 'The Three Pillars of Observability provide comprehensive system visibility: Metrics (aggregated numerical time-series for trend detection and alerting), Distributed Tracing (request lifecycle propagation across microservices with spans and latency breakdowns for bottleneck diagnosis), and Logs (context-rich event timestamps for root-cause analysis). SRE operationalizes reliability by defining Service Level Indicators (SLIs - quantifiable metrics like 99th percentile latency), establishing Service Level Objectives (SLOs - target reliability goals such as 99.9% success rate), and creating Error Budgets (100% - SLO). The Error Budget serves as an objective governance tool: when the error budget is healthy, developers can ship features aggressively; when the budget is depleted by incidents, feature releases freeze and engineering priorities shift to reliability and stability.',
 'Observability utilizes metrics, traces, and logs. SRE uses SLIs, SLOs, and Error Budgets to objectively balance new feature deployment velocity with system availability and stability.',
 'sre,observability,metrics,tracing,logs,distributed tracing,sli,slo,error budget,reliability,latency,governance');

INSERT INTO QUESTION_BANK (category_id, topic, question_type, difficulty, question_text, option_a, option_b, option_c, option_d, correct_answer, explanation, rubric_keywords) VALUES
(6, 'Cloud Computing Service Models', 'MCQ', 'Beginner',
 'Which cloud service model provides virtualized compute instances, raw storage volumes, and network routing where the customer is responsible for managing the guest OS, runtime, and applications?',
 'SaaS (Software as a Service)', 'IaaS (Infrastructure as a Service)', 'PaaS (Platform as a Service)', 'FaaS (Function as a Service)',
 'B',
 'IaaS provides fundamental compute, storage, and networking resources (e.g. AWS EC2, GCP Compute Engine). PaaS manages runtimes; SaaS delivers full end-user software.',
 'iaas,paas,saas,cloud models,infrastructure,virtual machine');

INSERT INTO QUESTION_BANK (category_id, topic, question_type, difficulty, question_text, option_a, option_b, option_c, option_d, correct_answer, explanation, rubric_keywords) VALUES
(6, 'Git Version Control', 'MCQ', 'Beginner',
 'In Git version control, which command moves modified files from the working directory to the staging area in preparation for a commit?',
 'git push', 'git add', 'git checkout', 'git stash',
 'B',
 'git add stages working tree modifications, indexing changes to be included in the next commit snapshot.',
 'git,git add,staging,version control,commit');

INSERT INTO QUESTION_BANK (category_id, topic, question_type, difficulty, question_text, option_a, option_b, option_c, option_d, correct_answer, explanation, rubric_keywords) VALUES
(6, 'Containers vs VMs', 'MCQ', 'Intermediate',
 'What is the core architectural difference between Docker containers and traditional Virtual Machines (VMs)?',
 'VMs share the host OS kernel, while containers package a dedicated guest OS kernel', 'Containers share the host operating system kernel and isolate user spaces, resulting in lightweight execution', 'Containers require dedicated hardware hypervisors (Type 1)', 'Virtual machines cannot run on Linux servers',
 'B',
 'Containers isolate processes using host kernel namespaces/cgroups, whereas VMs virtualize physical hardware with a hypervisor and full guest OS.',
 'containers,docker,host kernel,virtual machine,hypervisor');

INSERT INTO QUESTION_BANK (category_id, topic, question_type, difficulty, question_text, option_a, option_b, option_c, option_d, correct_answer, explanation, rubric_keywords) VALUES
(6, 'Infrastructure as Code (IaC)', 'MCQ', 'Intermediate',
 'What is the primary advantage of utilizing Infrastructure as Code (IaC) tools like Terraform or CloudFormation over manual cloud console provisioning?',
 'It eliminates the need for cloud billing accounts', 'It codifies cloud resources into declarative, version-controlled definitions that enable automated, repeatable, and drift-free environment deployments', 'It forces all virtual machines to run Windows Server OS', 'It prevents developers from using command-line terminals',
 'B',
 'IaC provides declarative state management, versioning, automated provisioning, and consistent replication across development, staging, and production environments.',
 'iac,infrastructure as code,terraform,declarative,automation,reproducibility');

INSERT INTO QUESTION_BANK (category_id, topic, question_type, difficulty, question_text, option_a, option_b, option_c, option_d, correct_answer, explanation, rubric_keywords) VALUES
(6, 'CI/CD Pipelines & Automation', 'DESCRIPTIVE', 'Intermediate',
 'Explain the difference between Continuous Integration (CI), Continuous Delivery (CD), and Continuous Deployment, outlining the typical automated pipeline stages from code commit to production release.',
 NULL, NULL, NULL, NULL,
 'Continuous Integration (CI) is the practice where developers regularly merge code into a shared repository, triggering automated builds, linters, static analysis, and unit test suites to catch regressions early. Continuous Delivery extends CI by automatically packaging artifacts and staging deployment to test environments, ensuring code is always in a releasable state, but requiring manual human approval for production deployment. Continuous Deployment automates the entire journey end-to-end: every change that passes all automated tests deploys automatically to production without human intervention. A standard pipeline includes: 1) Source/Trigger (git push), 2) Build/Compile (dependencies and container image building), 3) Test (unit, integration, and security scans), 4) Staging Verification (smoke and end-to-end tests), and 5) Production Release (canary or blue-green rollout with automated health checks).',
 'CI automates build and test on code merge. Continuous Delivery ensures code is always releasable to production with manual gate. Continuous Deployment automatically ships every passing commit to production.',
 'ci,cd,continuous integration,continuous delivery,continuous deployment,pipeline,build,test,staging,production,automation,regression');


-- 5. Insert Aptitude Test Questions (MCQs: Quantitative, Logical, Verbal)

-- Logical Section
INSERT INTO QUESTION_BANK (topic, question_type, difficulty, aptitude_section, question_text, option_a, option_b, option_c, option_d, correct_answer, explanation) VALUES
('Number Series', 'APTITUDE', 'Beginner', 'Logical',
 'Find the missing number in the sequence: 4, 9, 19, 39, 79, ?',
 '119', '139', '159', '169',
 'C',
 'Rule: (term * 2) + 1. (79 * 2) + 1 = 159.');

INSERT INTO QUESTION_BANK (topic, question_type, difficulty, aptitude_section, question_text, option_a, option_b, option_c, option_d, correct_answer, explanation) VALUES
('Coding-Decoding', 'APTITUDE', 'Intermediate', 'Logical',
 'If the word PYTHON is coded as QZWIPM, how would FLASK be coded following the same character shifting (+1, -1, +1, -1...)?',
 'GKBTL', 'GMBTL', 'GKZTL', 'GMZTL',
 'A',
 'Applying alternating character shift yields GKBTL.');

INSERT INTO QUESTION_BANK (topic, question_type, difficulty, aptitude_section, question_text, option_a, option_b, option_c, option_d, correct_answer, explanation) VALUES
('Syllogisms', 'APTITUDE', 'Intermediate', 'Logical',
 'Statements: All developers write code. Some developers are architects. Conclusions: I. Some code writers are architects. II. All architects are developers.',
 'Only Conclusion I follows', 'Only Conclusion II follows', 'Both follow', 'Neither follows',
 'A',
 'Since all developers write code and some are architects, those architects are code writers. Only Conclusion I follows logically.');

INSERT INTO QUESTION_BANK (topic, question_type, difficulty, aptitude_section, question_text, option_a, option_b, option_c, option_d, correct_answer, explanation) VALUES
('Direction Sense', 'APTITUDE', 'Beginner', 'Logical',
 'Starting from office, Priya walks 10m North, turns Right and walks 15m, turns Right again and walks 10m. How far is she from the starting point?',
 '15m East', '15m West', '10m South', '25m North',
 'A',
 'The north and south paths cancel out, placing her 15m directly East of the origin.');

INSERT INTO QUESTION_BANK (topic, question_type, difficulty, aptitude_section, question_text, option_a, option_b, option_c, option_d, correct_answer, explanation) VALUES
('Blood Relations', 'APTITUDE', 'Intermediate', 'Logical',
 'Pointing to a photograph, Rohit says, ''She is the daughter of the only son of my grandfather.'' How is the woman in the photograph related to Rohit?',
 'Sister', 'Aunt', 'Mother', 'Niece',
 'A',
 'Rohit''s grandfather''s only son is Rohit''s father. The daughter of Rohit''s father is Rohit''s sister.');

INSERT INTO QUESTION_BANK (topic, question_type, difficulty, aptitude_section, question_text, option_a, option_b, option_c, option_d, correct_answer, explanation) VALUES
('Clock Angles', 'APTITUDE', 'Intermediate', 'Logical',
 'What is the acute angle between the hour hand and the minute hand of an analog clock at 3:30?',
 '60 degrees', '75 degrees', '80 degrees', '90 degrees',
 'B',
 'Angle = |30*H - 5.5*M| = |30*3 - 5.5*30| = |90 - 165| = 75 degrees.');

INSERT INTO QUESTION_BANK (topic, question_type, difficulty, aptitude_section, question_text, option_a, option_b, option_c, option_d, correct_answer, explanation) VALUES
('Seating Arrangements', 'APTITUDE', 'Intermediate', 'Logical',
 'Six engineers (A, B, C, D, E, F) sit in a row facing North. C sits between A and E. D is to the immediate right of E. B is at the extreme left. Who sits between B and A?',
 'F', 'C', 'D', 'E',
 'A',
 'The seating arrangement from left to right is: B, F, A, C, E, D. Therefore, F sits between B and A.');

INSERT INTO QUESTION_BANK (topic, question_type, difficulty, aptitude_section, question_text, option_a, option_b, option_c, option_d, correct_answer, explanation) VALUES
('Critical Assumptions', 'APTITUDE', 'Intermediate', 'Logical',
 'Statement: ''To improve sprint delivery velocity, the DevOps team should implement automated CI/CD pipelines.'' Assumption I: Current manual deployments cause delivery bottlenecks. Assumption II: Automated pipelines reduce deployment errors.',
 'Only Assumption I is implicit', 'Only Assumption II is implicit', 'Both Assumptions I and II are implicit', 'Neither is implicit',
 'C',
 'Recommending automated CI/CD assumes that manual deployments currently hinder velocity and that automation remediates errors to improve delivery speed.');

INSERT INTO QUESTION_BANK (topic, question_type, difficulty, aptitude_section, question_text, option_a, option_b, option_c, option_d, correct_answer, explanation) VALUES
('System Analogies', 'APTITUDE', 'Beginner', 'Logical',
 'Compiler : Machine Code :: Interpreter : ?',
 'Source Code', 'Bytecode / Direct Execution', 'Assembler', 'Linker',
 'B',
 'A compiler translates entire high-level code into machine code, while an interpreter directly executes instructions or translates into intermediate bytecode.');

INSERT INTO QUESTION_BANK (topic, question_type, difficulty, aptitude_section, question_text, option_a, option_b, option_c, option_d, correct_answer, explanation) VALUES
('Letter-Number Coding', 'APTITUDE', 'Beginner', 'Logical',
 'If CLOUD is coded as 3-12-15-21-4 and DEV is coded as 4-5-22, how is the word OPS coded using standard alphabet positions?',
 '14-15-18', '15-16-19', '15-17-19', '16-17-20',
 'B',
 'Using 1-based alphabet positions: O = 15, P = 16, S = 19. Hence, 15-16-19.');


-- Quantitative Section
INSERT INTO QUESTION_BANK (topic, question_type, difficulty, aptitude_section, question_text, option_a, option_b, option_c, option_d, correct_answer, explanation) VALUES
('Arithmetic & Rates', 'APTITUDE', 'Intermediate', 'Quantitative',
 'A train running at 54 km/hr crosses a platform of length 250 meters in 30 seconds. What is the length of the train in meters?',
 '150 meters', '200 meters', '250 meters', '300 meters',
 'B',
 'Speed in m/s = 54 * (5/18) = 15 m/s. Total distance in 30s = 15 * 30 = 450m. Train length = 450 - 250 = 200m.');

INSERT INTO QUESTION_BANK (topic, question_type, difficulty, aptitude_section, question_text, option_a, option_b, option_c, option_d, correct_answer, explanation) VALUES
('Percentages & Profit', 'APTITUDE', 'Intermediate', 'Quantitative',
 'An article is sold for $840 at a gain of 20%. What was its initial cost price?',
 '$680', '$700', '$720', '$750',
 'B',
 'Cost Price = Selling Price / 1.20 = 840 / 1.20 = $700.');

INSERT INTO QUESTION_BANK (topic, question_type, difficulty, aptitude_section, question_text, option_a, option_b, option_c, option_d, correct_answer, explanation) VALUES
('Time & Work', 'APTITUDE', 'Intermediate', 'Quantitative',
 'Worker A can complete a project in 12 days and Worker B can complete it in 24 days. Working together, how many days will it take?',
 '6 days', '8 days', '9 days', '10 days',
 'B',
 'Combined daily rate = 1/12 + 1/24 = 3/24 = 1/8. Together they take 8 days.');

INSERT INTO QUESTION_BANK (topic, question_type, difficulty, aptitude_section, question_text, option_a, option_b, option_c, option_d, correct_answer, explanation) VALUES
('Ratios & Proportions', 'APTITUDE', 'Beginner', 'Quantitative',
 'The ratio of boys to girls in a computer science class is 5:3. If there are 40 students in total, how many girls are in the class?',
 '12', '15', '20', '25',
 'B',
 'Each ratio part = 40 / (5+3) = 5. Girls = 3 * 5 = 15.');

INSERT INTO QUESTION_BANK (topic, question_type, difficulty, aptitude_section, question_text, option_a, option_b, option_c, option_d, correct_answer, explanation) VALUES
('Probability', 'APTITUDE', 'Intermediate', 'Quantitative',
 'Two standard six-sided dice are rolled simultaneously. What is the probability that the sum of numbers equals 7?',
 '1/12', '1/6', '5/36', '7/36',
 'B',
 'There are 6 favorable outcomes out of 36 total possibilities. 6/36 = 1/6.');

INSERT INTO QUESTION_BANK (topic, question_type, difficulty, aptitude_section, question_text, option_a, option_b, option_c, option_d, correct_answer, explanation) VALUES
('Compound Interest', 'APTITUDE', 'Intermediate', 'Quantitative',
 'A sum of money invested at 10% compound interest compounded annually becomes ,420 in 2 years. What was the principal amount invested?',
 ',800', ',000', ',100', ',200',
 'B',
 'Amount = P * (1 + r/100)^t => 2420 = P * (1.10)^2 => P = 2420 / 1.21 = ,000.');

INSERT INTO QUESTION_BANK (topic, question_type, difficulty, aptitude_section, question_text, option_a, option_b, option_c, option_d, correct_answer, explanation) VALUES
('Pipes & Cisterns', 'APTITUDE', 'Intermediate', 'Quantitative',
 'Pipe A can fill a water tank in 4 hours, and Pipe B can fill it in 6 hours. If both pipes operate simultaneously, how long will it take to fill the tank completely?',
 '2 hours', '2 hours 24 minutes', '2 hours 45 minutes', '3 hours',
 'B',
 'Combined rate = 1/4 + 1/6 = 5/12 tank/hr. Total time = 12/5 hrs = 2.4 hrs = 2 hours 24 minutes.');

INSERT INTO QUESTION_BANK (topic, question_type, difficulty, aptitude_section, question_text, option_a, option_b, option_c, option_d, correct_answer, explanation) VALUES
('Boats & Streams', 'APTITUDE', 'Intermediate', 'Quantitative',
 'A motorboat travels upstream against the river current at 12 km/h and downstream with the current at 20 km/h. What is the speed of the river stream?',
 '3 km/h', '4 km/h', '5 km/h', '6 km/h',
 'B',
 'Speed of stream = (Downstream speed - Upstream speed) / 2 = (20 - 12) / 2 = 4 km/h.');

INSERT INTO QUESTION_BANK (topic, question_type, difficulty, aptitude_section, question_text, option_a, option_b, option_c, option_d, correct_answer, explanation) VALUES
('Averages & Teams', 'APTITUDE', 'Beginner', 'Quantitative',
 'The average age of 5 software engineers in a squad is 28 years. When the Tech Lead joins the squad, the average age increases to 30 years. What is the age of the Tech Lead?',
 '36 years', '40 years', '42 years', '45 years',
 'B',
 'Total age of 6 members = 6 * 30 = 180. Total age of 5 engineers = 5 * 28 = 140. Tech lead age = 180 - 140 = 40 years.');

INSERT INTO QUESTION_BANK (topic, question_type, difficulty, aptitude_section, question_text, option_a, option_b, option_c, option_d, correct_answer, explanation) VALUES
('Permutations', 'APTITUDE', 'Intermediate', 'Quantitative',
 'In how many distinct ways can the letters of the word ''REACT'' be arranged?',
 '60', '120', '240', '720',
 'B',
 'The word REACT has 5 distinct letters. Number of permutations = 5! = 5 * 4 * 3 * 2 * 1 = 120.');

INSERT INTO QUESTION_BANK (topic, question_type, difficulty, aptitude_section, question_text, option_a, option_b, option_c, option_d, correct_answer, explanation) VALUES
('Percentage Changes', 'APTITUDE', 'Intermediate', 'Quantitative',
 'A tech company increased its developer headcount by 25% in Q1, and subsequently reduced it by 20% in Q2. What was the net percentage change in headcount?',
 '+5% increase', '0% (No net change)', '-5% decrease', '+2.5% increase',
 'B',
 'Net multiplier = (1 + 0.25) * (1 - 0.20) = 1.25 * 0.80 = 1.00. Hence, net change is 0%.');


-- Verbal Section
INSERT INTO QUESTION_BANK (topic, question_type, difficulty, aptitude_section, question_text, option_a, option_b, option_c, option_d, correct_answer, explanation) VALUES
('Sentence Correction', 'APTITUDE', 'Intermediate', 'Verbal',
 'Choose the grammatically correct sentence:',
 'Neither the database administrator nor the developers was present at the incident review.', 'Neither the database administrator nor the developers were present at the incident review.', 'Neither the database administrator or the developers were present at the incident review.', 'Neither the database administrator nor the developers has been present at the incident review.',
 'B',
 'In neither...nor constructions, the verb agrees with the closer subject (''developers'' plural).');

INSERT INTO QUESTION_BANK (topic, question_type, difficulty, aptitude_section, question_text, option_a, option_b, option_c, option_d, correct_answer, explanation) VALUES
('Vocabulary & Synonyms', 'APTITUDE', 'Intermediate', 'Verbal',
 'Select the closest synonym for the word PRAGMATIC in a professional engineering context:',
 'Theoretical', 'Idealistic', 'Practical and outcome-oriented', 'Speculative',
 'C',
 'Pragmatic means practical, sensible, and focused on real-world outcomes.');

INSERT INTO QUESTION_BANK (topic, question_type, difficulty, aptitude_section, question_text, option_a, option_b, option_c, option_d, correct_answer, explanation) VALUES
('Antonyms', 'APTITUDE', 'Beginner', 'Verbal',
 'Choose the word that is most opposite in meaning to OBSOLETE:',
 'Redundant', 'Contemporary', 'Ancient', 'Archaic',
 'B',
 'Obsolete means outdated; contemporary means current or modern.');

INSERT INTO QUESTION_BANK (topic, question_type, difficulty, aptitude_section, question_text, option_a, option_b, option_c, option_d, correct_answer, explanation) VALUES
('Idioms in Workplace', 'APTITUDE', 'Intermediate', 'Verbal',
 'In professional team communication, what does the idiom ''Bite the bullet'' mean?',
 'Cancel a release abruptly', 'Face an inevitable, difficult situation with courage', 'Blame others for an outage', 'Celebrate a production milestone',
 'B',
 'To bite the bullet means to accept or confront a grim, difficult, or painful situation bravely.');

INSERT INTO QUESTION_BANK (topic, question_type, difficulty, aptitude_section, question_text, option_a, option_b, option_c, option_d, correct_answer, explanation) VALUES
('Reading Inference', 'APTITUDE', 'Intermediate', 'Verbal',
 'Passage: ''Microservices allow teams to deploy independent services. However, without centralized distributed tracing and strict interface versioning, systemic complexity quickly exceeds the cognitive capacity of squads.'' What can be logically inferred?',
 'Microservices eliminate the need for engineering squads', 'Autonomous microservices require observability and interface discipline to manage architectural complexity', 'Monoliths are always superior to microservices', 'Database schema changes never affect microservices',
 'B',
 'The passage directly emphasizes that independent microservices need distributed tracing and interface versioning to keep architectural complexity manageable.');

INSERT INTO QUESTION_BANK (topic, question_type, difficulty, aptitude_section, question_text, option_a, option_b, option_c, option_d, correct_answer, explanation) VALUES
('Spotting Grammatical Errors', 'APTITUDE', 'Intermediate', 'Verbal',
 'Identify the sentence segment containing a grammatical error: (A) Each of the software candidates / (B) have completed their / (C) technical assessment / (D) within the allocated timeframe.',
 'Segment A', 'Segment B', 'Segment C', 'Segment D',
 'B',
 '''Each'' is an indefinite singular pronoun and requires the singular verb ''has completed'', not ''have completed''.');

INSERT INTO QUESTION_BANK (topic, question_type, difficulty, aptitude_section, question_text, option_a, option_b, option_c, option_d, correct_answer, explanation) VALUES
('Sentence Completion', 'APTITUDE', 'Beginner', 'Verbal',
 'The comprehensive security audit uncovered several critical vulnerabilities that demanded _______ remediation to prevent sensitive data leakage.',
 'negligent', 'prompt and decisive', 'sluggish', 'redundant',
 'B',
 '''Prompt and decisive'' appropriately fits the urgent context of mitigating critical security vulnerabilities.');

INSERT INTO QUESTION_BANK (topic, question_type, difficulty, aptitude_section, question_text, option_a, option_b, option_c, option_d, correct_answer, explanation) VALUES
('Synonyms in Engineering', 'APTITUDE', 'Beginner', 'Verbal',
 'Choose the closest synonym for the word RESILIENT in the context of cloud systems architecture:',
 'Fragile', 'Robust and fault-tolerant', 'Volatile', 'Rigid',
 'B',
 'A resilient cloud architecture is robust, fault-tolerant, and capable of recovering quickly from disruptions.');

INSERT INTO QUESTION_BANK (topic, question_type, difficulty, aptitude_section, question_text, option_a, option_b, option_c, option_d, correct_answer, explanation) VALUES
('Sentence Sequencing', 'APTITUDE', 'Intermediate', 'Verbal',
 'Rearrange the phrases into a coherent logical sequence: (P) It triggers automated test suites. (Q) The developer pushes code to git. (R) Build artifacts deploy to staging. (S) The CI pipeline starts execution.',
 'Q-S-P-R', 'S-Q-R-P', 'Q-P-S-R', 'P-Q-S-R',
 'A',
 'Logical workflow: Developer pushes code (Q) -> CI pipeline starts (S) -> Automated tests run (P) -> Artifacts deploy to staging (R).');

-- 6. Insert Learning Resources for Closed-Loop Recommendations
INSERT INTO LEARNING_RESOURCE (category_id, topic, title, resource_url, resource_type, description) VALUES
(1, 'Backend & APIs', 'Architecting RESTful Web APIs: Best Practices', 'https://restfulapi.net/', 'Guide', 'Comprehensive principles for designing clean, idempotent, scalable HTTP APIs.');

INSERT INTO LEARNING_RESOURCE (category_id, topic, title, resource_url, resource_type, description) VALUES
(1, 'OOP & Programming', 'Clean Architecture and SOLID Design Principles', 'https://refactoring.guru/design-patterns', 'Interactive Book', 'Master object-oriented patterns, encapsulation, and maintainable software design.');

INSERT INTO LEARNING_RESOURCE (category_id, topic, title, resource_url, resource_type, description) VALUES
(2, 'Python Data Analysis', 'Pandas Complete Data Wrangling Bootcamp', 'https://pandas.pydata.org/docs/getting_started/index.html', 'Documentation', 'Essential methods for filtering, aggregating, handling missing values, and reshaping data.');

INSERT INTO LEARNING_RESOURCE (category_id, topic, title, resource_url, resource_type, description) VALUES
(3, 'ML Evaluation', 'Model Evaluation & Imbalanced Class Metrics in scikit-learn', 'https://scikit-learn.org/stable/modules/model_evaluation.html', 'Tutorial', 'Learn why accuracy is misleading in imbalanced problems and how to use Precision-Recall curves.');

INSERT INTO LEARNING_RESOURCE (category_id, topic, title, resource_url, resource_type, description) VALUES
(4, 'SQL & RDBMS', 'Oracle Database SQL Tuning and B-Tree Indexing Guide', 'https://docs.oracle.com/en/database/oracle/oracle-database/', 'Official Documentation', 'Deep-dive into cost-based query optimization, execution plans, and index architectures.');

INSERT INTO LEARNING_RESOURCE (category_id, topic, title, resource_url, resource_type, description) VALUES
(6, 'DevOps & Containers', 'Docker & Containerization Architectural Foundations', 'https://docs.docker.com/get-started/', 'Practical Lab', 'Understand namespaces, cgroups, layered storage, and container orchestration.');

INSERT INTO LEARNING_RESOURCE (NULL, 'Quantitative', 'Quantitative Aptitude for Campus Placements & Competitive Exams', 'https://www.indiabix.com/aptitude/questions-and-answers/', 'Practice Bank', 'Step-by-step arithmetic, ratios, speed, time, and algebra problem-solving strategies.');

INSERT INTO LEARNING_RESOURCE (NULL, 'Logical', 'Logical Reasoning Mastery: Series, Syllogisms, and Deduction', 'https://www.indiabix.com/logical-reasoning/questions-and-answers/', 'Practice Bank', 'Structured techniques to solve coding patterns, direction puzzles, and logical relations.');

INSERT INTO LEARNING_RESOURCE (NULL, 'Verbal', 'Grammar, Subject-Verb Concord, and Professional Vocabulary', 'https://www.indiabix.com/verbal-ability/questions-and-answers/', 'Practice Bank', 'Refine sentence mechanics, corporate communication vocabulary, and reading comprehension.');

COMMIT;
