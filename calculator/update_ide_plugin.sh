# Update IDE integration to include the new combined command
sed -i '/\aiCodingAssistant.fixBugs\/a {"command": "aiCodingAssistant.integrateFeatures", "title": "Integrate Advanced Features"}' package.json
