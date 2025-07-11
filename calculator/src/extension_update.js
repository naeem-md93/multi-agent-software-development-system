const vscode = require('vscode');
const { exec } = require('child_process');
function activate(context) {
  let integrateFeaturesCommand = vscode.commands.registerCommand('aiCodingAssistant.integrateFeatures', function () {
    exec('python3 advanced_features.py', (error, stdout, stderr) => {
      if (error) {
        vscode.window.showErrorMessage();
      } else {
        vscode.window.showInformationMessage(stdout);
      }
    });
  });
  context.subscriptions.push(integrateFeaturesCommand);
}
exports.activate = activate;
