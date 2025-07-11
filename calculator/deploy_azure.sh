#!/bin/bash
az group create --name ai-assistant-group --location eastus
az appservice plan create --name ai-assistant-plan --resource-group ai-assistant-group --sku B1 --is-linux
az webapp create --resource-group ai-assistant-group --plan ai-assistant-plan --name ai-assistant-deploy --runtime 'PYTHON|3.9'
az webapp deploy --resource-group ai-assistant-group --name ai-assistant-deploy --src-path .
