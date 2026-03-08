"""
expand_skills_comprehensive.py
==============================
Expands the career-ml skills dataset from ~300 to 1,200+ skills.

* Reads  : data/processed/skills.csv  (SK001–SK300)
* Writes : data/expanded/skills_v2.csv (SK001–SK1200+)

Every existing skill is preserved untouched.
New skills start from SK301 and cover:
  A. Technical Skills   (~600)
  B. Soft Skills         (~150)
  C. Certifications      (~150)

Run:
    cd career-ml
    python scripts/expand_skills_comprehensive.py
"""

from pathlib import Path
import pandas as pd
import sys
import textwrap

# ── paths ────────────────────────────────────────────────────────────────
BASE_DIR   = Path(__file__).resolve().parent.parent          # career-ml/
INPUT_CSV  = BASE_DIR / "data" / "processed" / "skills.csv"
OUTPUT_DIR = BASE_DIR / "data" / "expanded"
OUTPUT_CSV = OUTPUT_DIR / "skills_v2.csv"

# ── helper ───────────────────────────────────────────────────────────────
def _id(n: int) -> str:
    """SK001, SK012, SK0301 … – always at least 3 digits."""
    return f"SK{n:04d}" if n >= 1000 else f"SK{n:03d}"


# ======================================================================
#   NEW SKILLS DEFINITIONS
# ======================================================================
# Each entry: (name, aliases, category, type)
# Categories: frontend, backend, fullstack, data, ai_ml, devops, cloud,
#             security, mobile, blockchain, game_dev, embedded,
#             communication, leadership, project_mgmt, business,
#             certification, database, analytics
# Types: technical, soft, credential

NEW_SKILLS: list[tuple[str, str, str, str]] = []

# ──────────────────────────────────────────────────────────────────────
# A. TECHNICAL SKILLS  (~600)
# ──────────────────────────────────────────────────────────────────────

# --- A1. Programming Languages (50) ---
_programming_languages = [
    ("rust", "rust,rust-lang,rustlang", "backend", "technical"),
    ("go", "go,golang,go-lang", "backend", "technical"),
    ("kotlin", "kotlin,kt", "backend", "technical"),
    ("dart", "dart,dartlang", "frontend", "technical"),
    ("julia", "julia,julialang", "data", "technical"),
    ("elixir", "elixir,ex", "backend", "technical"),
    ("haskell", "haskell,hs", "backend", "technical"),
    ("clojure", "clojure,clj", "backend", "technical"),
    ("erlang", "erlang,erl", "backend", "technical"),
    ("f#", "fsharp,f#,f-sharp", "backend", "technical"),
    ("r programming", "r,r-lang,r programming,rstats", "data", "technical"),
    ("typescript", "typescript,ts", "frontend", "technical"),
    ("lua", "lua", "backend", "technical"),
    ("fortran", "fortran", "backend", "technical"),
    ("cobol", "cobol", "backend", "technical"),
    ("assembly", "assembly,asm", "embedded", "technical"),
    ("matlab", "matlab,mat", "data", "technical"),
    ("vba", "vba,visual basic for applications", "backend", "technical"),
    ("powershell", "powershell,ps1,pwsh", "devops", "technical"),
    ("bash scripting", "bash,bash scripting,sh,shell", "devops", "technical"),
    ("solidity", "solidity,sol", "blockchain", "technical"),
    ("prolog", "prolog", "ai_ml", "technical"),
    ("lisp", "lisp,common lisp", "ai_ml", "technical"),
    ("ocaml", "ocaml,ml", "backend", "technical"),
    ("zig", "zig,ziglang", "backend", "technical"),
    ("nim", "nim,nimlang", "backend", "technical"),
    ("crystal", "crystal,crystallang", "backend", "technical"),
    ("v lang", "vlang,v lang,v", "backend", "technical"),
    ("d language", "d,dlang,d language", "backend", "technical"),
    ("mojo", "mojo,mojo lang", "ai_ml", "technical"),
    ("carbon", "carbon,carbon language", "backend", "technical"),
    ("hack", "hack,hacklang", "backend", "technical"),
    ("gdscript", "gdscript,gd script", "game_dev", "technical"),
    ("verilog", "verilog,system verilog", "embedded", "technical"),
    ("vhdl", "vhdl", "embedded", "technical"),
    ("tcl", "tcl,tcl/tk", "backend", "technical"),
    ("pascal", "pascal,delphi,object pascal", "backend", "technical"),
    ("scheme", "scheme,racket", "backend", "technical"),
    ("ada", "ada", "embedded", "technical"),
    ("apex", "apex,salesforce apex", "cloud", "technical"),
    ("abap", "abap,sap abap", "backend", "technical"),
    ("groovy scripting", "groovy script,groovy scripting", "devops", "technical"),
    ("coffeescript", "coffeescript,coffee", "frontend", "technical"),
    ("wasm", "wasm,webassembly,web assembly", "frontend", "technical"),
    ("glsl", "glsl,opengl shading", "game_dev", "technical"),
    ("hlsl", "hlsl,high level shading", "game_dev", "technical"),
    ("cuda programming", "cuda,cuda programming,nvidia cuda", "ai_ml", "technical"),
    ("openmp", "openmp,open mp", "backend", "technical"),
    ("mpi", "mpi,message passing interface", "backend", "technical"),
    ("cython", "cython", "backend", "technical"),
]
NEW_SKILLS.extend(_programming_languages)

# --- A2. Web Frameworks (80) ---
_web_frameworks = [
    ("react", "react,reactjs,react.js,react js", "frontend", "technical"),
    ("vue.js", "vue,vuejs,vue.js,vue 3", "frontend", "technical"),
    ("angular", "angular,angular 17,angular 18", "frontend", "technical"),
    ("next.js", "nextjs,next.js,next js", "fullstack", "technical"),
    ("nuxt.js", "nuxtjs,nuxt.js,nuxt", "fullstack", "technical"),
    ("svelte", "svelte,sveltejs", "frontend", "technical"),
    ("sveltekit", "sveltekit,svelte kit", "fullstack", "technical"),
    ("remix", "remix,remix run", "fullstack", "technical"),
    ("astro", "astro,astro build", "frontend", "technical"),
    ("solid.js", "solidjs,solid.js,solid js", "frontend", "technical"),
    ("qwik", "qwik,qwik js", "frontend", "technical"),
    ("ember.js", "ember,emberjs,ember.js", "frontend", "technical"),
    ("backbone.js", "backbone,backbonejs,backbone.js", "frontend", "technical"),
    ("alpine.js", "alpinejs,alpine.js,alpine js", "frontend", "technical"),
    ("htmx", "htmx", "frontend", "technical"),
    ("tailwind css", "tailwind,tailwindcss,tailwind css", "frontend", "technical"),
    ("sass", "sass,scss", "frontend", "technical"),
    ("styled components", "styled-components,styled components,css-in-js", "frontend", "technical"),
    ("material ui", "mui,material ui,material-ui", "frontend", "technical"),
    ("chakra ui", "chakra,chakra ui,chakra-ui", "frontend", "technical"),
    ("ant design", "antd,ant design,ant-design", "frontend", "technical"),
    ("storybook", "storybook", "frontend", "technical"),
    ("webpack", "webpack", "frontend", "technical"),
    ("vite", "vite,vitejs", "frontend", "technical"),
    ("esbuild", "esbuild", "frontend", "technical"),
    ("turbopack", "turbopack", "frontend", "technical"),
    ("rollup", "rollup,rollupjs", "frontend", "technical"),
    ("parcel", "parcel,parceljs", "frontend", "technical"),
    ("flask", "flask,python flask", "backend", "technical"),
    ("fastapi", "fastapi,fast api,fast-api", "backend", "technical"),
    ("express.js", "express,expressjs,express.js", "backend", "technical"),
    ("nestjs", "nestjs,nest.js,nest js", "backend", "technical"),
    ("koa.js", "koa,koajs,koa.js", "backend", "technical"),
    ("hapi.js", "hapi,hapijs,hapi.js", "backend", "technical"),
    ("fastify", "fastify", "backend", "technical"),
    ("adonis.js", "adonisjs,adonis.js,adonis", "backend", "technical"),
    ("ruby on rails", "rails,ruby on rails,ror", "backend", "technical"),
    ("sinatra", "sinatra,ruby sinatra", "backend", "technical"),
    ("asp.net core", "asp.net core,dotnet core,.net core", "backend", "technical"),
    ("blazor", "blazor,blazor wasm", "fullstack", "technical"),
    ("gin", "gin,gin-gonic,go gin", "backend", "technical"),
    ("echo go", "echo,go echo,echo framework", "backend", "technical"),
    ("fiber go", "fiber,go fiber,fiber framework", "backend", "technical"),
    ("actix web", "actix,actix-web,actix web", "backend", "technical"),
    ("rocket rust", "rocket,rust rocket", "backend", "technical"),
    ("phoenix", "phoenix,elixir phoenix", "backend", "technical"),
    ("play framework", "play,play framework,scala play", "backend", "technical"),
    ("micronaut", "micronaut", "backend", "technical"),
    ("quarkus", "quarkus,quarkus io", "backend", "technical"),
    ("vert.x", "vertx,vert.x,eclipse vert.x", "backend", "technical"),
    ("graphql", "graphql,gql,graph ql", "backend", "technical"),
    ("apollo graphql", "apollo,apollo graphql,apollo server", "backend", "technical"),
    ("prisma", "prisma,prisma orm", "backend", "technical"),
    ("sequelize", "sequelize", "backend", "technical"),
    ("typeorm", "typeorm,type orm", "backend", "technical"),
    ("drizzle orm", "drizzle,drizzle orm", "backend", "technical"),
    ("sqlalchemy", "sqlalchemy,sql alchemy", "backend", "technical"),
    ("deno", "deno,deno js", "backend", "technical"),
    ("bun", "bun,bunjs,bun runtime", "backend", "technical"),
    ("grpc", "grpc,grpc api,g-rpc", "backend", "technical"),
    ("trpc", "trpc,t-rpc,trpc api", "fullstack", "technical"),
    ("redux", "redux,redux toolkit,rtk", "frontend", "technical"),
    ("zustand", "zustand", "frontend", "technical"),
    ("mobx", "mobx,mob-x", "frontend", "technical"),
    ("recoil", "recoil,recoiljs", "frontend", "technical"),
    ("pinia", "pinia", "frontend", "technical"),
    ("tanstack query", "tanstack,react query,tanstack query", "frontend", "technical"),
    ("gatsby", "gatsby,gatsbyjs", "frontend", "technical"),
    ("eleventy", "eleventy,11ty", "frontend", "technical"),
    ("hugo", "hugo,gohugo", "frontend", "technical"),
    ("jekyll", "jekyll", "frontend", "technical"),
    ("three.js", "threejs,three.js,three js,webgl", "frontend", "technical"),
    ("d3.js", "d3,d3js,d3.js,d3 visualization", "frontend", "technical"),
    ("cypress", "cypress,cypress io", "frontend", "technical"),
    ("playwright", "playwright,ms playwright", "frontend", "technical"),
    ("puppeteer", "puppeteer", "frontend", "technical"),
    ("selenium", "selenium,selenium webdriver", "frontend", "technical"),
    ("jest", "jest,jestjs", "frontend", "technical"),
    ("vitest", "vitest", "frontend", "technical"),
    ("mocha", "mocha,mochajs", "frontend", "technical"),
]
NEW_SKILLS.extend(_web_frameworks)

# --- A3. Cloud Platforms (100) ---
# AWS (40)
_aws_services = [
    ("aws lambda", "lambda,aws lambda,serverless,faas", "cloud", "technical"),
    ("aws s3", "s3,aws s3,simple storage service", "cloud", "technical"),
    ("aws ec2", "ec2,aws ec2,elastic compute cloud", "cloud", "technical"),
    ("aws rds", "rds,aws rds,relational database service", "cloud", "technical"),
    ("aws dynamodb", "dynamodb,aws dynamodb,dynamo db", "cloud", "technical"),
    ("aws cloudformation", "cloudformation,aws cloudformation,cfn", "cloud", "technical"),
    ("aws eks", "eks,aws eks,elastic kubernetes service", "cloud", "technical"),
    ("aws ecs", "ecs,aws ecs,elastic container service", "cloud", "technical"),
    ("aws fargate", "fargate,aws fargate", "cloud", "technical"),
    ("aws sqs", "sqs,aws sqs,simple queue service", "cloud", "technical"),
    ("aws sns", "sns,aws sns,simple notification service", "cloud", "technical"),
    ("aws kinesis", "kinesis,aws kinesis,data streams", "cloud", "technical"),
    ("aws step functions", "step functions,aws step functions,sfn", "cloud", "technical"),
    ("aws api gateway", "api gateway,aws api gateway,apigw", "cloud", "technical"),
    ("aws cloudwatch", "cloudwatch,aws cloudwatch", "cloud", "technical"),
    ("aws iam", "aws iam,iam policies,identity access management", "cloud", "technical"),
    ("aws vpc", "vpc,aws vpc,virtual private cloud", "cloud", "technical"),
    ("aws route 53", "route53,route 53,aws route 53,dns service", "cloud", "technical"),
    ("aws cloudfront", "cloudfront,aws cloudfront,cdn", "cloud", "technical"),
    ("aws elasticache", "elasticache,aws elasticache,redis aws", "cloud", "technical"),
    ("aws redshift", "redshift,aws redshift,data warehouse aws", "cloud", "technical"),
    ("aws glue", "glue,aws glue,etl aws", "cloud", "technical"),
    ("aws athena", "athena,aws athena,serverless sql", "cloud", "technical"),
    ("aws sagemaker", "sagemaker,aws sagemaker,ml aws", "cloud", "technical"),
    ("aws cdk", "cdk,aws cdk,cloud development kit", "cloud", "technical"),
    ("aws amplify", "amplify,aws amplify", "cloud", "technical"),
    ("aws cognito", "cognito,aws cognito,auth aws", "cloud", "technical"),
    ("aws secrets manager", "secrets manager,aws secrets manager", "cloud", "technical"),
    ("aws eventbridge", "eventbridge,aws eventbridge,event bus", "cloud", "technical"),
    ("aws codecommit", "codecommit,aws codecommit", "cloud", "technical"),
    ("aws codepipeline", "codepipeline,aws codepipeline,cicd aws", "cloud", "technical"),
    ("aws codebuild", "codebuild,aws codebuild", "cloud", "technical"),
    ("aws codedeploy", "codedeploy,aws codedeploy", "cloud", "technical"),
    ("aws elastic beanstalk", "elastic beanstalk,beanstalk,eb", "cloud", "technical"),
    ("aws aurora", "aurora,aws aurora,aurora db", "cloud", "technical"),
    ("aws documentdb", "documentdb,aws documentdb", "cloud", "technical"),
    ("aws emr", "emr,aws emr,elastic mapreduce", "cloud", "technical"),
    ("aws msk", "msk,aws msk,managed kafka", "cloud", "technical"),
    ("aws waf", "waf,aws waf,web application firewall", "cloud", "technical"),
    ("aws organizations", "aws organizations,aws org,multi-account", "cloud", "technical"),
]
NEW_SKILLS.extend(_aws_services)

# Azure (30)
_azure_services = [
    ("azure app service", "app service,azure app service,azure web app", "cloud", "technical"),
    ("azure functions", "azure functions,az functions,serverless azure", "cloud", "technical"),
    ("azure cosmos db", "cosmosdb,cosmos db,azure cosmos db", "cloud", "technical"),
    ("azure kubernetes service", "aks,azure kubernetes,azure aks", "cloud", "technical"),
    ("azure devops", "azure devops,ado,azure pipelines", "cloud", "technical"),
    ("azure sql database", "azure sql,azure sql database", "cloud", "technical"),
    ("azure blob storage", "blob storage,azure blob,azure storage", "cloud", "technical"),
    ("azure active directory", "azure ad,aad,entra id,azure active directory", "cloud", "technical"),
    ("azure virtual machines", "azure vm,azure virtual machines,az vm", "cloud", "technical"),
    ("azure container instances", "aci,azure container instances,az container", "cloud", "technical"),
    ("azure container apps", "azure container apps,aca", "cloud", "technical"),
    ("azure event hub", "event hub,azure event hub,eventhub", "cloud", "technical"),
    ("azure service bus", "service bus,azure service bus,asb", "cloud", "technical"),
    ("azure key vault", "key vault,azure key vault,akv", "cloud", "technical"),
    ("azure logic apps", "logic apps,azure logic apps", "cloud", "technical"),
    ("azure data factory", "data factory,adf,azure data factory", "cloud", "technical"),
    ("azure synapse analytics", "synapse,azure synapse,synapse analytics", "cloud", "technical"),
    ("azure machine learning", "azure ml,azure machine learning,azureml", "cloud", "technical"),
    ("azure cognitive services", "cognitive services,azure cognitive,ai services", "cloud", "technical"),
    ("azure monitor", "azure monitor,application insights,az monitor", "cloud", "technical"),
    ("azure front door", "front door,azure front door,afd", "cloud", "technical"),
    ("azure cdn", "azure cdn", "cloud", "technical"),
    ("azure api management", "apim,azure api management,az apim", "cloud", "technical"),
    ("azure redis cache", "azure redis,azure redis cache", "cloud", "technical"),
    ("azure databricks", "databricks,azure databricks", "cloud", "technical"),
    ("azure openai service", "azure openai,azure gpt,aoai", "cloud", "technical"),
    ("azure static web apps", "static web apps,azure swa", "cloud", "technical"),
    ("azure bicep", "bicep,azure bicep,arm bicep", "cloud", "technical"),
    ("azure terraform", "azure terraform,terraform azure", "cloud", "technical"),
    ("azure sentinel", "sentinel,azure sentinel,siem azure", "cloud", "technical"),
]
NEW_SKILLS.extend(_azure_services)

# GCP (30)
_gcp_services = [
    ("google compute engine", "compute engine,gce,google compute", "cloud", "technical"),
    ("google cloud functions", "cloud functions,gcf,google functions", "cloud", "technical"),
    ("google bigquery", "bigquery,bq,google bigquery", "cloud", "technical"),
    ("google kubernetes engine", "gke,google kubernetes,gke cluster", "cloud", "technical"),
    ("google cloud run", "cloud run,google cloud run,gcloud run", "cloud", "technical"),
    ("google cloud storage", "gcs,google cloud storage,cloud storage", "cloud", "technical"),
    ("google pub/sub", "pubsub,pub/sub,google pub sub", "cloud", "technical"),
    ("google cloud sql", "cloud sql,google cloud sql", "cloud", "technical"),
    ("google firestore", "firestore,google firestore,cloud firestore", "cloud", "technical"),
    ("google spanner", "spanner,cloud spanner,google spanner", "cloud", "technical"),
    ("google dataflow", "dataflow,google dataflow,apache beam gcp", "cloud", "technical"),
    ("google dataproc", "dataproc,google dataproc,hadoop gcp", "cloud", "technical"),
    ("google vertex ai", "vertex ai,google vertex,vertex ml", "cloud", "technical"),
    ("google cloud composer", "cloud composer,google composer,airflow gcp", "cloud", "technical"),
    ("google cloud build", "cloud build,google cloud build,gcb", "cloud", "technical"),
    ("google artifact registry", "artifact registry,gar,google artifact", "cloud", "technical"),
    ("google cloud armor", "cloud armor,google armor,ddos gcp", "cloud", "technical"),
    ("google cloud iam", "gcp iam,google cloud iam", "cloud", "technical"),
    ("google cloud cdn", "google cdn,cloud cdn,gcp cdn", "cloud", "technical"),
    ("google cloud logging", "cloud logging,stackdriver,gcp logging", "cloud", "technical"),
    ("google cloud monitoring", "cloud monitoring,gcp monitoring", "cloud", "technical"),
    ("google apigee", "apigee,google apigee,api management gcp", "cloud", "technical"),
    ("google anthos", "anthos,google anthos,hybrid cloud gcp", "cloud", "technical"),
    ("google cloud memorystore", "memorystore,gcp redis,gcp memcached", "cloud", "technical"),
    ("google alloydb", "alloydb,google alloydb", "cloud", "technical"),
    ("google cloud tasks", "cloud tasks,google tasks", "cloud", "technical"),
    ("google cloud scheduler", "cloud scheduler,google scheduler", "cloud", "technical"),
    ("google looker", "looker,google looker,looker studio", "cloud", "technical"),
    ("google firebase", "firebase,google firebase,fcm", "cloud", "technical"),
    ("google cloud endpoints", "cloud endpoints,google endpoints", "cloud", "technical"),
]
NEW_SKILLS.extend(_gcp_services)

# --- A4. AI / ML / Data Science (120) ---
_ai_ml_frameworks = [
    ("tensorflow", "tensorflow,tf,tensorflow 2", "ai_ml", "technical"),
    ("pytorch", "pytorch,torch", "ai_ml", "technical"),
    ("keras", "keras", "ai_ml", "technical"),
    ("scikit-learn", "sklearn,scikit-learn,scikit learn", "ai_ml", "technical"),
    ("hugging face transformers", "huggingface,hugging face,transformers,hf", "ai_ml", "technical"),
    ("jax", "jax,google jax", "ai_ml", "technical"),
    ("xgboost", "xgboost,xgb", "ai_ml", "technical"),
    ("lightgbm", "lightgbm,lgbm,light gbm", "ai_ml", "technical"),
    ("catboost", "catboost", "ai_ml", "technical"),
    ("fastai", "fastai,fast.ai", "ai_ml", "technical"),
    ("onnx", "onnx,open neural network exchange", "ai_ml", "technical"),
    ("pandas", "pandas,pd", "data", "technical"),
    ("numpy", "numpy,np", "data", "technical"),
    ("scipy", "scipy", "data", "technical"),
    ("matplotlib", "matplotlib,mpl", "data", "technical"),
    ("seaborn", "seaborn,sns", "data", "technical"),
    ("plotly", "plotly,plotly express", "data", "technical"),
    ("statsmodels", "statsmodels", "data", "technical"),
    ("polars", "polars", "data", "technical"),
    ("dask", "dask,dask distributed", "data", "technical"),
]
NEW_SKILLS.extend(_ai_ml_frameworks)

_llm_genai = [
    ("large language models", "llm,large language models,llms", "ai_ml", "technical"),
    ("gpt models", "gpt,gpt-4,gpt-3.5,chatgpt,openai gpt", "ai_ml", "technical"),
    ("bert", "bert,distilbert,roberta", "ai_ml", "technical"),
    ("langchain", "langchain,lang chain", "ai_ml", "technical"),
    ("llamaindex", "llamaindex,llama index,gpt index", "ai_ml", "technical"),
    ("retrieval augmented generation", "rag,retrieval augmented generation", "ai_ml", "technical"),
    ("prompt engineering", "prompt engineering,prompt design,prompting", "ai_ml", "technical"),
    ("fine tuning llms", "fine tuning,fine-tuning,finetuning,lora,qlora", "ai_ml", "technical"),
    ("vector databases", "vector db,vector databases,vector store", "ai_ml", "technical"),
    ("embeddings", "embeddings,word embeddings,sentence embeddings", "ai_ml", "technical"),
    ("openai api", "openai api,openai,chatgpt api", "ai_ml", "technical"),
    ("anthropic claude", "claude,anthropic,claude api", "ai_ml", "technical"),
    ("stable diffusion", "stable diffusion,sd,diffusion models", "ai_ml", "technical"),
    ("midjourney", "midjourney,midjourney ai", "ai_ml", "technical"),
    ("ai agents", "ai agents,autonomous agents,agent framework", "ai_ml", "technical"),
    ("autogen", "autogen,microsoft autogen", "ai_ml", "technical"),
    ("crewai", "crewai,crew ai", "ai_ml", "technical"),
    ("semantic kernel", "semantic kernel,sk,microsoft semantic kernel", "ai_ml", "technical"),
    ("llama", "llama,llama 2,llama 3,meta llama", "ai_ml", "technical"),
    ("mistral", "mistral,mistral ai,mixtral", "ai_ml", "technical"),
    ("gemini api", "gemini,google gemini,gemini api", "ai_ml", "technical"),
    ("copilot integration", "copilot,github copilot,ai coding assistant", "ai_ml", "technical"),
    ("ai ethics", "ai ethics,responsible ai,ai fairness,ai bias", "ai_ml", "technical"),
    ("generative ai", "genai,generative ai,generative artificial intelligence", "ai_ml", "technical"),
    ("multimodal ai", "multimodal,multimodal ai,vision language model", "ai_ml", "technical"),
]
NEW_SKILLS.extend(_llm_genai)

_mlops = [
    ("mlflow", "mlflow,ml flow", "ai_ml", "technical"),
    ("kubeflow", "kubeflow,kube flow", "ai_ml", "technical"),
    ("weights and biases", "wandb,weights and biases,w&b", "ai_ml", "technical"),
    ("dvc", "dvc,data version control", "ai_ml", "technical"),
    ("feature store", "feature store,feast,tecton", "ai_ml", "technical"),
    ("model serving", "model serving,model deployment,model inference", "ai_ml", "technical"),
    ("triton inference server", "triton,triton inference,nvidia triton", "ai_ml", "technical"),
    ("bentoml", "bentoml,bento ml", "ai_ml", "technical"),
    ("seldon core", "seldon,seldon core", "ai_ml", "technical"),
    ("ml monitoring", "ml monitoring,model monitoring,data drift", "ai_ml", "technical"),
    ("experiment tracking", "experiment tracking,ml experiments", "ai_ml", "technical"),
    ("model registry", "model registry,ml model registry", "ai_ml", "technical"),
    ("label studio", "label studio,data labeling,annotation tool", "ai_ml", "technical"),
    ("great expectations", "great expectations,data validation,ge", "data", "technical"),
    ("evidently ai", "evidently,evidently ai,ml observability", "ai_ml", "technical"),
]
NEW_SKILLS.extend(_mlops)

_big_data = [
    ("apache spark", "spark,apache spark,pyspark,spark sql", "data", "technical"),
    ("apache kafka", "kafka,apache kafka,kafka streams", "data", "technical"),
    ("apache airflow", "airflow,apache airflow,dag", "data", "technical"),
    ("apache flink", "flink,apache flink,stream processing", "data", "technical"),
    ("apache beam", "beam,apache beam,dataflow sdk", "data", "technical"),
    ("apache nifi", "nifi,apache nifi,data flow", "data", "technical"),
    ("apache cassandra advanced", "cassandra tuning,cassandra data modeling", "data", "technical"),
    ("apache druid", "druid,apache druid,olap", "data", "technical"),
    ("apache iceberg", "iceberg,apache iceberg,table format", "data", "technical"),
    ("delta lake", "delta lake,delta,databricks delta", "data", "technical"),
    ("apache hudi", "hudi,apache hudi", "data", "technical"),
    ("presto", "presto,trino,presto sql", "data", "technical"),
    ("dbt", "dbt,data build tool,dbt core", "data", "technical"),
    ("snowflake", "snowflake,snowflake db,snowflake data cloud", "data", "technical"),
    ("databricks platform", "databricks,databricks platform,lakehouse", "data", "technical"),
    ("data lakehouse", "lakehouse,data lakehouse,lake house", "data", "technical"),
    ("data mesh", "data mesh,data domain,data as product", "data", "technical"),
    ("data governance", "data governance,data quality,data catalog", "data", "technical"),
    ("data pipeline", "data pipeline,etl pipeline,elt", "data", "technical"),
    ("streaming analytics", "streaming analytics,real-time analytics", "data", "technical"),
]
NEW_SKILLS.extend(_big_data)

_bi_tools = [
    ("power bi", "power bi,powerbi,pbi", "analytics", "technical"),
    ("looker", "looker,google looker,looker studio", "analytics", "technical"),
    ("metabase", "metabase", "analytics", "technical"),
    ("apache superset", "superset,apache superset", "analytics", "technical"),
    ("qlik", "qlik,qlikview,qlik sense", "analytics", "technical"),
    ("sisense", "sisense", "analytics", "technical"),
    ("grafana dashboards", "grafana dashboard,grafana viz", "analytics", "technical"),
    ("google data studio", "data studio,google data studio,looker studio", "analytics", "technical"),
    ("excel analytics", "excel,advanced excel,excel analytics,pivot tables", "analytics", "technical"),
    ("jupyter notebooks", "jupyter,jupyter notebook,jupyterlab,ipynb", "data", "technical"),
]
NEW_SKILLS.extend(_bi_tools)

_computer_vision = [
    ("opencv", "opencv,cv2,open cv", "ai_ml", "technical"),
    ("yolo", "yolo,yolov5,yolov8,ultralytics", "ai_ml", "technical"),
    ("object detection", "object detection,object recognition", "ai_ml", "technical"),
    ("image segmentation", "image segmentation,semantic segmentation,instance segmentation", "ai_ml", "technical"),
    ("ocr", "ocr,optical character recognition,tesseract", "ai_ml", "technical"),
    ("face recognition", "face recognition,face detection,facial recognition", "ai_ml", "technical"),
    ("image classification", "image classification,image recognition", "ai_ml", "technical"),
    ("pose estimation", "pose estimation,human pose,mediapipe", "ai_ml", "technical"),
    ("3d vision", "3d vision,point cloud,depth estimation", "ai_ml", "technical"),
    ("video analytics", "video analytics,video processing,video ai", "ai_ml", "technical"),
]
NEW_SKILLS.extend(_computer_vision)

_nlp = [
    ("spacy", "spacy,spacy nlp", "ai_ml", "technical"),
    ("nltk", "nltk,natural language toolkit", "ai_ml", "technical"),
    ("text classification", "text classification,sentiment analysis,text categorization", "ai_ml", "technical"),
    ("named entity recognition", "ner,named entity recognition,entity extraction", "ai_ml", "technical"),
    ("topic modeling", "topic modeling,lda,topic extraction", "ai_ml", "technical"),
    ("machine translation", "machine translation,neural translation,nmt", "ai_ml", "technical"),
    ("speech recognition", "speech recognition,asr,speech to text,stt", "ai_ml", "technical"),
    ("text generation", "text generation,language generation,nlg", "ai_ml", "technical"),
    ("question answering", "question answering,qa system,reading comprehension", "ai_ml", "technical"),
    ("chatbot development", "chatbot,conversational ai,dialog systems", "ai_ml", "technical"),
    ("text summarization", "text summarization,abstractive summarization,extractive summarization", "ai_ml", "technical"),
    ("information retrieval", "information retrieval,search ranking,document retrieval", "ai_ml", "technical"),
    ("knowledge graphs", "knowledge graph,ontology,knowledge base", "ai_ml", "technical"),
    ("text analytics", "text analytics,text mining,corpus analysis", "ai_ml", "technical"),
    ("tokenization", "tokenization,subword tokenization,bpe", "ai_ml", "technical"),
]
NEW_SKILLS.extend(_nlp)

# --- A5. DevOps & Infrastructure (80) ---
_containers = [
    ("docker", "docker,dockerfile,docker-compose,containers", "devops", "technical"),
    ("kubernetes", "kubernetes,k8s,kube,container orchestration", "devops", "technical"),
    ("helm charts", "helm,helm charts,helm chart,k8s helm", "devops", "technical"),
    ("podman", "podman,pod manager", "devops", "technical"),
    ("containerd", "containerd,container runtime", "devops", "technical"),
    ("docker swarm", "docker swarm,swarm mode", "devops", "technical"),
    ("container security", "container security,image scanning,trivy", "devops", "technical"),
    ("openshift", "openshift,red hat openshift,ocp", "devops", "technical"),
    ("rancher", "rancher,rancher desktop", "devops", "technical"),
    ("k3s", "k3s,lightweight kubernetes", "devops", "technical"),
]
NEW_SKILLS.extend(_containers)

_cicd = [
    ("jenkins", "jenkins,jenkins ci,jenkins pipeline", "devops", "technical"),
    ("gitlab ci", "gitlab ci,gitlab ci/cd,gitlab runner", "devops", "technical"),
    ("github actions", "github actions,gha,gh actions", "devops", "technical"),
    ("circleci", "circleci,circle ci", "devops", "technical"),
    ("argocd", "argocd,argo cd,argo gitops", "devops", "technical"),
    ("tekton", "tekton,tekton pipelines", "devops", "technical"),
    ("azure pipelines", "azure pipelines,ado pipelines", "devops", "technical"),
    ("aws codepipeline advanced", "codepipeline advanced,aws cicd", "devops", "technical"),
    ("drone ci", "drone,drone ci", "devops", "technical"),
    ("buildkite", "buildkite", "devops", "technical"),
    ("spinnaker", "spinnaker,continuous delivery", "devops", "technical"),
    ("flux cd", "flux,fluxcd,flux cd,gitops", "devops", "technical"),
    ("harness", "harness,harness io,harness cd", "devops", "technical"),
    ("bamboo", "bamboo,atlassian bamboo", "devops", "technical"),
    ("travis ci", "travis,travis ci,travisci", "devops", "technical"),
]
NEW_SKILLS.extend(_cicd)

_iac = [
    ("terraform", "terraform,tf,hcl,hashicorp terraform", "devops", "technical"),
    ("ansible", "ansible,ansible playbook,ansible automation", "devops", "technical"),
    ("pulumi", "pulumi", "devops", "technical"),
    ("cloudformation advanced", "cloudformation advanced,cfn templates,aws iac", "devops", "technical"),
    ("chef", "chef,chef infra,chef cookbook", "devops", "technical"),
    ("puppet", "puppet,puppet enterprise", "devops", "technical"),
    ("saltstack", "saltstack,salt,salt automation", "devops", "technical"),
    ("vagrant", "vagrant,vagrantfile,hashicorp vagrant", "devops", "technical"),
    ("packer", "packer,hashicorp packer,image builder", "devops", "technical"),
    ("crossplane", "crossplane,k8s crossplane", "devops", "technical"),
]
NEW_SKILLS.extend(_iac)

_monitoring = [
    ("prometheus", "prometheus,prom,prometheus monitoring", "devops", "technical"),
    ("grafana", "grafana,grafana dashboard", "devops", "technical"),
    ("datadog", "datadog,dd,datadog monitoring", "devops", "technical"),
    ("new relic", "new relic,newrelic,nr", "devops", "technical"),
    ("elk stack", "elk,elk stack,elasticsearch logstash kibana", "devops", "technical"),
    ("kibana", "kibana", "devops", "technical"),
    ("logstash", "logstash,log pipeline", "devops", "technical"),
    ("fluentd", "fluentd,fluentbit,fluent bit", "devops", "technical"),
    ("jaeger", "jaeger,jaeger tracing,distributed tracing", "devops", "technical"),
    ("opentelemetry", "opentelemetry,otel,observability", "devops", "technical"),
    ("zipkin", "zipkin", "devops", "technical"),
    ("pagerduty", "pagerduty,incident management", "devops", "technical"),
    ("opsgenie", "opsgenie,ops genie", "devops", "technical"),
    ("nagios", "nagios,nagios monitoring", "devops", "technical"),
    ("zabbix", "zabbix,zabbix monitoring", "devops", "technical"),
    ("dynatrace", "dynatrace,dt", "devops", "technical"),
    ("appdynamics", "appdynamics,appd", "devops", "technical"),
    ("splunk observability", "splunk observability,splunk apm", "devops", "technical"),
]
NEW_SKILLS.extend(_monitoring)

_service_mesh = [
    ("istio", "istio,istio mesh,istio service mesh", "devops", "technical"),
    ("linkerd", "linkerd,linkerd mesh", "devops", "technical"),
    ("consul", "consul,hashicorp consul,consul connect", "devops", "technical"),
    ("envoy proxy", "envoy,envoy proxy,envoyproxy", "devops", "technical"),
    ("nginx", "nginx,nginx proxy,nginx reverse proxy", "devops", "technical"),
    ("traefik", "traefik,traefik proxy", "devops", "technical"),
    ("haproxy", "haproxy,ha proxy,load balancer", "devops", "technical"),
]
NEW_SKILLS.extend(_service_mesh)

_devops_misc = [
    ("site reliability engineering", "sre,site reliability,site reliability engineering", "devops", "technical"),
    ("chaos engineering", "chaos engineering,chaos monkey,litmus", "devops", "technical"),
    ("platform engineering", "platform engineering,internal developer platform,idp", "devops", "technical"),
    ("infrastructure as code", "iac,infrastructure as code", "devops", "technical"),
    ("configuration management", "config management,configuration management", "devops", "technical"),
    ("release management", "release management,release engineering", "devops", "technical"),
    ("incident management", "incident management,incident response,postmortem", "devops", "technical"),
    ("capacity planning", "capacity planning,resource planning", "devops", "technical"),
    ("blue green deployment", "blue green,blue-green deployment,canary deployment", "devops", "technical"),
    ("feature flags", "feature flags,feature toggles,launchdarkly", "devops", "technical"),
    ("vault", "vault,hashicorp vault,secrets management", "devops", "technical"),
    ("service catalog", "service catalog,backstage,developer portal", "devops", "technical"),
    ("gitops", "gitops,git ops,gitops workflow", "devops", "technical"),
]
NEW_SKILLS.extend(_devops_misc)

# --- A6. Database Systems (50) ---
_databases = [
    ("postgresql advanced", "postgresql tuning,pg advanced,postgres optimization", "database", "technical"),
    ("mysql advanced", "mysql tuning,mysql optimization,mysql 8", "database", "technical"),
    ("oracle database", "oracle db,oracle database,oracle 19c", "database", "technical"),
    ("sql server", "sql server,mssql,microsoft sql server", "database", "technical"),
    ("mariadb", "mariadb,maria db", "database", "technical"),
    ("cockroachdb", "cockroachdb,cockroach db,crdb", "database", "technical"),
    ("vitess", "vitess,mysql sharding", "database", "technical"),
    ("mongodb advanced", "mongodb atlas,mongo aggregation,mongodb advanced", "database", "technical"),
    ("cassandra database", "cassandra db,apache cassandra,cql", "database", "technical"),
    ("redis", "redis,redis cache,redis cluster", "database", "technical"),
    ("elasticsearch", "elasticsearch,es,elastic search,opensearch", "database", "technical"),
    ("neo4j", "neo4j,graph database,cypher", "database", "technical"),
    ("dgraph", "dgraph,graph db", "database", "technical"),
    ("arangodb", "arangodb,arango db,multi-model db", "database", "technical"),
    ("couchdb", "couchdb,couch db,apache couchdb", "database", "technical"),
    ("couchbase", "couchbase,couchbase server", "database", "technical"),
    ("influxdb", "influxdb,influx db,time series db", "database", "technical"),
    ("timescaledb", "timescaledb,timescale db,timescale", "database", "technical"),
    ("questdb", "questdb,quest db", "database", "technical"),
    ("pinecone", "pinecone,pinecone db,vector search", "database", "technical"),
    ("weaviate", "weaviate,weaviate db", "database", "technical"),
    ("milvus", "milvus,milvus db,vector similarity", "database", "technical"),
    ("chroma", "chroma,chromadb,chroma db", "database", "technical"),
    ("qdrant", "qdrant,qdrant db", "database", "technical"),
    ("pgvector", "pgvector,pg vector,postgresql vector", "database", "technical"),
    ("fauna", "fauna,faunadb,fauna db", "database", "technical"),
    ("supabase", "supabase,supa base", "database", "technical"),
    ("planetscale", "planetscale,planet scale", "database", "technical"),
    ("neon", "neon,neon db,neon postgres", "database", "technical"),
    ("database design", "database design,db schema,normalization", "database", "technical"),
    ("database replication", "replication,db replication,master-slave", "database", "technical"),
    ("database sharding", "sharding,db sharding,horizontal scaling", "database", "technical"),
    ("database migration", "migration,db migration,schema migration,flyway,liquibase", "database", "technical"),
    ("sql optimization", "sql optimization,query optimization,query tuning,explain plan", "database", "technical"),
    ("stored procedures", "stored procedures,plpgsql,t-sql,pl/sql", "database", "technical"),
    ("database backup recovery", "backup,recovery,db backup,point in time recovery,pitr", "database", "technical"),
    ("memcached", "memcached,memory cache", "database", "technical"),
    ("graph databases", "graph databases,graph db concepts,property graph", "database", "technical"),
    ("data modeling", "data modeling,er diagram,dimensional modeling", "database", "technical"),
    ("database indexing", "indexing,db indexing,b-tree,hash index", "database", "technical"),
]
NEW_SKILLS.extend(_databases)

# --- A7. Security & Compliance (40) ---
_security = [
    ("owasp", "owasp,owasp top 10,web security", "security", "technical"),
    ("burp suite", "burp suite,burp,burpsuite", "security", "technical"),
    ("metasploit", "metasploit,msfconsole", "security", "technical"),
    ("wireshark", "wireshark,packet analysis", "security", "technical"),
    ("nmap", "nmap,network scanner,port scanning", "security", "technical"),
    ("penetration testing", "pentest,penetration testing,ethical hacking", "security", "technical"),
    ("vulnerability assessment", "vulnerability assessment,vuln scan,vulnerability scanning", "security", "technical"),
    ("siem", "siem,security information event management", "security", "technical"),
    ("zero trust architecture", "zero trust,ztna,zero trust architecture", "security", "technical"),
    ("identity access management", "iam,identity access management,access control", "security", "technical"),
    ("privileged access management", "pam,privileged access,cyberark", "security", "technical"),
    ("security operations", "secops,security operations,soc", "security", "technical"),
    ("threat modeling", "threat modeling,stride,attack surface", "security", "technical"),
    ("incident response", "incident response,ir,security incident", "security", "technical"),
    ("devsecops", "devsecops,dev sec ops,security pipeline", "security", "technical"),
    ("application security", "appsec,application security,secure coding", "security", "technical"),
    ("network security", "network security,netsec,network defense", "security", "technical"),
    ("cloud security", "cloud security,cspm,cloud security posture", "security", "technical"),
    ("endpoint security", "endpoint security,edr,endpoint detection", "security", "technical"),
    ("cryptography", "cryptography,encryption,crypto,tls,ssl", "security", "technical"),
    ("malware analysis", "malware analysis,reverse engineering,malware", "security", "technical"),
    ("forensics", "digital forensics,forensics,cyber forensics", "security", "technical"),
    ("security automation", "security automation,soar,automated security", "security", "technical"),
    ("api security", "api security,oauth,jwt,api auth", "security", "technical"),
    ("web application firewall", "waf,web application firewall,mod security", "security", "technical"),
    ("data loss prevention", "dlp,data loss prevention,data protection", "security", "technical"),
    ("security audit", "security audit,compliance audit,security review", "security", "technical"),
    ("soc2 compliance", "soc2,soc 2,service organization control", "security", "technical"),
    ("gdpr compliance", "gdpr,general data protection regulation,data privacy", "security", "technical"),
    ("hipaa compliance", "hipaa,health insurance portability", "security", "technical"),
    ("pci dss compliance", "pci dss,pci-dss,payment card industry", "security", "technical"),
    ("iso 27001", "iso 27001,isms,information security management", "security", "technical"),
    ("nist framework", "nist,nist cybersecurity,nist framework", "security", "technical"),
    ("fedramp", "fedramp,federal risk authorization", "security", "technical"),
    ("sox compliance", "sox,sarbanes oxley,sox compliance", "security", "technical"),
    ("container security scanning", "trivy,snyk container,aqua security", "security", "technical"),
    ("secret scanning", "secret scanning,git secrets,credential scanning", "security", "technical"),
    ("sast", "sast,static application security testing,code scanning", "security", "technical"),
    ("dast", "dast,dynamic application security testing", "security", "technical"),
    ("sbom", "sbom,software bill of materials,supply chain security", "security", "technical"),
]
NEW_SKILLS.extend(_security)

# --- A8. Mobile Development (30) ---
_mobile = [
    ("react native", "react native,rn,react-native", "mobile", "technical"),
    ("flutter", "flutter,flutter sdk,dart flutter", "mobile", "technical"),
    ("swiftui", "swiftui,swift ui", "mobile", "technical"),
    ("jetpack compose", "jetpack compose,compose,android compose", "mobile", "technical"),
    ("kotlin multiplatform", "kmp,kotlin multiplatform,kmm", "mobile", "technical"),
    ("ionic", "ionic,ionic framework", "mobile", "technical"),
    ("capacitor", "capacitor,capacitorjs", "mobile", "technical"),
    ("expo", "expo,expo react native", "mobile", "technical"),
    ("maui", "maui,.net maui,dotnet maui", "mobile", "technical"),
    ("app clips", "app clips,ios app clips", "mobile", "technical"),
    ("widgets ios", "widgetkit,ios widgets", "mobile", "technical"),
    ("arkit", "arkit,ar kit,augmented reality ios", "mobile", "technical"),
    ("arcore", "arcore,ar core,augmented reality android", "mobile", "technical"),
    ("core data", "core data,coredata,ios persistence", "mobile", "technical"),
    ("room database", "room,room database,android room", "mobile", "technical"),
    ("realm", "realm,realm db,realm mobile", "mobile", "technical"),
    ("firebase mobile", "firebase mobile,firebase sdk,crashlytics", "mobile", "technical"),
    ("push notifications", "push notifications,apns,fcm push", "mobile", "technical"),
    ("mobile ui testing", "xctest,espresso,mobile testing", "mobile", "technical"),
    ("mobile ci cd", "fastlane,mobile ci cd,app distribution", "mobile", "technical"),
    ("app store optimization", "aso,app store optimization,play store optimization", "mobile", "technical"),
    ("mobile analytics", "mobile analytics,firebase analytics,mixpanel", "mobile", "technical"),
    ("mobile performance", "mobile performance,app performance,battery optimization", "mobile", "technical"),
    ("cross platform development", "cross platform,multiplatform,cross-platform", "mobile", "technical"),
    ("responsive design", "responsive,responsive design,adaptive layout", "mobile", "technical"),
    ("pwa", "pwa,progressive web app,progressive web application", "mobile", "technical"),
    ("mobile security", "mobile security,app security,mobile encryption", "mobile", "technical"),
    ("wear os", "wear os,wearables,smartwatch dev", "mobile", "technical"),
    ("tvos development", "tvos,apple tv,tv development", "mobile", "technical"),
    ("mobile deep linking", "deep linking,universal links,app links", "mobile", "technical"),
]
NEW_SKILLS.extend(_mobile)

# --- A9. Blockchain & Web3 (20) ---
_blockchain = [
    ("ethereum", "ethereum,eth,ethereum blockchain", "blockchain", "technical"),
    ("smart contracts", "smart contracts,smart contract development", "blockchain", "technical"),
    ("web3.js", "web3,web3.js,web3js", "blockchain", "technical"),
    ("ethers.js", "ethers,ethers.js,ethersjs", "blockchain", "technical"),
    ("hardhat", "hardhat,hardhat dev", "blockchain", "technical"),
    ("truffle", "truffle,truffle suite", "blockchain", "technical"),
    ("ipfs", "ipfs,interplanetary file system", "blockchain", "technical"),
    ("defi", "defi,decentralized finance", "blockchain", "technical"),
    ("nft development", "nft,nft development,erc-721", "blockchain", "technical"),
    ("dao", "dao,decentralized autonomous organization", "blockchain", "technical"),
    ("polygon", "polygon,matic,polygon network", "blockchain", "technical"),
    ("solana", "solana,sol", "blockchain", "technical"),
    ("avalanche", "avalanche,avax", "blockchain", "technical"),
    ("hyperledger", "hyperledger,hyperledger fabric", "blockchain", "technical"),
    ("cosmos blockchain", "cosmos,cosmos sdk,tendermint", "blockchain", "technical"),
    ("layer 2 solutions", "layer 2,l2,rollups,optimistic rollup,zk rollup", "blockchain", "technical"),
    ("tokenomics", "tokenomics,token economics,token design", "blockchain", "technical"),
    ("blockchain security", "smart contract audit,blockchain security", "blockchain", "technical"),
    ("rust blockchain", "rust blockchain,substrate,polkadot", "blockchain", "technical"),
    ("zero knowledge proofs", "zk proofs,zero knowledge,zkp,zk-snark", "blockchain", "technical"),
]
NEW_SKILLS.extend(_blockchain)

# --- A10. Game Development (15) ---
_game_dev = [
    ("unity", "unity,unity3d,unity game engine", "game_dev", "technical"),
    ("unreal engine", "unreal,unreal engine,ue5,ue4", "game_dev", "technical"),
    ("godot", "godot,godot engine", "game_dev", "technical"),
    ("game design", "game design,level design,game mechanics", "game_dev", "technical"),
    ("game physics", "game physics,physics engine,rigidbody", "game_dev", "technical"),
    ("shader programming", "shader,shader programming,compute shader", "game_dev", "technical"),
    ("3d modeling", "3d modeling,blender,maya,3ds max", "game_dev", "technical"),
    ("game ai", "game ai,pathfinding,behavior trees,npc ai", "game_dev", "technical"),
    ("multiplayer networking", "multiplayer,netcode,game networking", "game_dev", "technical"),
    ("procedural generation", "procedural generation,procgen,procedural content", "game_dev", "technical"),
    ("directx", "directx,dx12,direct3d", "game_dev", "technical"),
    ("vulkan", "vulkan,vulkan api", "game_dev", "technical"),
    ("opengl", "opengl,opengl es", "game_dev", "technical"),
    ("xr development", "xr,vr,ar,mixed reality,virtual reality", "game_dev", "technical"),
    ("game optimization", "game optimization,fps optimization,lod,occlusion culling", "game_dev", "technical"),
]
NEW_SKILLS.extend(_game_dev)

# --- A11. Embedded Systems (15) ---
_embedded = [
    ("arduino", "arduino,arduino ide,arduino programming", "embedded", "technical"),
    ("raspberry pi", "raspberry pi,rpi,raspi", "embedded", "technical"),
    ("rtos", "rtos,real time os,freertos,real-time operating system", "embedded", "technical"),
    ("firmware development", "firmware,firmware dev,firmware programming", "embedded", "technical"),
    ("embedded c", "embedded c,embedded c++,bare metal", "embedded", "technical"),
    ("iot protocols", "mqtt,coap,iot protocols,zigbee,ble", "embedded", "technical"),
    ("fpga", "fpga,field programmable gate array,xilinx", "embedded", "technical"),
    ("pcb design", "pcb,pcb design,circuit board,kicad", "embedded", "technical"),
    ("embedded linux", "embedded linux,yocto,buildroot", "embedded", "technical"),
    ("microcontrollers", "microcontroller,mcu,stm32,esp32,pic", "embedded", "technical"),
    ("can bus", "can bus,can protocol,automotive bus", "embedded", "technical"),
    ("signal processing", "dsp,digital signal processing,signal processing", "embedded", "technical"),
    ("sensor integration", "sensor,accelerometer,gyroscope,lidar", "embedded", "technical"),
    ("edge computing", "edge computing,edge ai,edge deployment", "embedded", "technical"),
    ("robotics", "robotics,ros,robot operating system", "embedded", "technical"),
]
NEW_SKILLS.extend(_embedded)

# ──────────────────────────────────────────────────────────────────────
# B. SOFT SKILLS  (~150)
# ──────────────────────────────────────────────────────────────────────

# --- B1. Communication (30) ---
_communication = [
    ("technical writing", "technical writing,tech writing,documentation writing", "communication", "soft"),
    ("presentation skills", "presentations,presentation skills,public speaking", "communication", "soft"),
    ("stakeholder management", "stakeholder management,stakeholder communication,stakeholder engagement", "communication", "soft"),
    ("documentation", "documentation,technical documentation,docs", "communication", "soft"),
    ("code review skills", "code review,peer review,code review skills", "communication", "soft"),
    ("active listening", "active listening,listening skills", "communication", "soft"),
    ("verbal communication", "verbal communication,oral communication", "communication", "soft"),
    ("cross functional communication", "cross functional,cross-functional communication,interdepartmental", "communication", "soft"),
    ("client communication", "client communication,client facing,customer communication", "communication", "soft"),
    ("email communication", "email communication,professional email,written correspondence", "communication", "soft"),
    ("negotiation skills", "negotiation,negotiation skills,deal making", "communication", "soft"),
    ("conflict resolution", "conflict resolution,dispute resolution,mediation", "communication", "soft"),
    ("feedback delivery", "feedback,giving feedback,constructive feedback", "communication", "soft"),
    ("storytelling", "storytelling,narrative,data storytelling", "communication", "soft"),
    ("facilitation", "facilitation,meeting facilitation,workshop facilitation", "communication", "soft"),
    ("persuasion", "persuasion,influence,convincing", "communication", "soft"),
    ("technical evangelism", "tech evangelism,developer advocacy,developer relations", "communication", "soft"),
    ("knowledge sharing", "knowledge sharing,knowledge transfer,brown bag", "communication", "soft"),
    ("report writing", "report writing,reporting,status reporting", "communication", "soft"),
    ("proposal writing", "proposal writing,rfp,business proposal", "communication", "soft"),
    ("intercultural communication", "intercultural,cross-cultural,global communication", "communication", "soft"),
    ("remote communication", "remote communication,async communication,virtual collaboration", "communication", "soft"),
    ("whiteboard sessions", "whiteboarding,whiteboard sessions,visual communication", "communication", "soft"),
    ("technical presentations", "tech talks,tech presentations,lightning talks", "communication", "soft"),
    ("api documentation", "api docs,api documentation,swagger docs", "communication", "soft"),
    ("user documentation", "user docs,user guides,end user documentation", "communication", "soft"),
    ("release notes", "release notes,changelog,version notes", "communication", "soft"),
    ("design documents", "design docs,design documents,rfc", "communication", "soft"),
    ("architecture decision records", "adr,architecture decision records,decision log", "communication", "soft"),
    ("runbook creation", "runbook,playbook,operational docs", "communication", "soft"),
]
NEW_SKILLS.extend(_communication)

# --- B2. Leadership (40) ---
_leadership = [
    ("team leadership", "team leadership,team lead,tech lead", "leadership", "soft"),
    ("mentoring", "mentoring,coaching,mentorship", "leadership", "soft"),
    ("strategic thinking", "strategic thinking,strategy,strategic planning", "leadership", "soft"),
    ("people management", "people management,people manager,direct reports", "leadership", "soft"),
    ("change management", "change management,organizational change,transformation", "leadership", "soft"),
    ("engineering management", "engineering management,eng management,engineering manager", "leadership", "soft"),
    ("product vision", "product vision,product strategy,product thinking", "leadership", "soft"),
    ("talent development", "talent development,career development,growth plans", "leadership", "soft"),
    ("performance management", "performance management,performance reviews,1:1s", "leadership", "soft"),
    ("hiring and interviewing", "hiring,interviewing,talent acquisition,recruiting", "leadership", "soft"),
    ("delegation", "delegation,task delegation,empowerment", "leadership", "soft"),
    ("team building", "team building,team bonding,team culture", "leadership", "soft"),
    ("decision making", "decision making,data-driven decisions,decision framework", "leadership", "soft"),
    ("emotional intelligence", "emotional intelligence,eq,empathy,self-awareness", "leadership", "soft"),
    ("servant leadership", "servant leadership,servant leader", "leadership", "soft"),
    ("technical strategy", "technical strategy,tech strategy,technology roadmap", "leadership", "soft"),
    ("architectural leadership", "architectural leadership,tech direction", "leadership", "soft"),
    ("cross team collaboration", "cross team,cross-team collaboration,inter-team", "leadership", "soft"),
    ("stakeholder alignment", "stakeholder alignment,alignment,consensus building", "leadership", "soft"),
    ("budget management", "budget management,cost management,financial planning", "leadership", "soft"),
    ("vendor management", "vendor management,vendor selection,vendor evaluation", "leadership", "soft"),
    ("organizational design", "org design,organizational design,team structure", "leadership", "soft"),
    ("succession planning", "succession planning,leadership pipeline", "leadership", "soft"),
    ("diversity inclusion", "dei,diversity inclusion,diversity equity inclusion", "leadership", "soft"),
    ("executive communication", "executive communication,c-suite,board presentations", "leadership", "soft"),
    ("vision setting", "vision setting,mission,north star", "leadership", "soft"),
    ("accountability", "accountability,ownership,responsible", "leadership", "soft"),
    ("resilience", "resilience,adaptability,grit", "leadership", "soft"),
    ("innovation leadership", "innovation leadership,innovation culture,intrapreneurship", "leadership", "soft"),
    ("thought leadership", "thought leadership,industry expert,subject matter expert", "leadership", "soft"),
    ("crisis management", "crisis management,crisis leadership,emergency response", "leadership", "soft"),
    ("influence without authority", "influence,lateral leadership,influence without authority", "leadership", "soft"),
    ("coaching skills", "coaching,executive coaching,technical coaching", "leadership", "soft"),
    ("onboarding", "onboarding,new hire,ramp up", "leadership", "soft"),
    ("culture building", "culture building,engineering culture,team values", "leadership", "soft"),
    ("goal setting", "goal setting,smart goals,objectives", "leadership", "soft"),
    ("time management leadership", "time management,prioritization,focus", "leadership", "soft"),
    ("remote team leadership", "remote leadership,distributed team,remote-first", "leadership", "soft"),
    ("technical debt management", "tech debt,technical debt management,debt reduction", "leadership", "soft"),
    ("scaling teams", "scaling teams,team growth,hiring plan", "leadership", "soft"),
]
NEW_SKILLS.extend(_leadership)

# --- B3. Problem Solving (25) ---
_problem_solving = [
    ("analytical thinking", "analytical thinking,analytical skills,analysis", "communication", "soft"),
    ("system design", "system design,systems thinking,architecture design", "communication", "soft"),
    ("debugging skills", "debugging,troubleshooting,root cause", "communication", "soft"),
    ("root cause analysis", "rca,root cause analysis,5 whys,fishbone", "communication", "soft"),
    ("innovation", "innovation,creative thinking,ideation", "communication", "soft"),
    ("critical thinking", "critical thinking,logical thinking,reasoning", "communication", "soft"),
    ("hypothesis driven development", "hypothesis driven,experimentation,a/b testing", "communication", "soft"),
    ("first principles thinking", "first principles,fundamental analysis", "communication", "soft"),
    ("design thinking", "design thinking,human-centered design,hcd", "communication", "soft"),
    ("complexity management", "complexity management,simplification", "communication", "soft"),
    ("trade-off analysis", "trade-off analysis,trade-offs,pros cons", "communication", "soft"),
    ("pattern recognition", "pattern recognition,identifying patterns", "communication", "soft"),
    ("abstraction", "abstraction,abstraction skills,generalization", "communication", "soft"),
    ("decomposition", "decomposition,breaking down problems,modularization", "communication", "soft"),
    ("estimation skills", "estimation,effort estimation,story points", "communication", "soft"),
    ("technical research", "technical research,technology evaluation,poc", "communication", "soft"),
    ("brainstorming", "brainstorming,ideation session,mind mapping", "communication", "soft"),
    ("reverse engineering", "reverse engineering,decompilation,protocol analysis", "communication", "soft"),
    ("performance analysis", "performance analysis,bottleneck identification,profiling", "communication", "soft"),
    ("architecture evaluation", "architecture evaluation,adr,technology assessment", "communication", "soft"),
    ("cost optimization", "cost optimization,cloud cost,finops", "communication", "soft"),
    ("scalability planning", "scalability,scale planning,capacity planning", "communication", "soft"),
    ("disaster recovery planning", "disaster recovery,dr planning,business continuity", "communication", "soft"),
    ("risk assessment", "risk assessment,risk analysis,risk mitigation", "communication", "soft"),
    ("continuous improvement", "continuous improvement,kaizen,retrospective", "communication", "soft"),
]
NEW_SKILLS.extend(_problem_solving)

# --- B4. Project Management (30) ---
_project_mgmt = [
    ("agile methodology", "agile,agile methodology,agile development", "project_mgmt", "soft"),
    ("scrum framework", "scrum,scrum framework,scrum master", "project_mgmt", "soft"),
    ("kanban", "kanban,kanban board,wip limits", "project_mgmt", "soft"),
    ("roadmap planning", "roadmap,roadmap planning,product roadmap", "project_mgmt", "soft"),
    ("risk management", "risk management,risk mitigation,risk register", "project_mgmt", "soft"),
    ("okr methodology", "okr,okrs,objectives key results", "project_mgmt", "soft"),
    ("sprint planning", "sprint planning,sprint,iteration planning", "project_mgmt", "soft"),
    ("backlog management", "backlog,backlog grooming,backlog refinement", "project_mgmt", "soft"),
    ("user story writing", "user stories,user story writing,acceptance criteria", "project_mgmt", "soft"),
    ("safe framework", "safe,scaled agile,safe framework", "project_mgmt", "soft"),
    ("lean methodology", "lean,lean methodology,waste reduction", "project_mgmt", "soft"),
    ("waterfall methodology", "waterfall,waterfall methodology,sequential", "project_mgmt", "soft"),
    ("release planning", "release planning,release train,pi planning", "project_mgmt", "soft"),
    ("resource allocation", "resource allocation,resource management", "project_mgmt", "soft"),
    ("project estimation", "project estimation,t-shirt sizing,planning poker", "project_mgmt", "soft"),
    ("status reporting", "status reporting,progress tracking,weekly updates", "project_mgmt", "soft"),
    ("dependency management", "dependency management,cross-team dependencies", "project_mgmt", "soft"),
    ("scope management", "scope management,scope creep,mvp definition", "project_mgmt", "soft"),
    ("quality assurance process", "qa process,quality assurance,quality gates", "project_mgmt", "soft"),
    ("technical debt tracking", "tech debt tracking,debt backlog,refactoring plan", "project_mgmt", "soft"),
    ("retrospectives", "retrospectives,retro,sprint retrospective", "project_mgmt", "soft"),
    ("daily standups", "standup,daily standup,daily scrum", "project_mgmt", "soft"),
    ("confluence", "confluence,wiki,knowledge base management", "project_mgmt", "soft"),
    ("jira management", "jira,jira management,atlassian jira", "project_mgmt", "soft"),
    ("trello", "trello,trello board", "project_mgmt", "soft"),
    ("asana", "asana,asana project", "project_mgmt", "soft"),
    ("notion", "notion,notion workspace", "project_mgmt", "soft"),
    ("monday.com", "monday,monday.com,monday board", "project_mgmt", "soft"),
    ("linear", "linear,linear app,linear issues", "project_mgmt", "soft"),
    ("github projects", "github projects,github issues,github board", "project_mgmt", "soft"),
]
NEW_SKILLS.extend(_project_mgmt)

# --- B5. Business Skills (25) ---
_business = [
    ("business analysis", "business analysis,ba,business analyst skills", "business", "soft"),
    ("requirements gathering", "requirements gathering,requirements elicitation,brd", "business", "soft"),
    ("product strategy", "product strategy,product management,product thinking", "business", "soft"),
    ("customer empathy", "customer empathy,user empathy,customer focus", "business", "soft"),
    ("market research", "market research,competitive analysis,market analysis", "business", "soft"),
    ("value proposition", "value proposition,value prop,business value", "business", "soft"),
    ("revenue modeling", "revenue modeling,business model,monetization", "business", "soft"),
    ("kpi definition", "kpi,kpi definition,metrics,success metrics", "business", "soft"),
    ("data driven decisions", "data driven,data-driven decisions,analytics driven", "business", "soft"),
    ("user experience focus", "ux focus,user experience,user-centric", "business", "soft"),
    ("go to market strategy", "gtm,go to market,launch strategy", "business", "soft"),
    ("technical sales", "technical sales,solutions engineering,pre-sales", "business", "soft"),
    ("roi analysis", "roi,roi analysis,return on investment", "business", "soft"),
    ("process improvement", "process improvement,process optimization,bpm", "business", "soft"),
    ("digital transformation", "digital transformation,digital strategy,modernization", "business", "soft"),
    ("startup mindset", "startup,entrepreneurship,lean startup", "business", "soft"),
    ("enterprise architecture", "enterprise architecture,togaf,ea", "business", "soft"),
    ("business intelligence", "business intelligence,bi,bi strategy", "business", "soft"),
    ("contract negotiation", "contract negotiation,sla,service agreement", "business", "soft"),
    ("compliance management", "compliance,regulatory compliance,compliance management", "business", "soft"),
    ("it governance", "it governance,itil,cobit", "business", "soft"),
    ("technology evaluation", "technology evaluation,tech assessment,build vs buy", "business", "soft"),
    ("privacy by design", "privacy by design,data privacy,privacy engineering", "business", "soft"),
    ("accessibility", "accessibility,a11y,wcag,ada compliance", "business", "soft"),
    ("sustainability tech", "sustainability,green tech,carbon footprint", "business", "soft"),
]
NEW_SKILLS.extend(_business)

# ──────────────────────────────────────────────────────────────────────
# C. CERTIFICATIONS  (~150)
# ──────────────────────────────────────────────────────────────────────

# --- C1. AWS Certifications (10) ---
_aws_certs = [
    ("aws solutions architect associate", "aws saa,solutions architect associate,aws saa-c03", "certification", "credential"),
    ("aws solutions architect professional", "aws sap,solutions architect professional,aws sap-c02", "certification", "credential"),
    ("aws developer associate", "aws dva,developer associate,aws dva-c02", "certification", "credential"),
    ("aws sysops administrator", "aws sysops,sysops administrator,aws soa-c02", "certification", "credential"),
    ("aws devops engineer professional", "aws devops pro,devops engineer professional", "certification", "credential"),
    ("aws data analytics specialty", "aws data analytics,das specialty", "certification", "credential"),
    ("aws machine learning specialty", "aws ml specialty,machine learning specialty", "certification", "credential"),
    ("aws security specialty", "aws security,security specialty,aws scs", "certification", "credential"),
    ("aws cloud practitioner", "aws cloud practitioner,clf,aws clf-c02", "certification", "credential"),
    ("aws database specialty", "aws database,database specialty,aws dbs", "certification", "credential"),
]
NEW_SKILLS.extend(_aws_certs)

# --- C2. Azure Certifications (8) ---
_azure_certs = [
    ("azure fundamentals az-900", "az-900,azure fundamentals", "certification", "credential"),
    ("azure administrator az-104", "az-104,azure administrator", "certification", "credential"),
    ("azure developer az-204", "az-204,azure developer", "certification", "credential"),
    ("azure solutions architect az-305", "az-305,azure solutions architect", "certification", "credential"),
    ("azure devops engineer az-400", "az-400,azure devops engineer", "certification", "credential"),
    ("azure data engineer dp-203", "dp-203,azure data engineer", "certification", "credential"),
    ("azure ai engineer ai-102", "ai-102,azure ai engineer", "certification", "credential"),
    ("azure security engineer az-500", "az-500,azure security engineer", "certification", "credential"),
]
NEW_SKILLS.extend(_azure_certs)

# --- C3. GCP Certifications (6) ---
_gcp_certs = [
    ("gcp cloud engineer", "gcp cloud engineer,associate cloud engineer", "certification", "credential"),
    ("gcp professional architect", "gcp architect,professional cloud architect", "certification", "credential"),
    ("gcp data engineer", "gcp data engineer,professional data engineer", "certification", "credential"),
    ("gcp ml engineer", "gcp ml engineer,professional machine learning engineer", "certification", "credential"),
    ("gcp devops engineer", "gcp devops,professional cloud devops engineer", "certification", "credential"),
    ("gcp security engineer", "gcp security,professional cloud security engineer", "certification", "credential"),
]
NEW_SKILLS.extend(_gcp_certs)

# --- C4. Multi-cloud Certifications (5) ---
_multicloud_certs = [
    ("hashicorp terraform associate", "terraform associate,hcta,terraform cert", "certification", "credential"),
    ("hashicorp vault associate", "vault associate,vault cert", "certification", "credential"),
    ("cka", "cka,certified kubernetes administrator", "certification", "credential"),
    ("ckad", "ckad,certified kubernetes application developer", "certification", "credential"),
    ("cks", "cks,certified kubernetes security specialist", "certification", "credential"),
]
NEW_SKILLS.extend(_multicloud_certs)

# --- C5. Security Certifications (15) ---
_security_certs = [
    ("cissp", "cissp,certified information systems security professional", "certification", "credential"),
    ("ceh", "ceh,certified ethical hacker", "certification", "credential"),
    ("oscp", "oscp,offensive security certified professional", "certification", "credential"),
    ("security+", "security+,comptia security+,sec+", "certification", "credential"),
    ("cisa", "cisa,certified information systems auditor", "certification", "credential"),
    ("cism", "cism,certified information security manager", "certification", "credential"),
    ("ccsp", "ccsp,certified cloud security professional", "certification", "credential"),
    ("gpen", "gpen,giac penetration tester", "certification", "credential"),
    ("gsec", "gsec,giac security essentials", "certification", "credential"),
    ("sscp", "sscp,systems security certified practitioner", "certification", "credential"),
    ("cysa+", "cysa+,comptia cysa,cybersecurity analyst", "certification", "credential"),
    ("pentest+", "pentest+,comptia pentest", "certification", "credential"),
    ("casp+", "casp+,comptia advanced security practitioner", "certification", "credential"),
    ("crtp", "crtp,certified red team professional", "certification", "credential"),
    ("oswe", "oswe,offensive security web expert", "certification", "credential"),
]
NEW_SKILLS.extend(_security_certs)

# --- C6. Data & AI Certifications (15) ---
_data_ai_certs = [
    ("tensorflow developer certificate", "tensorflow developer,tensorflow cert", "certification", "credential"),
    ("databricks certified data engineer", "databricks data engineer,databricks cert", "certification", "credential"),
    ("databricks certified ml professional", "databricks ml,databricks ml professional", "certification", "credential"),
    ("snowflake snowpro core", "snowpro core,snowflake cert", "certification", "credential"),
    ("dbt analytics engineering", "dbt certification,dbt analytics", "certification", "credential"),
    ("apache spark certification", "spark certification,databricks spark", "certification", "credential"),
    ("cloudera data analyst", "cloudera analyst,cdp cert", "certification", "credential"),
    ("microsoft data scientist dp-100", "dp-100,azure data scientist", "certification", "credential"),
    ("microsoft power bi da-100", "da-100,pl-300,power bi certification", "certification", "credential"),
    ("sas certified specialist", "sas certified,sas specialist", "certification", "credential"),
    ("ibm data science professional", "ibm data science,ibm ds cert", "certification", "credential"),
    ("google data analytics certificate", "google data analytics,google analytics cert", "certification", "credential"),
    ("aws data engineer associate", "aws data engineer,dea-c01", "certification", "credential"),
    ("nvidia deep learning institute", "nvidia dli,nvidia deep learning", "certification", "credential"),
    ("tableau desktop specialist", "tableau certification,tableau specialist", "certification", "credential"),
]
NEW_SKILLS.extend(_data_ai_certs)

# --- C7. Project Management Certifications (12) ---
_pm_certs = [
    ("pmp certification", "pmp,project management professional,pmi pmp", "certification", "credential"),
    ("csm", "csm,certified scrum master", "certification", "credential"),
    ("psm", "psm,professional scrum master", "certification", "credential"),
    ("safe agilist", "safe agilist,sa,leading safe", "certification", "credential"),
    ("prince2", "prince2,prince2 practitioner", "certification", "credential"),
    ("pmi-acp", "pmi-acp,agile certified practitioner", "certification", "credential"),
    ("cspo", "cspo,certified scrum product owner", "certification", "credential"),
    ("itil foundation", "itil,itil foundation,itil v4", "certification", "credential"),
    ("six sigma green belt", "six sigma,green belt,lean six sigma gb", "certification", "credential"),
    ("six sigma black belt", "six sigma black belt,black belt,lean six sigma bb", "certification", "credential"),
    ("togaf certification", "togaf,togaf 9,enterprise architecture cert", "certification", "credential"),
    ("lean it foundation", "lean it,lean foundation", "certification", "credential"),
]
NEW_SKILLS.extend(_pm_certs)

# --- C8. Development Certifications (20) ---
_dev_certs = [
    ("oracle certified professional java", "ocp java,oracle java cert,java certification", "certification", "credential"),
    ("oracle certified associate java", "oca java,oracle java associate", "certification", "credential"),
    ("microsoft certified azure developer", "microsoft azure developer,mcad", "certification", "credential"),
    ("microsoft certified devops expert", "microsoft devops expert", "certification", "credential"),
    ("red hat certified engineer", "rhce,red hat certified,rhcsa", "certification", "credential"),
    ("red hat openshift administrator", "openshift admin,ex280", "certification", "credential"),
    ("linux foundation certified sysadmin", "lfcs,linux sysadmin cert", "certification", "credential"),
    ("linux foundation certified engineer", "lfce,linux engineer cert", "certification", "credential"),
    ("lpic-1", "lpic-1,lpic 1,linux professional institute", "certification", "credential"),
    ("docker certified associate", "dca,docker certified", "certification", "credential"),
    ("mongodb developer certification", "mongodb cert,mongodb developer", "certification", "credential"),
    ("neo4j certified professional", "neo4j cert,graph db certification", "certification", "credential"),
    ("confluent kafka certification", "kafka certification,confluent cert", "certification", "credential"),
    ("github actions certification", "github cert,github actions cert", "certification", "credential"),
    ("istio certified associate", "istio cert,ica", "certification", "credential"),
    ("puppet certified professional", "puppet cert,puppet professional", "certification", "credential"),
    ("ansible automation engineer", "ansible cert,red hat ansible", "certification", "credential"),
    ("microsoft 365 developer", "ms-600,microsoft 365 developer", "certification", "credential"),
    ("spring professional certification", "spring cert,pivotal spring", "certification", "credential"),
    ("graphql certification", "graphql cert,apollo cert", "certification", "credential"),
]
NEW_SKILLS.extend(_dev_certs)

# --- C9. Specialized Certifications (30) ---
_specialized_certs = [
    ("salesforce administrator", "salesforce admin,sf admin", "certification", "credential"),
    ("salesforce developer", "salesforce developer,sf developer,platform developer", "certification", "credential"),
    ("salesforce architect", "salesforce architect,sf architect", "certification", "credential"),
    ("salesforce consultant", "salesforce consultant,sf consultant", "certification", "credential"),
    ("sap certified associate", "sap associate,sap certification", "certification", "credential"),
    ("sap s/4hana", "sap s/4hana,sap hana cert", "certification", "credential"),
    ("sap fiori", "sap fiori,sap ui5", "certification", "credential"),
    ("servicenow certified system admin", "servicenow admin,servicenow csa", "certification", "credential"),
    ("servicenow certified app developer", "servicenow developer,servicenow cad", "certification", "credential"),
    ("servicenow certified implementation specialist", "servicenow cis,servicenow implementation", "certification", "credential"),
    ("cisco ccna", "ccna certification,cisco ccna cert", "certification", "credential"),
    ("cisco ccnp enterprise", "ccnp enterprise,cisco ccnp", "certification", "credential"),
    ("cisco ccie", "ccie,cisco ccie,ccie certification", "certification", "credential"),
    ("cisco devnet associate", "devnet associate,cisco devnet", "certification", "credential"),
    ("comptia a+", "comptia a+,a+ certification", "certification", "credential"),
    ("comptia network+", "network+,comptia network,net+", "certification", "credential"),
    ("comptia linux+", "linux+,comptia linux", "certification", "credential"),
    ("comptia cloud+", "cloud+,comptia cloud", "certification", "credential"),
    ("comptia data+", "data+,comptia data", "certification", "credential"),
    ("scrum@scale", "scrum at scale,scrum@scale practitioner", "certification", "credential"),
    ("aws networking specialty", "aws networking,advanced networking specialty", "certification", "credential"),
    ("unity certified developer", "unity cert,unity certified", "certification", "credential"),
    ("unreal authorized instructor", "unreal cert,unreal instructor", "certification", "credential"),
    ("vmware certified professional", "vcp,vmware certified,vsphere cert", "certification", "credential"),
    ("fortinet nse", "fortinet,nse certification,fortinet nse", "certification", "credential"),
    ("palo alto pcnsa", "pcnsa,palo alto cert,palo alto pcnsa", "certification", "credential"),
    ("splunk certified power user", "splunk cert,splunk power user", "certification", "credential"),
    ("elastic certified engineer", "elastic cert,elasticsearch cert", "certification", "credential"),
    ("okta certified professional", "okta cert,okta professional", "certification", "credential"),
    ("figma certification", "figma cert,figma certified", "certification", "credential"),
]
NEW_SKILLS.extend(_specialized_certs)


# ======================================================================
#   MAIN
# ======================================================================

def main() -> None:
    print("=" * 70)
    print("  CAREER-ML  ·  Skills Dataset Expansion")
    print("=" * 70)

    # ── 1. Load existing ─────────────────────────────────────────────
    if not INPUT_CSV.exists():
        sys.exit(f"ERROR: Cannot find {INPUT_CSV}")

    existing = pd.read_csv(INPUT_CSV)
    print(f"\n[1] Loaded existing skills: {len(existing)}")
    print(f"    Columns: {list(existing.columns)}")

    original_count = len(existing)

    # ── 2. Build new rows ────────────────────────────────────────────
    next_id = original_count + 1
    rows = []
    for name, aliases, category, skill_type in NEW_SKILLS:
        rows.append({
            "skill_id": _id(next_id),
            "name":     name,
            "aliases":  aliases,
            "category": category,
            "type":     skill_type,
        })
        next_id += 1

    new_df = pd.DataFrame(rows)
    print(f"[2] Prepared {len(new_df)} new skills  (SK{original_count+1:03d} – SK{next_id-1:04d})")

    # ── 3. Merge ─────────────────────────────────────────────────────
    combined = pd.concat([existing, new_df], ignore_index=True)
    print(f"[3] Combined total: {len(combined)}")

    # ── 4. Validation ────────────────────────────────────────────────
    errors = []

    # 4a. Duplicate skill_ids
    dup_ids = combined[combined.duplicated(subset=["skill_id"], keep=False)]
    if not dup_ids.empty:
        errors.append(f"Duplicate skill_ids found: {dup_ids['skill_id'].unique().tolist()}")

    # 4b. Duplicate names (case-insensitive)
    combined["_name_lower"] = combined["name"].str.lower().str.strip()
    dup_names = combined[combined.duplicated(subset=["_name_lower"], keep=False)]
    if not dup_names.empty:
        dup_list = dup_names["name"].unique().tolist()
        # Remove exact duplicates with existing, keeping existing ones
        print(f"    ⚠ Found {len(dup_list)} duplicate name(s) – removing new duplicates:")
        for dn in dup_list:
            print(f"       · {dn}")
        # Keep the FIRST occurrence (which is the existing one)
        combined = combined.drop_duplicates(subset=["_name_lower"], keep="first")
        # Re-number IDs from SK301 onward for the new skills
        # (the existing block stays as-is)
        existing_part = combined.iloc[:original_count].copy()
        new_part = combined.iloc[original_count:].copy()
        new_part = new_part.reset_index(drop=True)
        for i, idx in enumerate(new_part.index):
            new_part.at[idx, "skill_id"] = _id(original_count + 1 + i)
        combined = pd.concat([existing_part, new_part], ignore_index=True)

    combined = combined.drop(columns=["_name_lower"], errors="ignore")

    # 4c. Null check
    nulls = combined.isnull().sum()
    null_cols = nulls[nulls > 0]
    if not null_cols.empty:
        errors.append(f"Null values: {null_cols.to_dict()}")

    if errors:
        for e in errors:
            print(f"    ✗ {e}")
    else:
        print("    ✓ No validation issues")

    # ── 5. Save ──────────────────────────────────────────────────────
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    combined.to_csv(OUTPUT_CSV, index=False)
    print(f"\n[4] Saved → {OUTPUT_CSV}")
    print(f"    Total skills: {len(combined)}")

    # ── 6. Statistics ────────────────────────────────────────────────
    print("\n" + "=" * 70)
    print("  STATISTICS")
    print("=" * 70)

    print(f"\n  Skills before : {original_count}")
    print(f"  Skills added  : {len(combined) - original_count}")
    print(f"  Skills after  : {len(combined)}")

    print("\n  ── Breakdown by CATEGORY ──")
    cat_counts = combined["category"].value_counts().sort_values(ascending=False)
    for cat, cnt in cat_counts.items():
        print(f"    {cat:<25s} {cnt:>5d}")

    print("\n  ── Breakdown by TYPE ──")
    type_counts = combined["type"].value_counts().sort_values(ascending=False)
    for t, cnt in type_counts.items():
        print(f"    {t:<25s} {cnt:>5d}")

    # ── 7. Sample new skills ─────────────────────────────────────────
    new_section = combined.iloc[original_count:]
    sample = new_section.sample(n=min(20, len(new_section)), random_state=42)
    print("\n  ── Sample of 20 NEW skills ──")
    print(sample.to_string(index=False))

    print("\n" + "=" * 70)
    print("  DONE – skills_v2.csv written successfully")
    print("=" * 70)


if __name__ == "__main__":
    main()
