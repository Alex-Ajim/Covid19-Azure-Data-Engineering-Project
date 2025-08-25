# Databricks notebook source
# MAGIC %md
# MAGIC ## Mount the following data lake storage gen2 containers
# MAGIC 1. raw
# MAGIC 2. processed
# MAGIC 3. lookup

# COMMAND ----------

# MAGIC %md
# MAGIC ### Set-up the configs
# MAGIC #### Please update the following 
# MAGIC - application-id
# MAGIC - service-credential
# MAGIC - directory-id

# COMMAND ----------

configs = {"fs.azure.account.auth.type": "OAuth",
           "fs.azure.account.oauth.provider.type": "org.apache.hadoop.fs.azurebfs.oauth2.ClientCredsTokenProvider",
           "fs.azure.account.oauth2.client.id": "92dfb966-0688-4c6c-9371-f6df6b00a83b",
           "fs.azure.account.oauth2.client.secret": "byM8Q~W2U6ZeRwMlUkoNr-a1JfRS4mhjRukRccS6",
           "fs.azure.account.oauth2.client.endpoint": "https://login.microsoftonline.com/6ea22ecb-00f9-4219-b416-a72eb7df5306/oauth2/token"}

# COMMAND ----------

# MAGIC %md
# MAGIC ### Mount the raw container
# MAGIC #### Update the storage account name before executing

# COMMAND ----------

dbutils.fs.mount(
  source = "abfss://raw@covid19storagedatalake.dfs.core.windows.net/",
  mount_point = "/mnt/covid19storagedatalake/raw",
  extra_configs = configs)

# COMMAND ----------

# MAGIC %md
# MAGIC ### Mount the processed container
# MAGIC #### Update the storage account name before executing

# COMMAND ----------

dbutils.fs.mount(
  source = "abfss://processed@covid19storagedatalake.dfs.core.windows.net/",
  mount_point = "/mnt/covid19storagedatalake/processed",
  extra_configs = configs)

# COMMAND ----------

# MAGIC %md
# MAGIC ### Mount the lookup container
# MAGIC #### Update the storage account name before executing

# COMMAND ----------

dbutils.fs.mount(
  source = "abfss://lookup@covid19storagedatalake.dfs.core.windows.net/",
  mount_point = "/mnt/covid19storagedatalake/lookup",
  extra_configs = configs)

# COMMAND ----------

dbutils.fs.ls("/mnt/covid19storagedatalake/processed")