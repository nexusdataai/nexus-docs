
Different Types of Data --

# AI-OPs Data

## What it consist

All simulators + Simulated Data + AI Diagnostic Data + AI Health Central Data

## How it works

Simulated data is stored in S3 , served through redis database, Redis database initailize the simulator data while bootstraping.

AI diagnostics are all automated workflows defined in AI engine.

AI Health Data are also all automated workflows defined in AI engine.

## Where it is persisted  

Simulators metadata lies in DynamoDB + Simulator Generated Data lies in S3 
AI diagnostics data lies in DynamoDB.
AI -Health Data lies in DynamoDB.

## How its backed Up

As a TAR of metedata(In Dynamo) + Generated data (in s3)

# Data Plane Data

## What it consist

Data Plane Definition Metadata + Data Sources Definition Metdata + Virtual-data + Virtual Data API Registry +  Mapping-Rules

## How it works

Data Plane connects with multiple data sources.The FDW Runtime that implements data plane can connect with Simulator, Direct ERP Databases, Athena Databases (ETL Mapping), FileToDb(), SocialToDB(),TimeSeries Historical DB().Data-Plane comprises of connections with different Data-sources Type (Simulator / ERP Databases/ ETL DB's,FileToDb(),SocialToDB(),TimeSeries Historical DB())

The supported data sources are Simulator / ERP Databases / ETL DB's,FileToDb(),SocialToDB(),TimeSeries Historical DB().

Each Data Sources work through Processors that connect to external systems, fetch data, and pass it through a directed flow. 

Source --> Process --> Transform --> Route --> Destination

Its like Oracle DB
      \
Kafka ---> Nexus ---> Validation ---> Enrichment ---> S3
      /
 REST API
 
The Virtual-data is a standardized common data layer that define the standard data of any domain , say supply chain.

Virtual Data API registry is a set of API's that can act on virtual Data,finally those VDL Api's in turn use the Connector API's-

Connector API's can call directly the SQL Update Query via FDW Runtime or Use third Party Rest API's. We need to maintain Connector API's Registry.

The Mapping Rules defines the mapping between data sources and Virtual Data , it a last layer of transformation between data sources and VDL.

## Where is persisted  

The entire Data-Plane and Data Sources Data persist in Dynamo Database.
Virtual-data and Virtual Data API registry persist in Dynamo Database.
Connectors + Connector-Settings + Connector API Registry + Connector Diagnostics 
- All persists in Dynamo Database.
Mapping Rules and Daignostics are stored in dynamodb.

## How its backed Up

As a TAR of all the data-plane components(from Dynamo)

# Control Plane Data

## What it Consist

Knowledge Pipeline + Knowledge Index + Knowledge Graph + Policy Editor + Workflow Editor + Integration Rules Editor + React-tools + Re-Act Tools-registry

## How it works

Knowledge Pipeline is the workflow to create the hybrid second brain for AI, it creates the vector data of knowledge index along with the knowledge graph of graph data that LLM use for its reasoning engine.  

Knowledge Index is the vector database of schemas , policies, workflows and integration that LLM uses for reasoning stage to find the Top-k matches. 

Knowledge graph is the Graph database of the entities , policies, workflows and integration rules.

Policy Editor defines the configurable policies for AI governance.

Workflow Editor defines the configurable workflows for AI governance.

Integration Rule Editor defines the configurable integration rules for AI governance.

## Where is persisted  
Knowledge Pipeline metdata are stored in dynamodb.
Knowledge index lies with PGVector
Knowledge Graph lies with Apache Age.

Workflows + Polocies + Integration Rules 
- All persists in Dynamo Database.

## How its backed Up

We need to take the backup of Knowledge Pipeline and Workflows + Polocies + Integration Rules + ReAct Registries + React Tools Metadata from dynamo db as a complete control-plane tar , we dont need to take backup of the Knowledge index and Knowledge Graph as they will be generated via Knowledge Pipeline execution.

# Reasoning Plane Data

## What it Consist
AI Co-Pilot , Planning Playground , ReAct Tools , Tools Registry , Tool Builder

## How it works

AI Co-pilot and Planning Playground are purely reasoning and planning utilities.

Each Re-Act Tools = Execute (VDL Query + VDL API's)  
VDL Api's in turn use the Connector API's,Connector API's can call directly the SQL Update Query via FDW Runtime or Use third Party Rest API's. We need to maintain Connector API's Registry and that is maintained in data-plane.

We will maintain VDL Api's registry , Connectors API's registries in dynamodb.
Also We will maintain ReactTool definitions(python code) inside ReAct Tool registry,in dynamodb.

## Where is persisted  
AI Co-Pilot , Planning Playground, Tool Buildier is pure transient program , no data is persisted.
React Tools and Tools Registries data lies in dynamodb.
 
## How its backed Up

React Tools and Tools Registries data are backed as tar from dynamodb.


# Workspace Data 

## What it Consist
AI Automations + AI Analytics and Dashboards + AI solutions + Role Based Access Control  

## How it works  

AI Automations runs Re-Act Tools in series or DAG workflow.We will mainatin a automation workflows registries in dynnamodb.

AI Analytics are a set of dashboard that performs the VDL query and does some transformation and tie up the result data with some views.

AI solutions are composed of AI Automation and AI-Analytics and NLP Query interface. Each AI solutions wil have a structured YAML definitions with lot of descriptions of the solutions, so that we can index them in vector db so that when customer will look for AI solution via NLP query , he will get a readymade solution and he can improve the solution incrementally.   

## Where is persisted  

All persist in Dynamo Database

## How its backed Up

Everything are backed as tar from dynamodb.
