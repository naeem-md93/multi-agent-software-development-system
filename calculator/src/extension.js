const vscode = require('vscode'); const { exec } = require('child_process'); function activate(context) { let generateCodeCommand = vscode.commands.registerCommand('aiCodingAssistant.generateCode', function () { vscode.window.showInputBox({ prompt: 'Enter your prompt to generate code' }).then(prompt => { if (prompt) { exec(An error occurred: 

You tried to access openai.ChatCompletion, but this is no longer supported in openai>=1.0.0 - see the README at https://github.com/openai/openai-python for the API.

You can run `openai migrate` to automatically upgrade your codebase to use the 1.0.0 interface. 

Alternatively, you can pin your installation to the old version, e.g. `pip install openai==0.28`

A detailed migration guide is available here: https://github.com/openai/openai-python/discussions/742, (error, stdout, stderr) => { if (error) { vscode.window.showErrorMessage(); } else { vscode.window.showInformationMessage(stdout); } }); } }); }); let fixBugsCommand = vscode.commands.registerCommand('aiCodingAssistant.fixBugs', function () { vscode.window.showOpenDialog({ canSelectMany: false, filters: { 'Code Files': ['py', 'js', 'txt'] } }).then(fileUri => { if (fileUri && fileUri[0]) { exec(, (error, stdout, stderr) => { if (error) { vscode.window.showErrorMessage(); } else { vscode.window.showInformationMessage(stdout); } }); } }); }); context.subscriptions.push(generateCodeCommand, fixBugsCommand); } exports.activate = activate; function deactivate() {} exports.deactivate = deactivate;
