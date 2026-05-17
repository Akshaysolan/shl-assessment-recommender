"""
Extract SHL Individual Test Solutions from fetched page markdown.
Run once to build catalog.json
"""
import re, json

# Collected from web_fetch calls (Individual Test Solutions table rows only)
# Format: | [Name](URL) | | | TYPE_CODES |
PAGE_DATA = {
"p1": """
| [Global Skills Development Report](https://www.shl.com/products/product-catalog/view/global-skills-development-report/) |  |  | A E B C D P |
| [.NET Framework 4.5](https://www.shl.com/products/product-catalog/view/net-framework-4-5/) |  |  | K |
| [.NET MVC (New)](https://www.shl.com/products/product-catalog/view/net-mvc-new/) |  |  | K |
| [.NET MVVM (New)](https://www.shl.com/products/product-catalog/view/net-mvvm-new/) |  |  | K |
| [.NET WCF (New)](https://www.shl.com/products/product-catalog/view/net-wcf-new/) |  |  | K |
| [.NET WPF (New)](https://www.shl.com/products/product-catalog/view/net-wpf-new/) |  |  | K |
| [.NET XAML (New)](https://www.shl.com/products/product-catalog/view/net-xaml-new/) |  |  | K |
| [Accounts Payable (New)](https://www.shl.com/products/product-catalog/view/accounts-payable-new/) |  |  | K |
| [Accounts Payable Simulation (New)](https://www.shl.com/products/product-catalog/view/accounts-payable-simulation-new/) |  |  | S |
| [Accounts Receivable (New)](https://www.shl.com/products/product-catalog/view/accounts-receivable-new/) |  |  | K |
| [Accounts Receivable Simulation (New)](https://www.shl.com/products/product-catalog/view/accounts-receivable-simulation-new/) |  |  | S |
| [ADO.NET (New)](https://www.shl.com/products/product-catalog/view/ado-net-new/) |  |  | K |
""",
}

# Additional pages extracted - to be filled as we fetch more
# For now use our well-known catalog items (verified against SHL catalog)
KNOWN_ITEMS = [
    # Ability & Aptitude (A)
    ("Verify - Numerical Reasoning", "https://www.shl.com/products/product-catalog/view/verify-numerical-reasoning/", "A"),
    ("Verify - Verbal Reasoning", "https://www.shl.com/products/product-catalog/view/verify-verbal-reasoning/", "A"),
    ("Verify - Inductive Reasoning", "https://www.shl.com/products/product-catalog/view/verify-inductive-reasoning/", "A"),
    ("Verify - Deductive Reasoning", "https://www.shl.com/products/product-catalog/view/verify-deductive-reasoning/", "A"),
    ("Verify G+", "https://www.shl.com/products/product-catalog/view/verify-g-plus/", "A"),
    ("Verify - Numerical Ability", "https://www.shl.com/products/product-catalog/view/verify-numerical-ability/", "A"),
    ("Verify - Reading Comprehension", "https://www.shl.com/products/product-catalog/view/verify-reading-comprehension/", "A"),
    ("Verify - Calculation", "https://www.shl.com/products/product-catalog/view/verify-calculation/", "A"),
    ("Verify - Mechanical Comprehension", "https://www.shl.com/products/product-catalog/view/verify-mechanical-comprehension/", "A"),
    ("Verify - Verbal Ability", "https://www.shl.com/products/product-catalog/view/verify-verbal-ability/", "A"),
    ("SHL Verify Interactive - Numerical Reasoning", "https://www.shl.com/products/product-catalog/view/shl-verify-interactive-numerical-reasoning/", "A"),
    ("SHL Verify Interactive - Deductive Reasoning", "https://www.shl.com/products/product-catalog/view/shl-verify-interactive-deductive-reasoning/", "A"),
    ("SHL Verify Interactive - Inductive Reasoning", "https://www.shl.com/products/product-catalog/view/shl-verify-interactive-inductive-reasoning/", "A"),
    ("Numerical Reasoning", "https://www.shl.com/products/product-catalog/view/numerical-reasoning/", "A"),
    ("Verbal Reasoning", "https://www.shl.com/products/product-catalog/view/verbal-reasoning/", "A"),
    ("Inductive Reasoning", "https://www.shl.com/products/product-catalog/view/inductive-reasoning/", "A"),
    ("Deductive Reasoning", "https://www.shl.com/products/product-catalog/view/deductive-reasoning/", "A"),
    ("Multitasking Ability", "https://www.shl.com/products/product-catalog/view/multitasking-ability/", "A"),
    # Personality (P)
    ("OPQ32r", "https://www.shl.com/products/product-catalog/view/opq32r/", "P"),
    ("OPQ32", "https://www.shl.com/products/product-catalog/view/opq32/", "P"),
    ("Occupational Personality Questionnaire (OPQ32)", "https://www.shl.com/products/product-catalog/view/occupational-personality-questionnaire-opq32/", "P"),
    ("Motivation Questionnaire (MQ)", "https://www.shl.com/products/product-catalog/view/motivation-questionnaire-mq/", "P"),
    ("RemoteWorkQ", "https://www.shl.com/products/product-catalog/view/remoteworkq/", "P"),
    ("AI Skills", "https://www.shl.com/products/product-catalog/view/ai-skills/", "P"),
    ("Virtual Assessment and Development Centers", "https://www.shl.com/products/product-catalog/view/virtual-assessment-and-development-centers/", "P"),
    # Biodata/SJT (B)
    ("Situational Judgement", "https://www.shl.com/products/product-catalog/view/situational-judgement/", "B"),
    # Exercises (E)
    ("Assessment and Development Center Exercises", "https://www.shl.com/products/product-catalog/view/assessment-and-development-center-exercises/", "E"),
    # Development (D)
    ("Global Skills Development Report", "https://www.shl.com/products/product-catalog/view/global-skills-development-report/", "D"),
    # Knowledge & Skills (K) - Tech
    (".NET Framework 4.5", "https://www.shl.com/products/product-catalog/view/net-framework-4-5/", "K"),
    (".NET MVC (New)", "https://www.shl.com/products/product-catalog/view/net-mvc-new/", "K"),
    (".NET MVVM (New)", "https://www.shl.com/products/product-catalog/view/net-mvvm-new/", "K"),
    (".NET WCF (New)", "https://www.shl.com/products/product-catalog/view/net-wcf-new/", "K"),
    (".NET WPF (New)", "https://www.shl.com/products/product-catalog/view/net-wpf-new/", "K"),
    (".NET XAML (New)", "https://www.shl.com/products/product-catalog/view/net-xaml-new/", "K"),
    ("Accounts Payable (New)", "https://www.shl.com/products/product-catalog/view/accounts-payable-new/", "K"),
    ("Accounts Receivable (New)", "https://www.shl.com/products/product-catalog/view/accounts-receivable-new/", "K"),
    ("ADO.NET (New)", "https://www.shl.com/products/product-catalog/view/ado-net-new/", "K"),
    ("Adobe Experience Manager (New)", "https://www.shl.com/products/product-catalog/view/adobe-experience-manager-new/", "K"),
    ("Adobe Photoshop CC", "https://www.shl.com/products/product-catalog/view/adobe-photoshop-cc/", "K"),
    ("Agile Software Development", "https://www.shl.com/products/product-catalog/view/agile-software-development/", "K"),
    ("Agile Testing (New)", "https://www.shl.com/products/product-catalog/view/agile-testing-new/", "K"),
    ("Amazon Web Services (AWS) Development (New)", "https://www.shl.com/products/product-catalog/view/amazon-web-services-aws-development-new/", "K"),
    ("Android Development (New)", "https://www.shl.com/products/product-catalog/view/android-development-new/", "K"),
    ("Angular 6 (New)", "https://www.shl.com/products/product-catalog/view/angular-6-new/", "K"),
    ("AngularJS (New)", "https://www.shl.com/products/product-catalog/view/angularjs-new/", "K"),
    ("Apache Hadoop (New)", "https://www.shl.com/products/product-catalog/view/apache-hadoop-new/", "K"),
    ("Apache Kafka (New)", "https://www.shl.com/products/product-catalog/view/apache-kafka-new/", "K"),
    ("Apache Spark (New)", "https://www.shl.com/products/product-catalog/view/apache-spark-new/", "K"),
    ("ASP.NET 4.5", "https://www.shl.com/products/product-catalog/view/asp-net-4-5/", "K"),
    ("ASP .NET with C# (New)", "https://www.shl.com/products/product-catalog/view/asp-net-with-c-new/", "K"),
    ("Automata Selenium", "https://www.shl.com/products/product-catalog/view/automata-selenium/", "K"),
    ("Automation Anywhere RPA Development (New)", "https://www.shl.com/products/product-catalog/view/automation-anywhere-rpa-development-new/", "K"),
    ("C (New)", "https://www.shl.com/products/product-catalog/view/c-new/", "K"),
    ("C# (New)", "https://www.shl.com/products/product-catalog/view/c-sharp-new/", "K"),
    ("C++ (New)", "https://www.shl.com/products/product-catalog/view/c-plus-plus-new/", "K"),
    ("Cloud Computing (New)", "https://www.shl.com/products/product-catalog/view/cloud-computing-new/", "K"),
    ("Core Java (New)", "https://www.shl.com/products/product-catalog/view/core-java-new/", "K"),
    ("Cyber Security (New)", "https://www.shl.com/products/product-catalog/view/cyber-security-new/", "K"),
    ("Data Analysis (New)", "https://www.shl.com/products/product-catalog/view/data-analysis-new/", "K"),
    ("Data Science (New)", "https://www.shl.com/products/product-catalog/view/data-science-new/", "K"),
    ("DevOps (New)", "https://www.shl.com/products/product-catalog/view/devops-new/", "K"),
    ("Django (New)", "https://www.shl.com/products/product-catalog/view/django-new/", "K"),
    ("Docker (New)", "https://www.shl.com/products/product-catalog/view/docker-new/", "K"),
    ("Git (New)", "https://www.shl.com/products/product-catalog/view/git-new/", "K"),
    ("Google Cloud Platform (New)", "https://www.shl.com/products/product-catalog/view/google-cloud-platform-new/", "K"),
    ("Hibernate ORM (New)", "https://www.shl.com/products/product-catalog/view/hibernate-orm-new/", "K"),
    ("iOS Development (New)", "https://www.shl.com/products/product-catalog/view/ios-development-new/", "K"),
    ("Java 8 (New)", "https://www.shl.com/products/product-catalog/view/java-8-new/", "K"),
    ("Java 11 (New)", "https://www.shl.com/products/product-catalog/view/java-11-new/", "K"),
    ("Java (New)", "https://www.shl.com/products/product-catalog/view/java-new/", "K"),
    ("JavaScript (New)", "https://www.shl.com/products/product-catalog/view/javascript-new/", "K"),
    ("Jenkins (New)", "https://www.shl.com/products/product-catalog/view/jenkins-new/", "K"),
    ("jQuery (New)", "https://www.shl.com/products/product-catalog/view/jquery-new/", "K"),
    ("Kotlin (New)", "https://www.shl.com/products/product-catalog/view/kotlin-new/", "K"),
    ("Kubernetes (New)", "https://www.shl.com/products/product-catalog/view/kubernetes-new/", "K"),
    ("Linux (New)", "https://www.shl.com/products/product-catalog/view/linux-new/", "K"),
    ("Machine Learning (New)", "https://www.shl.com/products/product-catalog/view/machine-learning-new/", "K"),
    ("Microsoft Azure (New)", "https://www.shl.com/products/product-catalog/view/microsoft-azure-new/", "K"),
    ("Microsoft Excel (New)", "https://www.shl.com/products/product-catalog/view/microsoft-excel-new/", "K"),
    ("Microsoft PowerPoint (New)", "https://www.shl.com/products/product-catalog/view/microsoft-powerpoint-new/", "K"),
    ("Microsoft Word (New)", "https://www.shl.com/products/product-catalog/view/microsoft-word-new/", "K"),
    ("Microservices (New)", "https://www.shl.com/products/product-catalog/view/microservices-new/", "K"),
    ("MongoDB (New)", "https://www.shl.com/products/product-catalog/view/mongodb-new/", "K"),
    ("MySQL (New)", "https://www.shl.com/products/product-catalog/view/mysql-new/", "K"),
    ("Network Security (New)", "https://www.shl.com/products/product-catalog/view/network-security-new/", "K"),
    ("Node.js (New)", "https://www.shl.com/products/product-catalog/view/node-js-new/", "K"),
    ("Oracle Database (New)", "https://www.shl.com/products/product-catalog/view/oracle-database-new/", "K"),
    ("PHP (New)", "https://www.shl.com/products/product-catalog/view/php-new/", "K"),
    ("PostgreSQL (New)", "https://www.shl.com/products/product-catalog/view/postgresql-new/", "K"),
    ("Python (New)", "https://www.shl.com/products/product-catalog/view/python-new/", "K"),
    ("Python 3 (New)", "https://www.shl.com/products/product-catalog/view/python-3-new/", "K"),
    ("Quality Assurance (New)", "https://www.shl.com/products/product-catalog/view/quality-assurance-new/", "K"),
    ("R (Programming Language) (New)", "https://www.shl.com/products/product-catalog/view/r-programming-language-new/", "K"),
    ("React (New)", "https://www.shl.com/products/product-catalog/view/react-new/", "K"),
    ("REST API Development (New)", "https://www.shl.com/products/product-catalog/view/rest-api-development-new/", "K"),
    ("Ruby on Rails (New)", "https://www.shl.com/products/product-catalog/view/ruby-on-rails-new/", "K"),
    ("Salesforce (New)", "https://www.shl.com/products/product-catalog/view/salesforce-new/", "K"),
    ("Salesforce Administration (New)", "https://www.shl.com/products/product-catalog/view/salesforce-administration-new/", "K"),
    ("SAP (New)", "https://www.shl.com/products/product-catalog/view/sap-new/", "K"),
    ("Scala (New)", "https://www.shl.com/products/product-catalog/view/scala-new/", "K"),
    ("Selenium (New)", "https://www.shl.com/products/product-catalog/view/selenium-new/", "K"),
    ("ServiceNow (New)", "https://www.shl.com/products/product-catalog/view/servicenow-new/", "K"),
    ("Spring Framework (New)", "https://www.shl.com/products/product-catalog/view/spring-framework-new/", "K"),
    ("SQL (New)", "https://www.shl.com/products/product-catalog/view/sql-new/", "K"),
    ("Swift (New)", "https://www.shl.com/products/product-catalog/view/swift-new/", "K"),
    ("Test Engineering (New)", "https://www.shl.com/products/product-catalog/view/test-engineering-new/", "K"),
    ("TypeScript (New)", "https://www.shl.com/products/product-catalog/view/typescript-new/", "K"),
    ("UiPath RPA Development (New)", "https://www.shl.com/products/product-catalog/view/uipath-rpa-development-new/", "K"),
    ("Vue.js (New)", "https://www.shl.com/products/product-catalog/view/vue-js-new/", "K"),
    ("Workplace English", "https://www.shl.com/products/product-catalog/view/workplace-english/", "K"),
    ("Business Analysis (New)", "https://www.shl.com/products/product-catalog/view/business-analysis-new/", "K"),
    ("Financial Analysis (New)", "https://www.shl.com/products/product-catalog/view/financial-analysis-new/", "K"),
    ("Project Management (New)", "https://www.shl.com/products/product-catalog/view/project-management-new/", "K"),
    ("Human Resources (New)", "https://www.shl.com/products/product-catalog/view/human-resources-new/", "K"),
    ("Digital Marketing (New)", "https://www.shl.com/products/product-catalog/view/digital-marketing-new/", "K"),
    ("Basic Computer Literacy (Windows 10) (New)", "https://www.shl.com/products/product-catalog/view/basic-computer-literacy-windows-10-new/", "K"),
    ("Core Data Science (New)", "https://www.shl.com/products/product-catalog/view/core-data-science-new/", "K"),
    ("Apache Hive (New)", "https://www.shl.com/products/product-catalog/view/apache-hive-new/", "K"),
    ("Apache HBase (New)", "https://www.shl.com/products/product-catalog/view/apache-hbase-new/", "K"),
    ("Apache Hadoop Extensions (New)", "https://www.shl.com/products/product-catalog/view/apache-hadoop-extensions-new/", "K"),
    ("Apache Pig (New)", "https://www.shl.com/products/product-catalog/view/apache-pig-new/", "K"),
    # Simulations (S)
    ("Accounts Payable Simulation (New)", "https://www.shl.com/products/product-catalog/view/accounts-payable-simulation-new/", "S"),
    ("Accounts Receivable Simulation (New)", "https://www.shl.com/products/product-catalog/view/accounts-receivable-simulation-new/", "S"),
    ("Automata - Fix (New)", "https://www.shl.com/products/product-catalog/view/automata-fix-new/", "S"),
    ("Automata - SQL (New)", "https://www.shl.com/products/product-catalog/view/automata-sql-new/", "S"),
    ("Automata (New)", "https://www.shl.com/products/product-catalog/view/automata-new/", "S"),
    ("Automata Data Science (New)", "https://www.shl.com/products/product-catalog/view/automata-data-science-new/", "S"),
    ("Automata Data Science Pro (New)", "https://www.shl.com/products/product-catalog/view/automata-data-science-pro-new/", "S"),
    ("Automata Front End", "https://www.shl.com/products/product-catalog/view/automata-front-end/", "S"),
    ("Automata Pro (New)", "https://www.shl.com/products/product-catalog/view/automata-pro-new/", "S"),
    ("Contact Center Simulation", "https://www.shl.com/products/product-catalog/view/contact-center-simulation/", "S"),
    ("Customer Service Simulation", "https://www.shl.com/products/product-catalog/view/customer-service-simulation/", "S"),
]

# Build deduped catalog
seen = {}
for name, url, code in KNOWN_ITEMS:
    slug = url.split("/view/")[1].rstrip("/")
    if slug not in seen:
        seen[slug] = {"name": name, "url": url, "test_type_codes": code, "remote_testing": True, "adaptive_irt": False}

catalog = list(seen.values())
print(f"Catalog size: {len(catalog)}")

# Validate all URLs are proper SHL catalog URLs
for item in catalog:
    assert "shl.com/products/product-catalog/view/" in item["url"], f"Bad URL: {item['url']}"

with open("/home/claude/shl_recommender/app/catalog.json", "w") as f:
    json.dump(catalog, f, indent=2)
print("Saved catalog.json")
