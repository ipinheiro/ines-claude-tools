---
allowed-tools:
  # Core Python tooling
  - Bash(uv:*)
  - Bash(uv run:*)
  # Code quality and linting
  - Bash(uv run --with ruff ruff:*)
  - Bash(uv run --with 'pyright[nodejs]' pyright:*)
  # Security analysis
  - Bash(uv run --with bandit bandit:*)
  - Bash(uv run --with safety safety:*)
  - Bash(uv run --with semgrep semgrep:*)
  - Bash(docker run --rm -v /tmp/trivy:/tmp/trivy -v "$(pwd):/src" aquasec/trivy repository . --skip-dirs .venv --cache-dir /tmp/trivy)
  # Performance profiling
  - Bash(uv run --with scalene scalene:*)
  - Bash(uv run --with memray memray:*)
  - Bash(uv run --with py-spy py-spy:*)
  - Bash(uv run --with line_profiler kernprof:*)
  - Bash(uv run --with memory_profiler mprof:*)
  # Databricks tooling
  - Bash(uv run --with databricks-cli databricks:*)
  - Bash(uv run --with dbx dbx:*)
  # Container security
  - Bash(docker run --rm -v /tmp/trivy:/tmp/trivy -v $(pwd):/src aquasec/trivy:*)
  # File operations for report generation
  - Write
  - Read
  - Edit
  - MultiEdit
description: Comprehensive multi-dimensional analysis for data science codebases including code quality, architecture, security, performance, data quality, ML models, and Databricks environments
---

# Data Science Codebase Analysis

Comprehensive multi-dimensional analysis tool specifically designed for data science teams working with Python, machine learning pipelines, and Databricks environments.

**Usage**: `/analyse [mode] [--plan] [--think|--think-hard|--ultrathink] [--output=path] [--parallel]`

**Arguments**:
- `mode`: Analysis mode (see Available Modes below)
- `--plan`: Begin by drawing up a detailed execution plan for user approval
- `--think|--think-hard|--ultrathink`: Set thinking token budget for complex analysis
- `--output=path`: Specify custom output directory (default: `./analysis-report-YYYY-MM-DD`)
- `--parallel`: Enable parallel analysis using sub-agents for faster execution

## Analysis Modes

### Core Analysis Modes

#### **code** - Code Quality & Best Practices
**Focus**: Python code quality, data science coding patterns, library usage optimization

**Specific Evaluation Criteria**:
- **Naming & Structure**: PEP 8 compliance, meaningful variable names, function organization
- **DRY Principles**: Code duplication detection, reusable component identification
- **Complexity Analysis**: Cyclomatic complexity, nested loop detection, function length
- **Type Safety**: Type hints coverage, pyright compatibility, pandas type consistency
- **Error Handling**: Exception management, data validation patterns
- **DS Library Optimization**: Pandas vectorization, NumPy efficiency, memory usage patterns
- **Jupyter Notebook Quality**: Cell organization, markdown documentation, output management
- **Package Management**: requirements.txt is deprecated, and users should be migrating to `pyproject.toml` with `uv` as their package manager

**Deliverables**: 
- Code quality score (0-100)
- Specific refactoring recommendations
- Library usage optimization suggestions
- Compliance checklist with actionable items

#### **arch** - Architecture & Design Patterns
**Focus**: System design, data pipeline architecture, ML system patterns

**Specific Evaluation Criteria**:
- **Design Patterns**: Factory, Strategy, Observer patterns in ML contexts
- **Layer Separation**: Data layer, business logic, presentation separation
- **API Design**: REST/GraphQL interface consistency, versioning strategy
- **Data Flow Architecture**: ETL/ELT patterns, stream processing design
- **ML Pipeline Structure**: Training/inference separation, model versioning
- **Microservices Design**: Service boundaries, inter-service communication
- **Configuration Management**: Environment-specific configs, feature flags

**Deliverables**:
- Architecture diagram recommendations
- Design pattern implementation suggestions
- Scalability improvement roadmap
- Integration points analysis

#### **security** - Security & Compliance
**Focus**: Data security, ML model security, compliance requirements

**Specific Evaluation Criteria**:
- **OWASP Top 10**: Web application security vulnerabilities
- **Data Security**: PII handling, encryption at rest/transit, data anonymization
- **Authentication & Authorization**: OAuth implementation, RBAC patterns
- **ML Security**: Model poisoning prevention, adversarial attack mitigation
- **Dependency Security**: Known vulnerabilities in packages, supply chain security
- **Secrets Management**: API key handling, credential rotation
- **Compliance**: GDPR, HIPAA, SOX requirements where applicable

**Deliverables**:
- Security risk assessment (High/Medium/Low)
- Vulnerability remediation plan
- Compliance gap analysis
- Security best practices checklist

#### **perf** - Performance & Optimization
**Focus**: Computational efficiency, memory optimization, scalability

**Specific Evaluation Criteria**:
- **CPU Optimization**: Algorithm complexity, vectorization opportunities
- **Memory Management**: Memory leaks, large object optimization, garbage collection
- **I/O Efficiency**: Database query optimization, file I/O patterns
- **Pandas Performance**: DataFrame operations, memory usage, chunking strategies
- **ML Model Performance**: Training time, inference latency, model size
- **Parallel Processing**: Multi-threading, multiprocessing, async patterns
- **Caching Strategies**: Result caching, memoization, distributed caching

**Deliverables**:
- Performance benchmark report
- Bottleneck identification and solutions
- Memory optimization recommendations
- Scalability improvement plan

### Data Science Specific Modes

#### **data-quality** - Data Quality & Validation
**Focus**: Data pipeline reliability, validation frameworks, data drift detection

**Specific Evaluation Criteria**:
- **Data Validation**: Schema validation, constraint checking, outlier detection
- **Data Drift**: Statistical drift detection, feature distribution changes
- **Data Lineage**: End-to-end data tracking, transformation documentation
- **Quality Metrics**: Completeness, accuracy, consistency, timeliness
- **Monitoring & Alerting**: Data quality dashboards, automated alerts

**Deliverables**:
- Data quality score and metrics
- Validation framework recommendations
- Data drift monitoring setup
- Quality assurance pipeline design

#### **pipeline** - Data Pipeline & ETL Analysis
**Focus**: Data engineering practices, pipeline reliability, orchestration

**Specific Evaluation Criteria**:
- **Pipeline Architecture**: DAG design, task dependencies, error handling
- **Data Processing**: Batch vs streaming, partitioning strategies, data formats
- **Orchestration**: Airflow, Prefect, or other workflow management
- **Error Handling**: Retry logic, dead letter queues, failure notifications
- **Resource Management**: Compute optimization, auto-scaling, cost efficiency
- **Testing**: Unit tests for transformations, integration tests, data validation
- **Monitoring**: Pipeline observability, execution metrics, SLA tracking

**Deliverables**:
- Pipeline reliability assessment
- Optimization recommendations
- Testing strategy improvements
- Monitoring and alerting setup

#### **databricks** - Databricks Environment Analysis
**Focus**: Databricks-specific optimizations, cluster management, notebook best practices

**Specific Evaluation Criteria**:
- **Cluster Configuration**: Instance types, auto-scaling, cost optimization
- **Notebook Organization**: Code structure, markdown documentation, magic commands
- **Delta Lake Usage**: Table optimization, time travel, data versioning
- **Spark Optimization**: Partitioning, caching, broadcast joins
- **MLflow Integration**: Experiment tracking, model registry, deployment
- **Security**: Access controls, credential management, network security
- **Cost Management**: Resource utilization, idle cluster detection, optimization

**Deliverables**:
- Databricks optimization recommendations
- Cost reduction strategies
- Security compliance assessment
- Performance tuning guide

## Structured Analysis Workflow

The analysis follows a systematic 3-phase approach designed for thorough evaluation:

### Phase 1: Discovery & Mapping (15-25% of time)
**Objective**: Understand codebase structure and identify analysis targets

**Tasks**:
1. **Codebase Structure Mapping**
   ```bash
   fd -e py | head -20
   fd -e ipynb | wc -l
   fd -g 'requirements*.txt' -g 'pyproject.toml'
   ```
   For a repo large enough that this floods context, dispatch an `Explore` agent instead and keep only its summary.

2. **Dependency Analysis**
   - Identify key libraries (pandas, sklearn, tensorflow, etc.)
   - Map data science stack components
   - Detect Databricks-specific imports

3. **Component Identification**
   - Data ingestion modules
   - ML training/inference code
   - API endpoints and services
   - Notebook collections
   - Configuration files

4. **Scope Definition**
   - Prioritize critical components
   - Identify analysis-mode-specific targets
   - Plan parallel execution strategy

### Phase 2: Analysis Execution (60-70% of time)
**Objective**: Execute comprehensive analysis using appropriate tools

**Parallel Execution Strategy**:
- Spawn analysis agents with the `Agent` tool, all in one message so they run concurrently
- Run complementary tools simultaneously
- Execute mode-specific evaluations

**Tool Execution Examples**:
```bash
# Code quality analysis
uv run --with ruff ruff check . --output-format=json
uv run --with 'pyright[nodejs]' pyright file1.py file2.py package/

# Security analysis
uv run --with bandit bandit -r . -f json -o bandit-report.json
uv run --with safety safety check --json
# trivy, has to be run through docker
docker run --rm -v /tmp/trivy:/tmp/trivy -v "$(pwd):/src" aquasec/trivy repository . --skip-dirs .venv --cache-dir /tmp/trivy

# Performance profiling (on sample files)
uv run --with scalene scalene --cpu --memory --json your_script.py

# Data quality analysis
uv run --with great-expectations great_expectations init
uv run --with pandas-profiling pandas_profiling.ProfileReport
```

### Phase 3: Compilation & Reporting (15-25% of time)
**Objective**: Synthesize findings into actionable insights

**Report Generation Process**:
1. **Results Aggregation**
   - Collect all tool outputs
   - Normalize findings across tools
   - Calculate composite scores

2. **Analysis Synthesis**
   - Identify cross-cutting issues
   - Prioritize recommendations
   - Create improvement roadmap

3. **Report Writing**
   - Generate structured markdown report
   - Include executive summary
   - Provide actionable next steps

## Enhanced Tool Arsenal

### Code Quality & Linting Tools

#### **ruff** - Fast Python Linter
```bash
# Basic analysis
uv run --with ruff ruff check . --output-format=json

# With fix suggestions
uv run --with ruff ruff check . --fix --show-fixes
```
**Use for**: PEP 8 compliance, import organization, code style consistency

#### **mypy** - Static Type Checker
```bash
# Type checking with detailed output
uv run --with mypy mypy . --show-error-codes --show-error-context
```
**Use for**: Type safety analysis, pandas type compatibility

#### **pylint** - Comprehensive Code Analysis
```bash
# Detailed code quality report
uv run --with pylint pylint your_package --output-format=json
```
**Use for**: Code quality scoring, complexity analysis, best practices

### Security Analysis Tools

#### **bandit** - Python Security Linter
```bash
# Security vulnerability scanning
uv run --with bandit bandit -r . -f json -o security-report.json
```
**Use for**: Python-specific security vulnerabilities, hardcoded secrets

#### **safety** - Dependency Vulnerability Scanner
```bash
# Check for known vulnerabilities in dependencies
uv run --with safety safety check --json --output safety-report.json
```
**Use for**: Package vulnerability detection, dependency security

#### **semgrep** - Static Analysis Tool
```bash
# Advanced security and bug detection
uv run --with semgrep semgrep --config=auto . --json
```
**Use for**: Advanced security patterns, custom rule enforcement

### Performance Analysis Tools

#### **scalene** - CPU/Memory Profiler
```bash
# Comprehensive profiling
uv run --with scalene scalene --cpu --memory --json your_script.py
```
**Use for**: Line-by-line performance analysis, memory usage tracking

#### **memray** - Memory Profiler
```bash
# Memory usage analysis
uv run --with memray memray run --output memray-report.bin your_script.py
uv run --with memray memray flamegraph memray-report.bin
```
**Use for**: Memory leak detection, allocation patterns

#### **py-spy** - Sampling Profiler
```bash
# Live process profiling
uv run --with py-spy py-spy record -o profile.svg -- python your_script.py
```
**Use for**: Production performance monitoring, CPU profiling

### Databricks Specific Tools

#### **databricks-cli** - Databricks Management
```bash
# Workspace analysis
uv run --with databricks-cli databricks workspace ls /
uv run --with databricks-cli databricks clusters list
```
**Use for**: Workspace management, cluster optimization

#### **dbx** - Databricks Developer Tools
```bash
# Project analysis and deployment
uv run --with dbx dbx configure
uv run --with dbx dbx deploy --dry-run
```
**Use for**: Databricks project optimization, deployment analysis

## Sub-Agent Strategy & Parallel Execution

### When to Use Sub-Agents

**Complex Multi-Component Analysis**:
- Large codebases (>100 files)
- Multi-mode analysis (e.g., code + security + performance)
- Databricks environments with multiple notebooks/clusters
- ML pipelines with multiple models

### Sub-Agent Task Examples

Dispatch these with the `Agent` tool. Put every call in a **single message** so they run concurrently rather than in sequence.

```
Agent(subagent_type="general-purpose", description="Security analysis", prompt="""
Perform a security analysis of the codebase:
1. Run bandit across all Python files
2. Check dependencies with safety
3. Analyse authentication patterns
Return findings with severity levels and file:line references.
""")

Agent(subagent_type="general-purpose", description="Performance analysis", prompt="""
Profile performance across key modules:
1. Run scalene on the main processing scripts
2. Analyse pandas operations for optimisation
3. Check for memory growth with memray
Return a report with specific improvements and measured numbers.
""")

Agent(subagent_type="general-purpose", description="Data quality assessment", prompt="""
Evaluate data quality and validation:
1. Analyse data schemas and validation patterns
2. Run great-expectations if configured
3. Check for drift detection
Return a scorecard and improvement plan.
""")
```

Each agent returns only its final report, so the tool output never lands in this context. Read the returns, then write the consolidated report yourself.

### Parallel Execution Benefits
- **Speed**: Reduce analysis time by 60-80%
- **Thoroughness**: Enable comprehensive multi-angle analysis
- **Specialization**: Allow focused expertise per analysis domain
- **Scalability**: Handle large, complex codebases efficiently

## Report Generation & Organization

### Output Structure

**Default Output Directory**: `./analysis-report-YYYY-MM-DD/`

```
analysis-report-2024-01-15/
├── executive-summary.md          # High-level findings and recommendations
├── detailed-analysis/
│   ├── code-quality-report.md
│   ├── security-assessment.md
│   ├── performance-analysis.md
│   ├── data-quality-report.md
│   ├── ml-model-evaluation.md
│   └── databricks-optimization.md
├── tool-outputs/
│   ├── ruff-results.json
│   ├── bandit-security.json
│   ├── scalene-profile.json
│   └── great-expectations-results.html
├── recommendations/
│   ├── immediate-actions.md      # Critical issues requiring immediate attention
│   ├── improvement-roadmap.md    # 30/60/90 day improvement plan
│   └── technical-debt.md         # Long-term architectural improvements
└── appendices/
    ├── tool-configurations.md    # Recommended tool configs for ongoing use
    ├── metrics-baseline.md       # Baseline metrics for future comparison
    └── compliance-checklist.md   # Regulatory/standards compliance status
```

### Report Requirements

**Executive Summary Must Include**:
- Overall codebase health score (0-100)
- Top 5 critical findings requiring immediate attention
- Investment priorities (security, performance, maintainability)
- Timeline for key improvements

**Detailed Reports Must Include**:
- Specific metrics and scores
- Before/after code examples
- Step-by-step implementation guidance
- Cost/benefit analysis for recommendations

**All Reports Must**:
- Be written to disk as markdown files
- Include actionable next steps
- Provide specific code examples
- Reference line numbers and file paths
- Include timeline estimates for improvements

## Usage Examples

### Basic Code Quality Analysis
```bash
/analyse code --output=./quality-review
```

### Comprehensive Data Science Analysis
```bash
/analyse ml-model --parallel --think-hard --output=./ml-assessment
```

### Databricks Environment Optimization
```bash
/analyse databricks --plan --output=./databricks-optimization
```

### Multi-Mode Analysis with Planning
```bash
/analyse security --plan --parallel --output=./security-audit
```

## Success Metrics

Each analysis mode provides quantitative success metrics:

- **Code Quality**: Maintainability Index, Technical Debt Ratio, Test Coverage
- **Security**: Vulnerability Count, Risk Score, Compliance Percentage
- **Performance**: Execution Time Improvement %, Memory Usage Reduction %
- **Data Quality**: Data Quality Score, Validation Coverage, Drift Detection Rate
- **ML Models**: Model Performance Metrics, MLOps Maturity Score
- **Architecture**: Coupling Metrics, Modularity Score, API Consistency Index

These metrics enable progress tracking and ROI measurement for improvement initiatives.
