# Covid19 Azure Data Engineering Project
## Introduction
This project demonstrates the implementation of a real-world data engineering solution for analyzing and reporting on COVID-19 data trends. It leverages modern cloud-based technologies to build an end-to-end data pipeline capable of ingesting, transforming, storing, and visualizing data at scale.

The solution integrates Azure Data Factory, Azure Data Lake, Azure SQL Database, Databricks, and HDInsight, with monitoring and orchestration powered by CI/CD practices. The pipeline ingests raw COVID-19 datasets, applies data transformations, and makes the processed data available for advanced analytics and visualization through Power BI and other reporting tools.

The project highlights best practices in data engineering, including:  
- Building scalable and reusable data pipelines  
- Orchestrating transformations across multiple services  
- Implementing monitoring, logging, and error handling  
- Supporting downstream analytics and reporting for decision-making

The pipeline provides a reliable framework for handling large-scale COVID-19 datasets and can be extended for other real-world data analytics and reporting use cases.

## Architecture

![Project Architecture](https://github.com/Alex-Ajim/Covid19-Azure-Data-Engineering-Project/blob/main/Data%20Architecture.png)

## Technology Used  

1. **Programming Language** – Python  
2. **Scripting Language** – SQL  
3. **Microsoft Azure Services**  
   - Azure Data Factory (ETL orchestration)  
   - Azure Data Lake Storage (data lake for raw and curated data)  
   - Azure SQL Database (relational data storage)  
   - Azure Databricks (data transformation & analytics)  
   - Azure HDInsight (big data processing)  
   - Power BI (data visualization & reporting)  
4. **CI/CD & Monitoring**  
   - Azure DevOps (CI/CD pipelines)  
   - Azure Monitor & Log Analytics (pipeline monitoring and diagnostics)  

## Dataset Used  

This project makes use of publicly available COVID-19 datasets from trusted sources, primarily **ECDC (European Centre for Disease Prevention and Control)** and **Eurostat**. These datasets provide information on COVID-19 cases, deaths, testing, hospital admissions, government responses, and population demographics across different countries.  

### Data Sources  
1. **ECDC (European Centre for Disease Prevention and Control)**  
   - COVID-19 cases and deaths (`cases_deaths.csv`)  
   - Country-specific responses (`country_response.csv`)  
   - Hospital admissions (`hospital_admissions.csv`)  
   - Testing statistics (`testing.csv`)  
   - UK-specific data (`case_deaths_uk_ind_only.csv`)  
   - [Official Source](https://www.ecdc.europa.eu/en/covid-19/data)  

2. **Eurostat**  
   - Population by age data (`population_by_age.tsv.gz`)  
   - [Official Source](https://ec.europa.eu/eurostat/web/population/data/database)  

3. **Lookup Tables**  
   - Country reference data (`country_lookup.csv`)  
   - Date dimension for time-series analysis (`dim_date.csv`)  

These datasets form the foundation of the data pipelines built in this project, enabling transformations, aggregations, and insights on COVID-19 trends across different regions and demographics.  

## Extract Data  

The **Extract Data stage** focuses on ingesting COVID-19 datasets from multiple sources into the Azure Data Lake for downstream processing and analysis. Two main pipelines were developed: one for population data and another for ECDC datasets.  

### 1. Copy ECDC Data Pipeline  
This pipeline ingests COVID-19 datasets originally hosted on the **ECDC website** (now mirrored on GitHub) into the data lake. A key feature of this pipeline is **scalability** — if the number of data sources increases (e.g., from 4 to 50), we only need to update the list of sources in a JSON configuration file.  

**Key Design Points:**  
- **Parameterization** was applied at multiple levels:  
  - Base URL (linked service)  
  - Relative URL (source dataset)  
  - File name (sink dataset)  
- **Lookup activity** retrieves the list of datasets to be ingested.  
- **ForEach activity** iterates over the dataset list, passing parameters into the **Copy activity**.  
- Each iteration performs a copy operation using the current dataset’s parameters (base URL, relative URL, file name).  
- The pipeline is scheduled using a **Tumbling Window Trigger** that executes every 24 hours.  

**Security:** Access to the data lake is secured using the **Azure Storage Account Key**.  

### 2. Copy Population Data Pipeline  
This pipeline ingests **population data** (`population_by_age.tsv.gz`) from Blob Storage into the data lake, storing it as `population_by_age.tsv`.  

**Pipeline Logic:**  
1. **Validation activity** checks if the file exists in Blob Storage.  
2. **Get Metadata activity** retrieves file properties, including `columnCount`.  
3. **If Condition activity** validates whether the column count equals the expected value (16).  
   - If **True** → Copy activity executes and source file is deleted.  
   - If **False** → Pipeline fails gracefully.  

**Security:** Data Factory requires authenticated access to both Blob Storage and Data Lake, configured using the **Storage Account Key**.  

**Trigger:**  
- The pipeline runs automatically whenever a new file arrives in Blob Storage (**Event Trigger**).  
- Upon successful ingestion, the **Process Population Pipeline** is executed.  

### 3. Parent Pipeline Execution  
A **parent pipeline** was created to orchestrate execution. It ensures that once the ingestion pipeline completes, the **processing pipeline** is triggered, providing a seamless end-to-end flow.  

## Transform Data  

The **Transform Data stage** focuses on cleaning, shaping, and enriching the ingested datasets to prepare them for analytics and reporting. A combination of **Azure Data Factory Dataflows**, **Azure HDInsight**, and **Azure Databricks** were used, depending on the dataset and transformation requirements.  

### 1. Dataflows (ADF)  
Two separate pipelines were implemented using **Mapping Dataflows** to preprocess the *Cases and Deaths* dataset and the *Hospital Admissions* dataset.  

- **Process Cases and Deaths Data**  
  - **Source:** Raw `cases_and_deaths` dataset (from the Extract stage).  
  - **Transformations:** Data cleaning, schema alignment, and filtering.  
  - **Sink:** `processed_cases_and_deaths` dataset in the Data Lake.  

- **Process Hospital Admissions Data**  
  - **Source:** Raw `hospital_admissions` dataset (from the Extract stage).  
  - **Transformations:** Column selection, null handling, and data standardization.  
  - **Sink:** `processed_hospital_admissions` dataset in the Data Lake.  

These pipelines were orchestrated via **ADF pipeline activities**, making the transformations scalable and easy to maintain.  

### 2. HDInsight (ECDC Data Preprocessing)  
For more computationally intensive preprocessing, **Azure HDInsight** was used to handle larger ECDC datasets. This ensured that distributed processing could be applied efficiently to prepare the datasets for downstream analysis.  

### 3. Databricks (Population Data)  
Population data preprocessing was handled using **Azure Databricks**, allowing for flexible data transformations in a notebook environment.  

**Key Configurations:**  
- **Linked Service Integration:** The Databricks notebook was invoked through Azure Data Factory, with an access token generated from Databricks to authenticate the linked service.  
- **Service Principal Authentication:**  
  - A service principal was created and assigned the **Blob Storage Contributor** role.  
  - The service principal credentials were stored in Azure Key Vault and securely referenced by the Databricks notebook.  
  - This enabled the notebook to read and write data from the Data Lake securely.
  - ![Configuration illustration](https://github.com/Alex-Ajim/Covid19-Azure-Data-Engineering-Project/blob/main/2.%20Transform%20Data/Process%20population%20pipeline.png)


**Triggering Logic:**  
- Once the **Ingest Pipeline** executes successfully, the **Process Population Pipeline** is automatically triggered.  
- A **parent pipeline** was designed to orchestrate both ingestion and transformation steps, ensuring end-to-end automation.

## Load Data  

The **Load Data stage** focuses on moving the processed datasets from the Azure Data Lake into a **SQL Database**, making the data ready for analytics, reporting, and BI tools.  

### Pipeline Design  
- A **Linked Service** was created to connect Azure Data Factory to the Data Lake, where the processed datasets are stored.  
- Another **Linked Service** was configured for the SQL Database, authenticated using the SQL server username and password.  
- **Copy Activity** was used to transfer data:  
  - **Source Dataset:** Configured from the Data Lake (processed datasets).  
  - **Sink Dataset:** Configured to the SQL Database via its Linked Service.
- ![Configuration illustration](https://github.com/Alex-Ajim/Covid19-Azure-Data-Engineering-Project/blob/main/3.%20Load%20Data/Load%20to%20SQL%20database.png)

This design ensures secure and reliable movement of transformed data from the Data Lake into the SQL Database.  

### Datasets Loaded into SQL Database  
- **Hospital Admissions Data** (from Dataflow transformation)  
- **Cases and Deaths Data** (from Dataflow transformation)  
- **Testing Data** (from HDInsight transformation)  

> Note: The **Population Data** was not loaded into the SQL database, as it was used primarily for demonstration purposes.  

### Security  
- Data Lake access was secured via **Storage Account Key**.  
- SQL Database access was configured through **username/password authentication** within the Linked Service.  

