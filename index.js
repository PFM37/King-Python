const fs = require('fs');
const readline = require('readline-sync');
const { program } = require('commander');

function print(string) {
    console.log(string);
}

function error(err) {
    console.error("Error:", err);
}

function input(question) {
    return readline.question(question);
}

class KpJS {
    static transpile(code) {
        let jsCode = `import * as kp from 'C:/KP/index.js';\n\n`;
    
        // Process the King Python code
        jsCode += code
            // Variables
            .replace(/(\w+)\s*=\s*(.+);/g, 'let $1 = $2;')
            
            // Functions
            .replace(/fun (\w+)\((.*?)\):/g, 'function $1($2) {')
            
            // Control flow
            .replace(/if\((.*?)\):/g, 'if ($1) {')
            .replace(/else:/g, '} else {')
            .replace(/while\((.*?)\):/g, 'while ($1) {')
            
            // Special King Python syntax
            .replace(/say\s+(.*?);/g, 'print($1);')
            .replace(/ask\s+(.*?);/g, 'input($1);')
            
            // Blocks
            .replace(/:$/gm, '{')
            // Add closing braces
            .replace(/(\n\s*)(?=function|if|else|while)/g, '$1}\n$1');
            return jsCode;
    }

    static async runFile(filePath) {
        try {
            const code = fs.readFileSync(filePath, 'utf8');
            const jsCode = this.transpile(code);
            
            // Create a safe execution context
            const context = {
                KpJS: this,
                console,
                require,
                process,
                module: { exports: {} }
            };

            // Execute in isolated context
            const vm = require('vm');
            const script = new vm.Script(jsCode);
            script.runInNewContext(context);
            
            return context.module.exports;
        } catch (err) {
            this.error(err);
            throw err;
        }
    }
}

// CLI Setup
program
    .command("run <file>")
    .description("Run a King Python file")
    .action((file) => {
        if (!file.endsWith('.kp')) {
            KpJS.error("File must have .kp extension");
            process.exit(1);
        }
        KpJS.runFile(file).catch(() => process.exit(1));
    });

program.parse(process.argv);

module.exports = KpJS;