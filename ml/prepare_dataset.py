"""
Dataset preparation script for Technical Skill Categorization.
Generates a representative, labeled training dataset of technical resume profiles across 6 core domains.
"""
import os
import pandas as pd
from pathlib import Path

DATASET_DIR = Path(__file__).resolve().parent / "dataset"
DATASET_DIR.mkdir(parents=True, exist_ok=True)
DATASET_FILE = DATASET_DIR / "resume_data.csv"

def generate_dataset():
    data = [
        # --- 1. Software and Web Development ---
        {"category": "Software and Web Development", "text": "Full stack developer with 3 years experience building scalable web applications using Python Flask Django React JavaScript and PostgreSQL. Designed RESTful APIs, optimized state management with Redux, and built responsive UI components using HTML5 CSS3."},
        {"category": "Software and Web Development", "text": "Frontend engineer specialized in React TypeScript Tailwind CSS and Next.js. Engineered interactive client interfaces, single page applications (SPAs), implemented WebSockets for live chat, and ensured WCAG accessibility."},
        {"category": "Software and Web Development", "text": "Backend software engineer proficient in Java Spring Boot Microservices REST APIs and Hibernate. Built resilient service mesh, automated unit testing with JUnit and Mockito, and integrated Redis cache."},
        {"category": "Software and Web Development", "text": "Junior web developer with strong foundation in JavaScript Node.js Express HTML5 CSS3 and MongoDB. Created e-commerce prototype with shopping cart, user authentication, and Stripe payments."},
        {"category": "Software and Web Development", "text": "Full stack software developer skilled in C# .NET Core Angular and Microsoft SQL Server. Implemented clean architecture, CQRS pattern, and entity framework data layers."},
        {"category": "Software and Web Development", "text": "Software engineer with expertise in Python FastAPI Vue.js and Docker. Developed high throughput microservices, automated API documentation using Swagger, and integrated relational databases."},
        {"category": "Software and Web Development", "text": "Web application developer experienced in PHP Laravel VueJS MySQL and Bootstrap. Built content management systems, multi-tenant SaaS dashboards, and automated scheduled tasks."},
        {"category": "Software and Web Development", "text": "Frontend developer focusing on modern JavaScript ES6+ HTML5 CSS3 responsive grid layouts and animations. Collaborated with UX designers to deliver pixel perfect interfaces."},
        {"category": "Software and Web Development", "text": "Senior application architect with deep knowledge of TypeScript Node.js GraphQL Apollo React and Microfrontend architectures. Improved page load times by 40% through code splitting."},
        {"category": "Software and Web Development", "text": "Software developer proficient in C++ algorithms data structures object-oriented programming OOP and Qt framework. Built desktop utilities with multi-threading and socket programming."},
        {"category": "Software and Web Development", "text": "Full-stack engineer skilled in Go Golang React Docker and PostgreSQL. Engineered gRPC microservices and built modern single-page dashboard with real-time analytics."},
        {"category": "Software and Web Development", "text": "Web developer with experience in Ruby on Rails PostgreSQL JavaScript and Tailwind CSS. Implemented MVC design pattern, background jobs with Sidekiq, and unit tests with RSpec."},
        {"category": "Software and Web Development", "text": "Mobile and web developer skilled in React Native React JavaScript Firebase and Redux. Delivered cross-platform applications for iOS Android and progressive web apps."},
        {"category": "Software and Web Development", "text": "Backend developer with expertise in Flask Python SQLAlchemy REST API design and Redis session management. Created student grading portal with role-based access control."},
        {"category": "Software and Web Development", "text": "Frontend engineer proficient in Angular RxJS TypeScript SCSS and Karma unit testing. Managed complex enterprise state machines and dynamic reactive forms."},
        {"category": "Software and Web Development", "text": "Full stack web developer experienced in Django Python React Bootstrap and SQLite. Developed hospital management system with appointment booking and billing automation."},
        {"category": "Software and Web Development", "text": "Software engineer specializing in API development OAuth2 JWT authentication Node.js Express and MongoDB. Refactored monolithic application into microservices."},
        {"category": "Software and Web Development", "text": "Web developer with solid command over HTML5 semantic tags CSS flexbox grid JavaScript DOM manipulation and webpack bundling."},
        {"category": "Software and Web Development", "text": "Software developer skilled in Java J2EE Spring MVC Maven and Oracle SQL. Implemented enterprise banking transaction system with ACID compliance."},
        {"category": "Software and Web Development", "text": "Full-stack web engineer proficient in Python Flask HTML CSS JavaScript and MySQL. Built real-time collaborative whiteboard using WebSockets."},

        # --- 2. Data Science and Analytics ---
        {"category": "Data Science and Analytics", "text": "Data scientist with expertise in Python Pandas NumPy Matplotlib Seaborn and SQL. Conducted exploratory data analysis EDA, feature engineering, hypothesis testing, and built predictive analytics dashboards."},
        {"category": "Data Science and Analytics", "text": "Data analyst proficient in SQL Power BI Tableau and Excel. Analyzed customer churn datasets, engineered ETL pipelines, and created executive KPI visualization reports for leadership."},
        {"category": "Data Science and Analytics", "text": "Quantitative data analyst with strong background in probability statistics hypothesis testing R programming and time series forecasting using ARIMA and Prophet."},
        {"category": "Data Science and Analytics", "text": "Business intelligence developer experienced in Tableau SQL Server Reporting Services SSRS DAX and data warehousing. Designed star schema data models to support sales reporting."},
        {"category": "Data Science and Analytics", "text": "Data analyst skilled in Python Pandas Seaborn BigQuery and Google Data Studio. Cleaned messy survey datasets, imputed missing values, and calculated cohort retention rates."},
        {"category": "Data Science and Analytics", "text": "Data scientist experienced in statistical modeling A/B testing logistic regression random forest and multivariate statistical analysis. Delivered actionable marketing insights."},
        {"category": "Data Science and Analytics", "text": "Data analytics consultant with knowledge of SQL Snowflake dbt and Power BI. Automated daily reporting workflows and reduced analytical query runtimes by 50%."},
        {"category": "Data Science and Analytics", "text": "Junior data analyst skilled in Excel VLOOKUP pivot tables Python Pandas and data visualization. Analyzed supply chain inventory metrics and supplier performance."},
        {"category": "Data Science and Analytics", "text": "Data scientist proficient in exploratory data analysis statistical inference scikit-learn regression models and financial risk modeling using Monte Carlo simulations."},
        {"category": "Data Science and Analytics", "text": "Business analyst with expertise in SQL queries Tableau dashboards user stories data mapping and stakeholder presentations. Bridged business objectives with technical data pipelines."},
        {"category": "Data Science and Analytics", "text": "Data science graduate with project experience in sentiment analysis customer segmentation using K-Means clustering and interactive visualization using Plotly Dash."},
        {"category": "Data Science and Analytics", "text": "Analytics engineer skilled in SQL Python dbt Apache Airflow and Looker. Built semantic data models and validated data quality metrics across company data marts."},
        {"category": "Data Science and Analytics", "text": "Data analyst proficient in R ggplot2 dplyr tidyverse and statistical hypothesis testing. Performed clinical trial data analysis and generated statistical summary tables."},
        {"category": "Data Science and Analytics", "text": "Quantitative researcher experienced in time series analysis econometric modeling Python Pandas statsmodels and financial portfolio optimization."},
        {"category": "Data Science and Analytics", "text": "Data scientist specializing in marketing attribution models cohort analysis SQL queries and customer lifetime value CLV prediction using survival analysis."},
        {"category": "Data Science and Analytics", "text": "Data analyst with experience in SQL database aggregation data cleaning in Python and executive reporting in Microsoft Power BI. Created automated sales forecast report."},
        {"category": "Data Science and Analytics", "text": "Junior data scientist skilled in Pandas NumPy Scipy Matplotlib and exploratory data analysis on Kaggle datasets. Built house price prediction model."},
        {"category": "Data Science and Analytics", "text": "Data specialist experienced in web scraping with BeautifulSoup data cleaning with Pandas and automated report generation with openpyxl and Tableau."},
        {"category": "Data Science and Analytics", "text": "Statistical analyst skilled in ANOVA regression modeling Chi-square tests Python and SPSS. Delivered demographic research analysis for consumer product goods."},
        {"category": "Data Science and Analytics", "text": "Data analytics engineer with expertise in PostgreSQL window functions Pandas dataframes Seaborn heatmaps and descriptive business reporting."},

        # --- 3. Artificial Intelligence and Machine Learning ---
        {"category": "Artificial Intelligence and Machine Learning", "text": "Machine learning engineer with 3 years experience building and deploying supervised and unsupervised models using scikit-learn PyTorch and TensorFlow. Specialized in deep learning, CNN architectures, and MLflow tracking."},
        {"category": "Artificial Intelligence and Machine Learning", "text": "NLP engineer skilled in Hugging Face Transformers BERT spaCy NLTK and large language models LLMs. Developed text classification, named entity recognition NER, and semantic search pipelines."},
        {"category": "Artificial Intelligence and Machine Learning", "text": "Computer vision engineer experienced in OpenCV PyTorch YOLO object detection image segmentation and ResNet architectures. Deployed automated defect inspection model on edge devices."},
        {"category": "Artificial Intelligence and Machine Learning", "text": "AI researcher specializing in deep reinforcement learning generative adversarial networks GANs and neural architecture search. Published paper on policy gradient optimization."},
        {"category": "Artificial Intelligence and Machine Learning", "text": "Machine learning engineer proficient in feature engineering hyperparameter tuning XGBoost LightGBM scikit-learn and model evaluation with ROC-AUC and precision-recall curves."},
        {"category": "Artificial Intelligence and Machine Learning", "text": "AI engineer experienced in conversational agents LangChain retrieval-augmented generation RAG vector embeddings FAISS and OpenAI API integrations."},
        {"category": "Artificial Intelligence and Machine Learning", "text": "Deep learning practitioner skilled in recurrent neural networks RNN LSTM sequence-to-sequence models and attention mechanisms for speech and audio classification."},
        {"category": "Artificial Intelligence and Machine Learning", "text": "MLOps engineer with expertise in Docker Kubernetes Kubeflow Triton inference server and monitoring model drift in production environments."},
        {"category": "Artificial Intelligence and Machine Learning", "text": "Machine learning developer with project in recommendation systems collaborative filtering matrix factorization and neural collaborative filtering in PyTorch."},
        {"category": "Artificial Intelligence and Machine Learning", "text": "AI specialist skilled in natural language processing text summarization tokenization TF-IDF embeddings and sentiment classification using support vector machines and transformers."},
        {"category": "Artificial Intelligence and Machine Learning", "text": "Junior ML engineer with hands-on experience in scikit-learn Logistic Regression Random Forest gradient boosting and cross-validation for disease prediction."},
        {"category": "Artificial Intelligence and Machine Learning", "text": "Computer vision specialist proficient in OpenCV image preprocessing contour detection optical character recognition OCR using Tesseract and PyTorch."},
        {"category": "Artificial Intelligence and Machine Learning", "text": "AI developer experienced in fine-tuning FLAN-T5 Llama models LoRA quantization and building domain-specific document question-answering systems."},
        {"category": "Artificial Intelligence and Machine Learning", "text": "Machine learning researcher focusing on graph neural networks GNNs anomaly detection in high dimensional feature spaces and unsupervised clustering."},
        {"category": "Artificial Intelligence and Machine Learning", "text": "Deep learning engineer skilled in TensorFlow Keras convolutional networks transfer learning MobileNet and ONNX runtime optimization for mobile deployment."},
        {"category": "Artificial Intelligence and Machine Learning", "text": "ML practitioner with expertise in text vectorization word2vec GloVe embeddings cosine similarity and multi-class classification using scikit-learn."},
        {"category": "Artificial Intelligence and Machine Learning", "text": "AI software engineer experienced in building automated resume parsing pipelines entity recognition with spaCy and skill classification using logistic regression."},
        {"category": "Artificial Intelligence and Machine Learning", "text": "Machine learning engineer skilled in predictive maintenance time series anomaly detection with autoencoders and deploying FastAPI prediction endpoints."},
        {"category": "Artificial Intelligence and Machine Learning", "text": "AI researcher with experience in transformer self-attention mechanisms prompt engineering zero-shot classification and evaluation benchmarks."},
        {"category": "Artificial Intelligence and Machine Learning", "text": "Data and ML engineer skilled in PySpark MLlib scikit-learn ensemble methods and distributed model training on big data clusters."},

        # --- 4. Database Development ---
        {"category": "Database Development", "text": "Oracle Database administrator and PL/SQL developer with 5 years experience in database architecture schema design stored procedures triggers packages and execution plan tuning using EXPLAIN PLAN."},
        {"category": "Database Development", "text": "Senior SQL developer and database developer skilled in Microsoft SQL Server T-SQL stored procedures indexing strategies query optimization and transactional consistency."},
        {"category": "Database Development", "text": "Database engineer proficient in PostgreSQL schema normalization 3NF Boyce-Codd normal form partitioning materialized views and ACID transaction isolation levels."},
        {"category": "Database Development", "text": "NoSQL database developer experienced in MongoDB document data modeling aggregation pipelines sharding replication and Cassandra distributed wide-column stores."},
        {"category": "Database Development", "text": "Database administrator DBA skilled in Oracle 19c 21c XE RAC backup and recovery using RMAN Data Guard replication and database security audits."},
        {"category": "Database Development", "text": "Database architect specializing in data modeling Erwin relational diagrams star schema snowflake schema ETL pipelines and data governance."},
        {"category": "Database Development", "text": "MySQL database developer with expertise in InnoDB storage engine index tuning slow query log analysis and high availability master-slave replication."},
        {"category": "Database Development", "text": "PL/SQL programmer experienced in complex analytical queries window functions cursor management exception handling and automated batch processing in Oracle."},
        {"category": "Database Development", "text": "Database developer skilled in Redis in-memory caching MongoDB caching layers SQL joins subqueries and database migration scripts with Liquibase."},
        {"category": "Database Development", "text": "Junior database developer with strong foundation in relational database management systems RDBMS DDL DML DCL commands foreign key constraints and view creation."},
        {"category": "Database Development", "text": "SQL developer proficient in complex CTEs common table expressions recursive queries analytical functions RANK DENSE_RANK and database performance profiling."},
        {"category": "Database Development", "text": "Database performance tuning specialist experienced in analyzing Oracle AWR reports execution plans B-Tree indexes bitmap indexes and query cost optimization."},
        {"category": "Database Development", "text": "Database developer with experience in PostgreSQL administration vacuuming query planning pg_stat_statements and connection pooling with PgBouncer."},
        {"category": "Database Development", "text": "Relational database designer skilled in normalization up to 3NF denormalization trade-offs entity relationship ER diagrams and integrity constraints."},
        {"category": "Database Development", "text": "Database programmer experienced in writing stored functions packages triggers and audit logging tables in Oracle Database XE and MySQL."},
        {"category": "Database Development", "text": "Database developer focusing on data migration schema versioning Flyway SQL scripts and automated testing of database constraints."},
        {"category": "Database Development", "text": "Data engineer and database specialist skilled in column-oriented databases ClickHouse BigQuery SQL queries indexing and partition pruning."},
        {"category": "Database Development", "text": "Junior SQL developer with solid command of SELECT WHERE GROUP BY HAVING INNER JOIN LEFT JOIN UNION operations and subqueries."},
        {"category": "Database Development", "text": "Database administrator with experience in user privilege management roles grant revoke tablespaces storage allocation and database monitoring."},
        {"category": "Database Development", "text": "Database engineer proficient in graph databases Neo4j Cypher queries relational conversions and hybrid polyglot persistence architectures."},

        # --- 5. Networking and Cybersecurity ---
        {"category": "Networking and Cybersecurity", "text": "Cybersecurity analyst with expertise in network security penetration testing ethical hacking vulnerability assessment using Nessus and Metasploit. Certified CEH with experience in SIEM monitoring."},
        {"category": "Networking and Cybersecurity", "text": "Network engineer skilled in Cisco routing switching OSPF BGP VLANs subnetting TCP/IP protocols and configuring enterprise firewalls and VPN tunnels."},
        {"category": "Networking and Cybersecurity", "text": "Information security specialist experienced in incident response digital forensics threat hunting Wireshark packet capture analysis and malware triage."},
        {"category": "Networking and Cybersecurity", "text": "Security engineer proficient in application security OWASP Top 10 vulnerabilities SAST DAST source code auditing and zero trust architecture."},
        {"category": "Networking and Cybersecurity", "text": "Network administrator with experience in Linux networking DNS DHCP Active Directory LDAP firewall rules and intrusion detection systems Snort."},
        {"category": "Networking and Cybersecurity", "text": "Cryptographic security engineer specializing in Public Key Infrastructure PKI SSL/TLS certificate management AES-256 encryption RSA algorithms and secure hashing."},
        {"category": "Networking and Cybersecurity", "text": "SOC analyst experienced in Splunk QRadar log analysis identifying DDoS attacks phishing email analysis and configuring endpoint detection and response EDR agents."},
        {"category": "Networking and Cybersecurity", "text": "Penetration tester with hands-on experience in Kali Linux Burp Suite Nmap web application security assessments and writing comprehensive remediation reports."},
        {"category": "Networking and Cybersecurity", "text": "Network security engineer skilled in Palo Alto firewalls perimeter defense IPS/IDS configuration NAT policies and network segmentation."},
        {"category": "Networking and Cybersecurity", "text": "Cybersecurity specialist with knowledge of ISO 27001 compliance NIST cybersecurity framework risk management and security awareness program design."},
        {"category": "Networking and Cybersecurity", "text": "Junior network technician with understanding of OSI 7 layer model IP addressing IPv4 IPv6 routing tables Ethernet switching and network troubleshooting."},
        {"category": "Networking and Cybersecurity", "text": "Security researcher experienced in reverse engineering disassembly with Ghidra buffer overflow exploitation and analyzing C/C++ security vulnerabilities."},
        {"category": "Networking and Cybersecurity", "text": "Network engineer proficient in software defined networking SDN Wi-Fi enterprise authentication 802.1X RADIUS servers and network monitoring with Zabbix."},
        {"category": "Networking and Cybersecurity", "text": "Cloud security engineer skilled in AWS IAM policies VPC security groups GuardDuty cloud compliance and infrastructure hardening."},
        {"category": "Networking and Cybersecurity", "text": "Cybersecurity intern with experience in port scanning with Nmap vulnerability scanning with OpenVAS and configuring Linux iptables firewalls."},
        {"category": "Networking and Cybersecurity", "text": "Information assurance analyst specializing in threat modeling secure coding standards authorization controls and multifactor authentication MFA."},
        {"category": "Networking and Cybersecurity", "text": "Network architect experienced in designing fault-tolerant wide area networks WAN SD-WAN MPLS circuits and high availability gateway redundancy protocols HSRP."},
        {"category": "Networking and Cybersecurity", "text": "Cyber defense analyst skilled in MITRE ATT&CK framework mapping intrusion analysis PowerShell security auditing and honeypot deployment."},
        {"category": "Networking and Cybersecurity", "text": "Network security administrator with expertise in proxy servers reverse proxies web application firewalls WAF and SSL inspection."},
        {"category": "Networking and Cybersecurity", "text": "Ethical hacker and security auditor with experience in wireless network security WPA3 auditing password cracking prevention and social engineering defenses."},

        # --- 6. Cloud Computing and DevOps ---
        {"category": "Cloud Computing and DevOps", "text": "DevOps engineer with 4 years experience designing automated CI/CD pipelines using GitHub Actions Jenkins GitLab CI. Skilled in Docker containerization Kubernetes Terraform and AWS."},
        {"category": "Cloud Computing and DevOps", "text": "Cloud architect specializing in Amazon Web Services AWS EC2 S3 Lambda CloudFront IAM Route53 and building serverless microservices architectures."},
        {"category": "Cloud Computing and DevOps", "text": "Site Reliability Engineer SRE proficient in Linux systems engineering Prometheus Grafana monitoring ELK stack logging and implementing 99.99% service level objectives SLOs."},
        {"category": "Cloud Computing and DevOps", "text": "Kubernetes administrator with expertise in Helm charts ingress controllers persistent volumes service mesh Istio and cluster auto-scaling on Google Cloud GKE."},
        {"category": "Cloud Computing and DevOps", "text": "Infrastructure as Code IaC engineer skilled in Terraform Ansible CloudFormation and automating multi-region cloud resource provisioning on Microsoft Azure."},
        {"category": "Cloud Computing and DevOps", "text": "Cloud engineer experienced in Microsoft Azure Azure DevOps Virtual Networks App Services CosmosDB and Azure Active Directory integration."},
        {"category": "Cloud Computing and DevOps", "text": "DevOps specialist proficient in Docker container builds multi-stage Dockerfiles Docker Compose container security scanning and artifact registries."},
        {"category": "Cloud Computing and DevOps", "text": "Cloud systems administrator with strong Linux Bash shell scripting Python automation and AWS cloud cost optimization strategies."},
        {"category": "Cloud Computing and DevOps", "text": "DevSecOps engineer with experience integrating SonarQube dependency scanning secret scanning and container vulnerability scanning into automated Jenkins pipelines."},
        {"category": "Cloud Computing and DevOps", "text": "Cloud native software engineer skilled in serverless computing AWS Lambda API Gateway DynamoDB and event-driven architecture using Apache Kafka."},
        {"category": "Cloud Computing and DevOps", "text": "Junior DevOps engineer with experience setting up automated test runners Dockerizing Python Flask web apps and deploying on AWS EC2 with Nginx."},
        {"category": "Cloud Computing and DevOps", "text": "Site reliability engineer experienced in incident management on-call rotation post-mortems chaos engineering with Chaos Mesh and distributed tracing with Jaeger."},
        {"category": "Cloud Computing and DevOps", "text": "Cloud infrastructure engineer proficient in Google Cloud Platform GCP Compute Engine Cloud Storage BigQuery deployment and Cloud Run microservices."},
        {"category": "Cloud Computing and DevOps", "text": "Automation engineer with expertise in Ansible playbooks configuration management Linux server patching and automated SSH key management."},
        {"category": "Cloud Computing and DevOps", "text": "DevOps practitioner skilled in Git version control branch strategies GitFlow trunk-based development and semantic versioning automation."},
        {"category": "Cloud Computing and DevOps", "text": "Cloud security and DevOps specialist experienced in HashiCorp Vault secrets management TLS certificate automation with Let's Encrypt and IAM least privilege."},
        {"category": "Cloud Computing and DevOps", "text": "Kubernetes engineer experienced in deploying stateful workloads managing ConfigMaps Secrets resource limits and horizontal pod autoscaling HPA."},
        {"category": "Cloud Computing and DevOps", "text": "Cloud migration consultant with experience rehosting virtual machines rearchitecting on-premise applications to AWS and establishing hybrid Direct Connect circuits."},
        {"category": "Cloud Computing and DevOps", "text": "Linux administrator and cloud engineer skilled in RedHat CentOS Ubuntu systemd kernel tuning storage volume management LVM and shell scripting."},
        {"category": "Cloud Computing and DevOps", "text": "DevOps engineer focusing on container registries Harbor Nexus GitHub Packages and automated multi-environment deployment pipelines (Dev, Staging, Prod)."}
    ]

    df = pd.DataFrame(data)
    df.to_csv(DATASET_FILE, index=False)
    print(f"[SUCCESS] Prepared {len(df)} labeled training samples across 6 categories in {DATASET_FILE}")
    print(df["category"].value_counts())
    return df

if __name__ == "__main__":
    generate_dataset()
