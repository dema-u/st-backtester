az container delete --resource-group fxcm-trader --name trader
az container create --resource-group fxcm-trader --name trader --file ../container.yaml
pause